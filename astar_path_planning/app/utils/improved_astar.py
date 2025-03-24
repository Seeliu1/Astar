import heapq
import math
import numpy as np
from typing import List, Tuple, Callable, Set, Dict, Any, Optional
from astar_path_planning.app.utils.astar import euclidean_distance, manhattan_distance, diagonal_distance

def adaptive_weight(current: Tuple[int, int], start: Tuple[int, int], goal: Tuple[int, int]) -> float:
    """
    自适应权重函数，根据节点位置调整启发函数的权重
    
    参数:
        current: 当前节点(x, y)
        start: 起点(x, y)
        goal: 终点(x, y)
    
    返回:
        启发函数权重值，范围在[1.0, 2.0]
    """
    # 计算节点到起点和终点的距离比例
    dist_to_start = euclidean_distance(current, start)
    dist_to_goal = euclidean_distance(current, goal)
    total_dist = dist_to_start + dist_to_goal
    
    if total_dist == 0:
        return 1.0
    
    # 节点越接近目标，权重越小
    ratio = dist_to_goal / total_dist
    
    # 返回范围在[1.0, 2.0]的权重
    return 1.0 + ratio
    
def terrain_aware_heuristic(p1: Tuple[int, int], p2: Tuple[int, int], grid_map, base_heuristic: Callable = euclidean_distance) -> float:
    """
    考虑地形的启发函数，调整基础启发函数的值
    
    参数:
        p1: 第一个点(x, y)
        p2: 第二个点(x, y)
        grid_map: 栅格地图对象
        base_heuristic: 基础启发函数
    
    返回:
        考虑地形的启发函数值
    """
    # 计算基础启发函数值
    base_value = base_heuristic(p1, p2)
    
    # 如果grid_map提供了地形信息，可以结合地形代价
    # 这里使用一个简单的方法：沿直线采样几个点的地形代价，取平均值
    samples = 5
    avg_cost = 0.0
    
    for i in range(1, samples + 1):
        # 在p1和p2之间等距离取样
        t = i / (samples + 1)
        sample_x = int(p1[0] + t * (p2[0] - p1[0]))
        sample_y = int(p1[1] + t * (p2[1] - p1[1]))
        
        # 获取采样点的地形代价
        if grid_map.is_valid(sample_x, sample_y) and not grid_map.is_obstacle(sample_x, sample_y):
            avg_cost += grid_map.get_terrain_cost(sample_x, sample_y)
        else:
            avg_cost += 1.0  # 默认代价
    
    avg_cost /= samples
    
    # 如果地形代价高，增加启发函数值
    return base_value * max(1.0, avg_cost)

