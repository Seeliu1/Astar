# 基于A*算法的复杂地形路径规划系统

这是一个使用A*算法及其改进变体进行路径规划的Web应用程序，支持不同地形代价和障碍物的复杂环境。

## 功能特点

- 支持多种地图生成方式：随机障碍物、迷宫、复杂地形
- 提供多种A*算法变体：标准A*、自适应A*
- 支持多种启发函数：欧几里得距离、曼哈顿距离、对角线距离
- 路径后处理：路径平滑、碰撞检测和修正
- 交互式地图编辑器
- 路径规划过程可视化
- 性能统计和对比分析

## 安装

### 环境要求

- Python 3.8+
- 必要依赖库：参见requirements.txt

### 安装步骤

1. 克隆或下载本仓库：

```
git clone https://github.com/yourusername/astar_path_planning.git
cd astar_path_planning
```

2. 安装依赖：

```
pip install -r requirements.txt
```

## 使用方法

1. 启动应用：

```
python main.py
```

2. 在浏览器中访问：http://localhost:8000

3. 使用界面：
   - 创建地图：选择地图类型并设置尺寸
   - 编辑地图：使用提供的工具绘制障碍物或设置不同地形
   - 设置起点和终点
   - 选择算法和启发函数
   - 点击"寻找路径"按钮开始路径规划

## 系统结构

- `app/models/`: 数据模型定义，包括网格地图和节点
- `app/utils/`: 工具函数，包括A*算法实现和地图生成器
- `app/routers/`: API路由定义
- `app/templates/`: 前端模板
- `app/static/`: 静态资源

## API接口

系统提供以下主要API接口：

- 地图管理：`/grid/*`
- 路径规划：`/path/*`
- 可视化：`/visualization/*`

详细API文档可在启动应用后访问：http://localhost:8000/docs

## 扩展与定制

系统设计良好的模块化结构使其易于扩展：

- 添加新的启发函数：在`app/utils/astar.py`中添加
- 添加新的A*变体：在`app/utils/improved_astar.py`中添加
- 添加新的地图生成方法：在`app/utils/map_generator.py`中添加

## 许可

本项目采用MIT许可证。 
