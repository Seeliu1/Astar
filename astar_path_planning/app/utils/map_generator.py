import numpy as np
import random
import math
from typing import Optional, Tuple, List
from astar_path_planning.app.models.grid_map import GridMap, TerrainMap

def generate_random_obstacles(grid_map: GridMap, obstacle_density: float = 0.3, seed: Optional[int] = None):
    """
    在地图中随机生成障碍物
    
    参数:
        grid_map: 栅格地图对象
        obstacle_density: 障碍物密度，范围[0, 1]
        seed: 随机种子，为None时使用系统时间
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 随机生成障碍物
    for y in range(grid_map.height):
        for x in range(grid_map.width):
            if np.random.random() < obstacle_density:
                grid_map.set_obstacle(x, y)

def generate_maze(grid_map: GridMap, seed: Optional[int] = None):
    """
    使用深度优先搜索算法生成迷宫
    
    参数:
        grid_map: 栅格地图对象
        seed: 随机种子，为None时使用系统时间
    """
    if seed is not None:
        random.seed(seed)
    
    # 初始化所有单元格为墙（障碍物）
    for y in range(grid_map.height):
        for x in range(grid_map.width):
            grid_map.set_obstacle(x, y)
    
    # 获取地图尺寸
    width, height = grid_map.width, grid_map.height
    
    # 使用深度优先搜索生成迷宫
    def carve_passages_from(cx: int, cy: int, visited: set):
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # 上、右、下、左
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < width and 0 <= ny < height and 
                (nx, ny) not in visited):
                visited.add((nx, ny))
                grid_map.clear_obstacle(nx, ny)
                grid_map.clear_obstacle(cx + dx//2, cy + dy//2)  # 清除中间的墙
                carve_passages_from(nx, ny, visited)
    
    # 选择起点并开始生成
    start_x, start_y = 1, 1
    visited = {(start_x, start_y)}
    grid_map.clear_obstacle(start_x, start_y)
    carve_passages_from(start_x, start_y, visited)

def generate_complex_terrain(terrain_map: TerrainMap, seed: Optional[int] = None):
    """
    生成具有不同地形类型的复杂地形地图
    
    参数:
        terrain_map: 地形地图对象
        seed: 随机种子，为None时使用系统时间
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 地形类型及其代价（限制最大值为10.0）
    terrain_types = {
        0: 1.0,    # 平地
        1: min(2.0, 10.0),    # 山地
        2: min(3.0, 10.0)     # 水域
    }
    
    # 使用柏林噪声或简单随机生成不同的地形区域
    # 这里使用简化版本，使用随机生成
    
    # 先随机放置一些种子点
    seeds = []
    for terrain_type in range(3):  # 3种地形类型
        num_seeds = np.random.randint(3, 10)  # 每种地形随机生成3-10个种子点
        for _ in range(num_seeds):
            x = np.random.randint(0, terrain_map.width)
            y = np.random.randint(0, terrain_map.height)
            seeds.append((x, y, terrain_type))
    
    # 对每个点，找到最近的种子点并设置为对应的地形类型
    for y in range(terrain_map.height):
        for x in range(terrain_map.width):
            # 计算到每个种子点的距离，选择最近的
            min_dist = None
            terrain = 0  # 默认为平地
            
            for seed_x, seed_y, seed_terrain in seeds:
                # 使用曼哈顿距离
                dist = abs(x - seed_x) + abs(y - seed_y)
                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    terrain = seed_terrain
            
            # 设置地形类型和代价（确保代价在有效范围内）
            try:
                cost = min(float(terrain_types[terrain]), 10.0)  # 限制最大代价为10.0
                if not math.isinf(cost) and not math.isnan(cost):
                    terrain_map.set_terrain(x, y, terrain, cost)
                else:
                    # 如果代价无效，使用默认值
                    terrain_map.set_terrain(x, y, 0, 1.0)
            except (ValueError, TypeError):
                # 如果转换失败，使用默认值
                terrain_map.set_terrain(x, y, 0, 1.0)
    
    # 随机生成一些障碍物
    generate_random_obstacles(terrain_map, obstacle_density=0.1, seed=seed)