def get_line_points(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
    """使用Bresenham算法获取直线上的所有点"""
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    
    if dx > dy:
        err = dx / 2.0
        while x != x2:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y2:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
            
    points.append((x2, y2))
    return points

def get_dynamic_directions(current: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """获取动态扩展方向"""
    dx = goal[0] - current[0]
    dy = goal[1] - current[1]
    
    # 基础方向：东、西、南、北、东北、西北、东南、西南
    base_directions = [(1,0), (-1,0), (0,1), (0,-1), 
                      (1,1), (-1,1), (1,-1), (-1,-1)]
    
    # 如果dx或dy为0，不需要排序
    if dx == 0 or dy == 0:
        return base_directions
    
    # 根据目标方向对扩展方向进行排序
    # 计算每个方向与目标方向的点积，点积越大表示方向越相近
    return sorted(base_directions, 
                 key=lambda d: -(dx*d[0] + dy*d[1])/
                              (math.sqrt(d[0]**2 + d[1]**2) * 
                               math.sqrt(dx**2 + dy**2)))

def adaptive_astar_search(grid_map, start: Tuple[int, int], goal: Tuple[int, int], 
                         heuristic_func: Callable = euclidean_distance):
    """
    自适应A*搜索算法，动态调整启发函数的权重
    
    参数:
        grid_map: 栅格地图对象
        start: 起点坐标(x, y)
        goal: 终点坐标(x, y)
        heuristic_func: 基础启发函数
    
    返回:
        如果找到路径，返回(路径, 已探索节点集合)；否则返回(None, 已探索节点集合)
    """
    # 初始化open和closed集合
    open_set = []  # 优先队列
    closed_set = set()  # 已访问节点集合
    
    # g, h, f值字典
    g_score = {start: 0}
    h_score = {start: heuristic_func(start, goal)}
    f_score = {start: h_score[start]}
    
    # 添加起点到open集合
    heapq.heappush(open_set, (f_score[start], start))
    
    # 用于重建路径的父节点字典
    came_from = {}
    
    # 记录已探索的节点
    explored_nodes = set()
    
    while open_set:
        # 获取f值最小的节点
        _, current = heapq.heappop(open_set)
        
        # 记录已探索节点
        explored_nodes.add(current)
        
        # 如果到达目标
        if current == goal:
            # 重建路径
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            
            path.append(start)
            path.reverse()
            return path, list(explored_nodes)
        
        # 将当前节点添加到closed集合
        closed_set.add(current)
        
        # 获取邻居节点
        neighbors = grid_map.get_neighbors(current[0], current[1])
        
        # 对每个邻居进行处理
        for neighbor in neighbors:
            # 如果邻居在closed集合中，跳过
            if neighbor in closed_set:
                continue
            
            # 计算通过当前节点到达邻居的g值
            tentative_g = g_score[current] + grid_map.get_movement_cost(
                current[0], current[1], neighbor[0], neighbor[1])
            
            # 如果邻居不在open集合中，或者找到了更好的路径
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # 更新父节点
                came_from[neighbor] = current
                
                # 更新g值
                g_score[neighbor] = tentative_g
                
                # 计算h值，使用地形感知的启发函数
                h_score[neighbor] = terrain_aware_heuristic(neighbor, goal, grid_map, heuristic_func)
                
                # 应用自适应权重
                weight = adaptive_weight(neighbor, start, goal)
                
                # 更新f值
                f_score[neighbor] = g_score[neighbor] + weight * h_score[neighbor]
                
                # 如果邻居不在open集合中，添加它
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # 如果没有找到路径
    return None, list(explored_nodes)

def smooth_path(grid_map, path: List[Tuple[int, int]], window_size: int = 3) -> List[Tuple[int, int]]:
    """
    对路径进行平滑处理
    
    参数:
        grid_map: 栅格地图对象
        path: 原始路径
        window_size: 平滑窗口大小
    
    返回:
        平滑后的路径
    """
    if len(path) <= 2:
        return path  # 点数太少，无需平滑
    
    # 保留起点和终点
    smoothed_path = [path[0]]
    
    # 对中间点进行平滑
    for i in range(1, len(path) - 1):
        # 确定窗口范围
        window_start = max(0, i - window_size // 2)
        window_end = min(len(path) - 1, i + window_size // 2)
        
        # 计算窗口内点的加权平均
        avg_x, avg_y = 0, 0
        total_weight = 0
        
        for j in range(window_start, window_end + 1):
            # 距离中心点越近，权重越大
            weight = 1.0 / (abs(j - i) + 1)
            avg_x += path[j][0] * weight
            avg_y += path[j][1] * weight
            total_weight += weight
        
        avg_x /= total_weight
        avg_y /= total_weight
        
        # 将平均点转为整数坐标
        new_x, new_y = int(round(avg_x)), int(round(avg_y))
        
        # 确保平滑后的点不是障碍物
        if grid_map.is_valid(new_x, new_y) and not grid_map.is_obstacle(new_x, new_y):
            smoothed_path.append((new_x, new_y))
        else:
            # 如果是障碍物，则使用原始点
            smoothed_path.append(path[i])
    
    # 添加终点
    smoothed_path.append(path[-1])
    
    return smoothed_path

def check_and_fix_collision(grid_map, path: List[Tuple[int, int]], safety_dist: int = 1) -> List[Tuple[int, int]]:
    """
    检查路径是否有碰撞风险（与障碍物过近），并修正
    
    参数:
        grid_map: 栅格地图对象
        path: 路径
        safety_dist: 安全距离，与障碍物的最小允许距离
    
    返回:
        修正后的路径
    """
    if not path:
        return path
    
    fixed_path = []
    
    for i, point in enumerate(path):
        x, y = point
        
        # 检查点周围是否有障碍物
        has_close_obstacle = False
        
        for dx in range(-safety_dist, safety_dist + 1):
            for dy in range(-safety_dist, safety_dist + 1):
                if dx == 0 and dy == 0:
                    continue
                
                check_x, check_y = x + dx, y + dy
                
                if grid_map.is_valid(check_x, check_y) and grid_map.is_obstacle(check_x, check_y):
                    has_close_obstacle = True
                    break
            
            if has_close_obstacle:
                break
        
        if has_close_obstacle and i > 0 and i < len(path) - 1:
            # 如果是中间点且太靠近障碍物，尝试找到替代点
            prev_x, prev_y = path[i-1]
            next_x, next_y = path[i+1]
            
            # 计算远离障碍物的方向（简单实现：使用前后点的中点）
            alt_x = (prev_x + next_x) // 2
            alt_y = (prev_y + next_y) // 2
            
            # 如果替代点是安全的，使用它
            if grid_map.is_valid(alt_x, alt_y) and not grid_map.is_obstacle(alt_x, alt_y):
                fixed_path.append((alt_x, alt_y))
            else:
                # 否则尝试使用一个小的随机偏移
                found_safe = False
                for _ in range(8):  # 尝试8个方向
                    rand_dx = np.random.randint(-1, 2)
                    rand_dy = np.random.randint(-1, 2)
                    
                    alt_x = x + rand_dx
                    alt_y = y + rand_dy
                    
                    if grid_map.is_valid(alt_x, alt_y) and not grid_map.is_obstacle(alt_x, alt_y):
                        fixed_path.append((alt_x, alt_y))
                        found_safe = True
                        break
                
                if not found_safe:
                    fixed_path.append(point)  # 如果找不到安全点，保留原点
        else:
            fixed_path.append(point)
    
    return fixed_path 