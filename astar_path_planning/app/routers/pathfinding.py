from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import time
from astar_path_planning.app.models.grid_map import GridMap
from astar_path_planning.app.utils.astar import astar_search, euclidean_distance, manhattan_distance, diagonal_distance
from astar_path_planning.app.utils.improved_astar import adaptive_astar_search, terrain_aware_heuristic, smooth_path, check_and_fix_collision
from astar_path_planning.app.routers.grid import get_current_map

router = APIRouter(prefix="/path", tags=["路径规划"])

class PathRequest(BaseModel):
    start_x: int
    start_y: int
    goal_x: int
    goal_y: int
    algorithm: str = "astar"  # astar, adaptive_astar
    heuristic: str = "euclidean"  # euclidean, manhattan, diagonal
    smooth: bool = False
    check_collision: bool = False

class PathPoint(BaseModel):
    x: int
    y: int

class PathResponse(BaseModel):
    path: List[PathPoint]
    explored: List[PathPoint]
    path_length: float
    computation_time: float
    path_cost: float
    nodes_explored: int

def get_heuristic(heuristic_name: str):
    """根据名称获取启发函数"""
    if heuristic_name == "manhattan":
        return manhattan_distance
    elif heuristic_name == "diagonal":
        return diagonal_distance
    else:  # default to euclidean
        return euclidean_distance

@router.post("/find", response_model=PathResponse)
async def find_path(request: PathRequest, grid_map: GridMap = Depends(get_current_map)):
    """
    使用指定算法寻找路径
    """
    # 检查起点和终点是否有效
    if not grid_map.is_valid(request.start_x, request.start_y):
        raise HTTPException(status_code=400, detail="起点坐标无效")
        
    if not grid_map.is_valid(request.goal_x, request.goal_y):
        raise HTTPException(status_code=400, detail="终点坐标无效")
    
    # 检查起点和终点是否是障碍物
    if grid_map.is_obstacle(request.start_x, request.start_y):
        raise HTTPException(status_code=400, detail="起点是障碍物")
        
    if grid_map.is_obstacle(request.goal_x, request.goal_y):
        raise HTTPException(status_code=400, detail="终点是障碍物")
    
    # 获取启发函数
    heuristic_func = get_heuristic(request.heuristic)
    
    # 记录计算时间
    start_time = time.time()
    
    # 根据请求的算法进行路径规划
    start = (request.start_x, request.start_y)
    goal = (request.goal_x, request.goal_y)
    
    if request.algorithm == "adaptive_astar":
        path, explored = adaptive_astar_search(grid_map, start, goal, heuristic_func)
    else:  # default to standard A*
        path, explored = astar_search(grid_map, start, goal, heuristic_func)
    
    computation_time = time.time() - start_time
    
    # 如果未找到路径
    if path is None:
        return PathResponse(
            path=[],
            explored=[PathPoint(x=e[0], y=e[1]) for e in explored],
            path_length=0,
            computation_time=computation_time,
            path_cost=float('inf'),
            nodes_explored=len(explored)
        )
    
    # 路径后处理
    original_path = path.copy()
    
    # 如果需要路径平滑
    if request.smooth and len(path) > 2:
        path = smooth_path(grid_map, path)
    
    # 如果需要碰撞检查
    if request.check_collision:
        path = check_and_fix_collision(grid_map, path)
    
    # 计算路径长度和代价
    path_length = 0.0
    path_cost = 0.0
    
    for i in range(1, len(path)):
        x1, y1 = path[i-1]
        x2, y2 = path[i]
        segment_length = euclidean_distance((x1, y1), (x2, y2))
        path_length += segment_length
        path_cost += grid_map.get_movement_cost(x1, y1, x2, y2)
    
    # 转换为API响应格式
    return PathResponse(
        path=[PathPoint(x=p[0], y=p[1]) for p in path],
        explored=[PathPoint(x=e[0], y=e[1]) for e in explored],
        path_length=path_length,
        computation_time=computation_time,
        path_cost=path_cost,
        nodes_explored=len(explored)
    )

@router.get("/heuristics")
async def get_available_heuristics():
    """
    获取可用的启发函数列表
    """
    return {
        "heuristics": [
            {"id": "euclidean", "name": "欧几里得距离"},
            {"id": "manhattan", "name": "曼哈顿距离"},
            {"id": "diagonal", "name": "对角线距离"}
        ]
    }

@router.get("/algorithms")
async def get_available_algorithms():
    """
    获取可用的路径规划算法列表
    """
    return {
        "algorithms": [
            {"id": "astar", "name": "A*算法"},
            {"id": "adaptive_astar", "name": "自适应A*算法"}
        ]
    } 