import heapq
import math
from typing import List, Tuple, Callable, Set, Dict, Any

def euclidean_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    计算欧几里得距离
    
    参数:
        p1: 第一个点(x, y)
        p2: 第二个点(x, y)
    
    返回:
        两点间的欧几里得距离
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    计算曼哈顿距离
    
    参数:
        p1: 第一个点(x, y)
        p2: 第二个点(x, y)
    
    返回:
        两点间的曼哈顿距离
    """
    return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])

def diagonal_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    计算对角线距离（切比雪夫距离）
    
    参数:
        p1: 第一个点(x, y)
        p2: 第二个点(x, y)
    
    返回:
        两点间的对角线距离
    """
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    return max(dx, dy) + 0.414 * min(dx, dy)  # √2-1 ≈ 0.414

def astar_search(grid_map, start: Tuple[int, int], goal: Tuple[int, int], 
                heuristic_func: Callable[[Tuple[int, int], Tuple[int, int]], float]):
    """
    A*搜索算法
    
    参数:
        grid_map: 栅格地图对象
        start: 起点坐标(x, y)
        goal: 终点坐标(x, y)
        heuristic_func: 启发函数
    
    返回:
        如果找到路径，返回(路径, 已探索节点集合)；否则返回(None, 已探索节点集合)
    """
    # 初始化open和closed集合
    open_set = []  # 优先队列
    closed_set = set()  # 已访问节点集合
    
    # g, h, f值字典
    g_score = {start: 0}
    f_score = {start: heuristic_func(start, goal)}
    
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
                
                # 更新g和f值
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + heuristic_func(neighbor, goal)
                
                # 如果邻居不在open集合中，添加它
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # 如果没有找到路径
    return None, list(explored_nodes) 