from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import numpy as np
from astar_path_planning.app.models.grid_map import GridMap, TerrainMap
from astar_path_planning.app.routers.grid import get_current_map

# 修复matplotlib在没有GUI的情况下的问题
matplotlib.use('Agg')

router = APIRouter(prefix="/visualization", tags=["可视化"])

class VisualizationRequest(BaseModel):
    path: Optional[List[Dict[str, int]]] = None
    explored: Optional[List[Dict[str, int]]] = None
    show_grid: bool = True
    show_explored: bool = True
    show_path: bool = True
    format: str = "png"  # png, svg

@router.post("/render")
async def render_visualization(request: VisualizationRequest, grid_map: GridMap = Depends(get_current_map)):
    """
    生成地图和路径可视化
    """
    # 设置图像大小和分辨率
    dpi = 100
    figsize = (grid_map.width / dpi * 3, grid_map.height / dpi * 3)
    
    # 创建图像
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # 绘制地图网格
    if request.show_grid:
        # 准备地图数据
        grid_data = np.zeros((grid_map.height, grid_map.width, 3))
        
        # 设置地图颜色：白色-可通行，黑色-障碍物
        for y in range(grid_map.height):
            for x in range(grid_map.width):
                if grid_map.is_obstacle(x, y):
                    grid_data[y, x] = [0, 0, 0]  # 黑色-障碍物
                else:
                    # 如果是地形地图，使用不同颜色表示不同地形
                    if isinstance(grid_map, TerrainMap):
                        terrain_type = grid_map.terrain_type[y, x]
                        if terrain_type == 0:
                            grid_data[y, x] = [1, 1, 1]  # 白色-平地
                        elif terrain_type == 1:
                            grid_data[y, x] = [0.6, 0.3, 0.1]  # 棕色-山地
                        elif terrain_type == 2:
                            grid_data[y, x] = [0.2, 0.5, 0.8]  # 蓝色-水域
                        else:
                            grid_data[y, x] = [0.8, 0.8, 0.6]  # 其他地形
                    else:
                        grid_data[y, x] = [1, 1, 1]  # 白色-可通行
        
        # 绘制地图
        ax.imshow(grid_data, origin='upper')
    
    # 绘制探索节点
    if request.show_explored and request.explored:
        explored_x = [point["x"] for point in request.explored]
        explored_y = [point["y"] for point in request.explored]
        ax.scatter(explored_x, explored_y, color='lightblue', marker='o', alpha=0.5, s=10)
    
    # 绘制路径
    if request.show_path and request.path:
        path_x = [point["x"] for point in request.path]
        path_y = [point["y"] for point in request.path]
        ax.plot(path_x, path_y, color='red', linewidth=2)
        
        # 起点和终点标记
        if path_x and path_y:
            ax.scatter(path_x[0], path_y[0], color='green', marker='o', s=100)
            ax.scatter(path_x[-1], path_y[-1], color='blue', marker='*', s=100)
    
    # 设置坐标轴
    ax.set_xticks(np.arange(-0.5, grid_map.width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid_map.height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
    ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    
    # 保存图像到内存
    buf = io.BytesIO()
    if request.format == "svg":
        plt.savefig(buf, format='svg', bbox_inches='tight')
        mime_type = "image/svg+xml"
    else:  # default to png
        plt.savefig(buf, format='png', bbox_inches='tight')
        mime_type = "image/png"
    
    plt.close(fig)
    buf.seek(0)
    
    # 返回图像
    return Response(content=buf.getvalue(), media_type=mime_type)

@router.get("/metrics")
async def get_metrics(grid_map: GridMap = Depends(get_current_map)):
    """
    获取地图统计指标
    """
    # 计算地图中的障碍物比例
    obstacle_count = 0
    terrain_stats = {}
    
    for y in range(grid_map.height):
        for x in range(grid_map.width):
            if grid_map.is_obstacle(x, y):
                obstacle_count += 1
            
            # 如果是地形地图，统计各类地形
            if isinstance(grid_map, TerrainMap):
                terrain_type = grid_map.terrain_type[y, x]
                if not terrain_stats.get(terrain_type):
                    terrain_stats[terrain_type] = 0
                terrain_stats[terrain_type] += 1
    
    total_cells = grid_map.width * grid_map.height
    
    result = {
        "width": grid_map.width,
        "height": grid_map.height,
        "total_cells": total_cells,
        "obstacle_count": obstacle_count,
        "obstacle_ratio": obstacle_count / total_cells,
        "free_cells": total_cells - obstacle_count,
        "free_ratio": (total_cells - obstacle_count) / total_cells
    }
    
    # 如果是地形地图，添加地形统计
    if isinstance(grid_map, TerrainMap):
        result["terrain_stats"] = {str(k): {"count": v, "ratio": v/total_cells} for k, v in terrain_stats.items()}
    
    return result 