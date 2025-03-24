import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# 创建FastAPI应用
app = FastAPI(title="基于A*算法的复杂地形路径规划系统")

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="astar_path_planning/app/static"), name="static")
templates = Jinja2Templates(directory="astar_path_planning/app/templates")

# 导入路由
from astar_path_planning.app.routers import grid, pathfinding, visualization

# 注册路由
app.include_router(grid.router)
app.include_router(pathfinding.router)
app.include_router(visualization.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """渲染主页"""
    return templates.TemplateResponse("index.html", {"request": request})

# 创建静态文件夹（如果不存在）
os.makedirs("astar_path_planning/app/static", exist_ok=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 