def generate_u_shape_obstacle(grid_map: GridMap, center_x: int, center_y: int, size: int):
    """
    在地图中生成U形障碍物
    
    参数:
        grid_map: 栅格地图对象
        center_x, center_y: U形障碍物的中心坐标
        size: U形障碍物的大小
    """
    # 确保位置合法
    if (center_x - size//2 < 0 or center_x + size//2 >= grid_map.width or
        center_y - size//2 < 0 or center_y + size//2 >= grid_map.height):
        return
    
    # 绘制U形的底边
    for x in range(center_x - size//2, center_x + size//2 + 1):
        grid_map.set_obstacle(x, center_y - size//2)
    
    # 绘制U形的左边
    for y in range(center_y - size//2, center_y + size//2 + 1):
        grid_map.set_obstacle(center_x - size//2, y)
    
    # 绘制U形的右边
    for y in range(center_y - size//2, center_y + size//2 + 1):
        grid_map.set_obstacle(center_x + size//2, y)

def generate_spiral_obstacles(grid_map: GridMap, center_x: int, center_y: int, max_radius: int):
    """
    生成螺旋形障碍物
    
    参数:
        grid_map: 栅格地图对象
        center_x, center_y: 螺旋的中心坐标
        max_radius: 最大半径
    """
    theta = 0
    radius = 0
    step = 0.2
    while radius < max_radius:
        x = int(center_x + radius * math.cos(theta))
        y = int(center_y + radius * math.sin(theta))
        if grid_map.is_valid(x, y):
            grid_map.set_obstacle(x, y)
        theta += step
        radius = theta / (2 * math.pi)

def generate_radial_obstacles(grid_map: GridMap, center_x: int, center_y: int, num_rays: int, length: int):
    """
    生成放射状障碍物
    
    参数:
        grid_map: 栅格地图对象
        center_x, center_y: 放射中心坐标
        num_rays: 射线数量
        length: 射线长度
    """
    for i in range(num_rays):
        angle = 2 * math.pi * i / num_rays
        for r in range(length):
            x = int(center_x + r * math.cos(angle))
            y = int(center_y + r * math.sin(angle))
            if grid_map.is_valid(x, y):
                grid_map.set_obstacle(x, y)

def initialize_test_environment(width: int, height: int, map_type: str = "simple") -> GridMap:
    """
    初始化测试环境，创建指定类型的地图
    
    参数:
        width: 地图宽度
        height: 地图高度
        map_type: 地图类型，可选值: "simple"(随机障碍物), "maze"(迷宫), "complex"(复杂地形),
                           "advanced"(高级地图，包含动态障碍物和环境因素)
    
    返回:
        grid_map: 创建的地图对象
    """
    if map_type == "advanced":
        # 创建高级地图
        grid_map = AdvancedMap(width, height)
        # 添加动态障碍物
        grid_map.add_dynamic_obstacle(width//4, height//4, 'linear', {'amplitude': 5, 'frequency': 0.5})
        grid_map.add_dynamic_obstacle(width//2, height//2, 'circular', {'radius': 3, 'frequency': 0.3})
        # 设置地形和环境
        for y in range(height):
            for x in range(width):
                # 设置随机高度
                elevation = np.random.uniform(0, 5)
                grid_map.set_elevation(x, y, elevation)
                # 设置区域
                zone = (x // (width//3)) + (y // (height//3)) * 3
                grid_map.set_zone(x, y, zone)
        # 设置天气和光照
        grid_map.set_weather('rain')
        grid_map.set_light_level(0.7)
        
    elif map_type == "complex":
        # 创建地形地图
        grid_map = TerrainMap(width, height)
        generate_complex_terrain(grid_map)
        # 添加螺旋和放射状障碍物
        generate_spiral_obstacles(grid_map, width//3, height//3, min(width, height)//4)
        generate_radial_obstacles(grid_map, 2*width//3, 2*height//3, 8, min(width, height)//5)
        
    else:
        # 创建基础栅格地图
        grid_map = GridMap(width, height)
        
        if map_type == "maze":
            # 生成迷宫
            generate_maze(grid_map)
        else:  # simple
            # 生成随机障碍物
            generate_random_obstacles(grid_map, obstacle_density=0.2)
            
            # 添加一些U形障碍物
            num_u_shapes = random.randint(1, 3)
            for _ in range(num_u_shapes):
                center_x = random.randint(width//4, 3*width//4)
                center_y = random.randint(height//4, 3*height//4)
                size = random.randint(5, min(15, width//5, height//5))
                generate_u_shape_obstacle(grid_map, center_x, center_y, size)
    
    return grid_map