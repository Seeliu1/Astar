import os
import sys
import uvicorn

# 添加当前目录到Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用程序
from astar_path_planning.main import app

if __name__ == "__main__":
    # 确保目录  结构存在
    os.makedirs("astar_path_planning/app/static", exist_ok=True)
    
    # 运行应用
    uvicorn.run("astar_path_planning.main:app", host="127.0.0.1", port=8000, reload=True) 