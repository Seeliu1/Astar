import numpy as np
import math

class GridMap:
    """栅格地图类，用于表示二维栅格环境"""
    
    def __init__(self, width, height):
        """
        初始化栅格地图
        
        参数:
            width (int): 地图宽度
            height (int): 地图高度
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=bool)  # False表示可通行，True表示障碍物
        self.cost_map = np.ones((height, width), dtype=float)  # 默认代价为1.0
    
    def is_valid(self, x, y):
        """检查坐标是否在地图范围内"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def set_obstacle(self, x, y):
        """在指定位置设置障碍物"""
        if self.is_valid(x, y):
            self.grid[y, x] = True
            self.cost_map[y, x] = float('inf')
    
    def clear_obstacle(self, x, y):
        """清除指定位置的障碍物"""
        if self.is_valid(x, y):
            self.grid[y, x] = False
            self.cost_map[y, x] = 1.0
    
    def is_obstacle(self, x, y):
        """检查指定位置是否是障碍物"""
        if not self.is_valid(x, y):
            return True  # 地图边界外视为障碍物
        return self.grid[y, x]
    
    def set_terrain_cost(self, x, y, cost):
        """设置指定位置的地形代价"""
        if self.is_valid(x, y) and not self.is_obstacle(x, y):
            self.cost_map[y, x] = cost
    
    def get_terrain_cost(self, x, y):
        """获取指定位置的地形代价"""
        if not self.is_valid(x, y):
            return float('inf')
        return self.cost_map[y, x]
    
    def get_movement_cost(self, x1, y1, x2, y2):
        """计算从(x1,y1)移动到(x2,y2)的代价"""
        if self.is_obstacle(x2, y2):
            return float('inf')
        
        # 移动距离 * 目标格子的地形代价
        base_cost = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return base_cost * self.cost_map[y2, x2]
    
    def get_neighbors(self, x, y):
        """获取(x,y)周围的八个方向的邻居坐标"""
        neighbors = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # 跳过自身
                
                nx, ny = x + dx, y + dy
                if self.is_valid(nx, ny) and not self.is_obstacle(nx, ny):
                    neighbors.append((nx, ny))
        
        return neighbors


class TerrainMap(GridMap):
    """带有地形类型的地形地图类"""
    
    def __init__(self, width, height):
        """
        初始化地形地图
        
        参数:
            width (int): 地图宽度
            height (int): 地图高度
        """
        super().__init__(width, height)
        # 地形类型: 0-平地，1-山地，2-水域，3-沙地等
        self.terrain_type = np.zeros((height, width), dtype=int)
    
    def set_terrain(self, x, y, terrain_type, cost_factor):
        """
        设置指定位置的地形类型和代价
        
        参数:
            x, y: 坐标
            terrain_type: 地形类型(0-平地，1-山地，2-水域等)
            cost_factor: 地形代价系数
        """
        if self.is_valid(x, y) and not self.is_obstacle(x, y):
            self.terrain_type[y, x] = terrain_type
            self.cost_map[y, x] = cost_factor
    
    def get_terrain_type(self, x, y):
        """获取指定位置的地形类型"""
        if not self.is_valid(x, y):
            return -1  # 无效地形
        return self.terrain_type[y, x] 