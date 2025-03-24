from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
from astar_path_planning.app.models.grid_map import GridMap, TerrainMap
from astar_path_planning.app.utils.map_generator import initialize_test_environment, generate_random_obstacles, generate_maze, generate_complex_terrain

router = APIRouter(prefix="/grid", tags=["地图管理"])

# 内存中的地图对象
current_map = None

class MapConfig(BaseModel):
    width: int = 50
    height: int = 50
    map_type: str = "simple"  # simple, maze, complex

class MapCell(BaseModel):
    x: int
    y: int
    is_obstacle: bool = False
    terrain_type: int = 0
    cost: float = 1.0

class MapData(BaseModel):
    width: int
    height: int
    cells: List[MapCell]
    map_type: str = "simple"

def get_current_map() -> GridMap:
    """获取当前地图对象"""
    global current_map
    if current_map is None:
        current_map = initialize_test_environment(50, 50, 'simple')
    return current_map

@router.post("/create", response_model=MapData)
async def create_map(config: MapConfig):
    """
    创建新地图
    """
    global current_map
    
    if config.width <= 0 or config.height <= 0:
        raise HTTPException(status_code=400, detail="地图尺寸必须大于0")
    
    if config.width > 200 or config.height > 200:
        raise HTTPException(status_code=400, detail="地图尺寸过大，最大支持200x200")
    
    # 根据类型初始化地图
    current_map = initialize_test_environment(config.width, config.height, config.map_type)
    
    # 转换为API响应格式
    cells = []
    for y in range(current_map.height):
        for x in range(current_map.width):
            cell = MapCell(
                x=x,
                y=y,
                is_obstacle=current_map.is_obstacle(x, y),
                cost=current_map.get_terrain_cost(x, y)
            )
            
            # 如果是地形地图，添加地形类型
            if config.map_type == "complex" and isinstance(current_map, TerrainMap):
                cell.terrain_type = current_map.terrain_type[y, x]
                
            cells.append(cell)
    
    return MapData(width=current_map.width, height=current_map.height, cells=cells, map_type=config.map_type)

@router.get("/current", response_model=MapData)
async def get_map(grid_map: GridMap = Depends(get_current_map)):
    """
    获取当前地图数据
    """
    cells = []
    for y in range(grid_map.height):
        for x in range(grid_map.width):
            cell = MapCell(
                x=x,
                y=y,
                is_obstacle=grid_map.is_obstacle(x, y),
                cost=grid_map.get_terrain_cost(x, y)
            )
            
            # 如果是地形地图，添加地形类型
            if isinstance(grid_map, TerrainMap):
                cell.terrain_type = grid_map.terrain_type[y, x]
                
            cells.append(cell)
    
    map_type = "complex" if isinstance(grid_map, TerrainMap) else "simple"
    return MapData(width=grid_map.width, height=grid_map.height, cells=cells, map_type=map_type)

@router.post("/cell/update")
async def update_cell(cell: MapCell, grid_map: GridMap = Depends(get_current_map)):
    """
    更新单元格状态
    """
    if not grid_map.is_valid(cell.x, cell.y):
        raise HTTPException(status_code=400, detail="坐标超出地图范围")
    
    if cell.is_obstacle:
        grid_map.set_obstacle(cell.x, cell.y)
    else:
        grid_map.clear_obstacle(cell.x, cell.y)
        
        # 如果是地形地图，更新地形类型和代价
        if isinstance(grid_map, TerrainMap):
            grid_map.set_terrain(cell.x, cell.y, cell.terrain_type, cell.cost)
        else:
            grid_map.set_terrain_cost(cell.x, cell.y, cell.cost)
    
    return {"message": "单元格更新成功"}

@router.post("/clear")
async def clear_map(grid_map: GridMap = Depends(get_current_map)):
    """
    清空地图（移除所有障碍物）
    """
    for y in range(grid_map.height):
        for x in range(grid_map.width):
            grid_map.clear_obstacle(x, y)
            
            # 如果是地形地图，重置为平地
            if isinstance(grid_map, TerrainMap):
                grid_map.set_terrain(x, y, 0, 1.0)
    
    return {"message": "地图已清空"} 