import numpy as np
import math
from typing import List, Tuple, Dict
from .grid_map import GridMap, TerrainMap

class DynamicObstacle:
    """动态障碍物类"""
    def __init__(self, x: int, y: int, movement_pattern: str, params: Dict = None):
        """
        初始化动态障碍物
        
        参数:
            x, y: 初始位置
            movement_pattern: 移动模式（'linear', 'circular', 'random'）
            params: 移动参数（如速度、范围等）
        """
        self.x = x
        self.y = y
        self.movement_pattern = movement_pattern
        self.params = params or {}
        self.initial_x = x
        self.initial_y = y
        self.time = 0
    
    def update(self, delta_time: float):
        """更新障碍物位置"""
        self.time += delta_time
        
        if self.movement_pattern == 'linear':
            # 线性移动（来回移动）
            amplitude = self.params.get('amplitude', 5)
            frequency = self.params.get('frequency', 1.0)
            self.x = self.initial_x + int(amplitude * math.sin(2 * math.pi * frequency * self.time))
            
        elif self.movement_pattern == 'circular':
            # 圆周运动
            radius = self.params.get('radius', 3)
            frequency = self.params.get('frequency', 1.0)
            self.x = self.initial_x + int(radius * math.cos(2 * math.pi * frequency * self.time))
            self.y = self.initial_y + int(radius * math.sin(2 * math.pi * frequency * self.time))
            
        elif self.movement_pattern == 'random':
            # 随机移动
            if self.time >= self.params.get('update_interval', 1.0):
                self.x += np.random.randint(-1, 2)
                self.y += np.random.randint(-1, 2)
                self.time = 0

class AdvancedMap(TerrainMap):
    """高级地图类，支持动态障碍物、多层地形和环境因素"""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.dynamic_obstacles: List[DynamicObstacle] = []
        self.elevation = np.zeros((height, width), dtype=float)  # 高度信息
        self.zones = np.zeros((height, width), dtype=int)  # 区域信息
        self.weather_condition = 'clear'  # 天气状况
        self.light_level = 1.0  # 光照水平（0.0-1.0）
        
    def add_dynamic_obstacle(self, x: int, y: int, movement_pattern: str, params: Dict = None):
        """添加动态障碍物"""
        obstacle = DynamicObstacle(x, y, movement_pattern, params)
        self.dynamic_obstacles.append(obstacle)
    
    def update_dynamic_obstacles(self, delta_time: float):
        """更新所有动态障碍物的位置"""
        # 清除旧的动态障碍物标记
        for obstacle in self.dynamic_obstacles:
            if self.is_valid(obstacle.x, obstacle.y):
                super().clear_obstacle(obstacle.x, obstacle.y)
        
        # 更新并标记新的动态障碍物位置
        for obstacle in self.dynamic_obstacles:
            obstacle.update(delta_time)
            if self.is_valid(obstacle.x, obstacle.y):
                super().set_obstacle(obstacle.x, obstacle.y)
    
    def set_elevation(self, x: int, y: int, height: float):
        """设置地形高度"""
        if self.is_valid(x, y):
            self.elevation[y, x] = height
    
    def get_elevation(self, x: int, y: int) -> float:
        """获取地形高度"""
        if not self.is_valid(x, y):
            return float('inf')
        return self.elevation[y, x]
    
    def set_zone(self, x: int, y: int, zone_id: int):
        """设置区域标识"""
        if self.is_valid(x, y):
            self.zones[y, x] = zone_id
    
    def get_zone(self, x: int, y: int) -> int:
        """获取区域标识"""
        if not self.is_valid(x, y):
            return -1
        return self.zones[y, x]
    
    def set_weather(self, condition: str):
        """设置天气状况"""
        self.weather_condition = condition
    
    def set_light_level(self, level: float):
        """设置光照水平"""
        self.light_level = max(0.0, min(1.0, level))
    
    def get_movement_cost(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """计算考虑多个因素的移动代价"""
        if self.is_obstacle(x2, y2):
            return float('inf')
        
        # 基础移动代价
        base_cost = super().get_movement_cost(x1, y1, x2, y2)
        
        # 高度变化带来的额外代价
        elevation_diff = abs(self.get_elevation(x2, y2) - self.get_elevation(x1, y1))
        elevation_cost = elevation_diff * 0.5
        
        # 天气影响
        weather_factor = {
            'clear': 1.0,
            'rain': 1.5,
            'snow': 2.0,
            'fog': 1.3
        }.get(self.weather_condition, 1.0)
        
        # 光照影响（夜间移动代价增加）
        light_factor = 1.0 + (1.0 - self.light_level) * 0.5
        
        # 计算总代价
        total_cost = base_cost + elevation_cost
        total_cost *= weather_factor * light_factor
        
        return total_cost