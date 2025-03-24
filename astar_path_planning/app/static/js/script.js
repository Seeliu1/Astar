document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let gridMap = null;
    let cellSize = 15;
    let currentTool = 'select';
    let brushSize = 1;
    let startPosition = null;
    let goalPosition = null;
    let currentPath = null;
    let exploredNodes = null;
    let isSettingStart = false;
    let isSettingGoal = false;
    
    const canvas = document.getElementById('gridCanvas');
    const ctx = canvas.getContext('2d');
    
    // 初始化
    createNewMap();
    
    // 创建新地图
    document.getElementById('createMapBtn').addEventListener('click', createNewMap);
    document.getElementById('clearMapBtn').addEventListener('click', clearMap);
    
    // 编辑工具选择
    document.querySelectorAll('input[name="editTool"]').forEach(tool => {
        tool.addEventListener('change', function() {
            currentTool = this.id.replace('Tool', '');
            
            // 如果选择了地形编辑工具且是复杂地形地图，显示地形选项
            if (document.getElementById('mapType').value === 'complex' && currentTool !== 'select') {
                document.getElementById('terrainTools').classList.remove('d-none');
            } else {
                document.getElementById('terrainTools').classList.add('d-none');
            }
        });
    });
    
    // 画笔大小调整
    document.getElementById('brushSize').addEventListener('input', function() {
        brushSize = parseInt(this.value);
    });
    
    // 地图类型变更
    document.getElementById('mapType').addEventListener('change', function() {
        if (this.value === 'complex') {
            document.getElementById('terrainTools').classList.remove('d-none');
        } else {
            document.getElementById('terrainTools').classList.add('d-none');
        }
    });
    
    // 设置起点和终点
    document.getElementById('setStartBtn').addEventListener('click', function() {
        isSettingStart = true;
        isSettingGoal = false;
        currentTool = 'select';
        document.getElementById('selectTool').checked = true;
    });
    
    document.getElementById('setGoalBtn').addEventListener('click', function() {
        isSettingStart = false;
        isSettingGoal = true;
        currentTool = 'select';
        document.getElementById('selectTool').checked = true;
    });
    
    // 路径规划
    document.getElementById('findPathBtn').addEventListener('click', findPath);
    document.getElementById('clearPathBtn').addEventListener('click', clearPath);
    
    // 鼠标事件处理
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('click', handleClick);
    
    let isDrawing = false;
    
    function handleMouseDown(e) {
        isDrawing = true;
        const { x, y } = getCellCoordinates(e);
        updateCell(x, y);
    }
    
    function handleMouseMove(e) {
        if (!isDrawing) return;
        const { x, y } = getCellCoordinates(e);
        updateCell(x, y);
    }
    
    function handleMouseUp() {
        isDrawing = false;
    }
    
    function handleClick(e) {
        const { x, y } = getCellCoordinates(e);
        
        if (isSettingStart) {
            setStartPosition(x, y);
            isSettingStart = false;
        } else if (isSettingGoal) {
            setGoalPosition(x, y);
            isSettingGoal = false;
        } else {
            updateCell(x, y);
        }
    }
    
    function getCellCoordinates(e) {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / cellSize);
        const y = Math.floor((e.clientY - rect.top) / cellSize);
        return { x, y };
    }
    
    function updateCell(x, y) {
        if (!gridMap || x < 0 || y < 0 || x >= gridMap.width || y >= gridMap.height) {
            return;
        }
        
        for (let brushY = y - Math.floor(brushSize / 2); brushY <= y + Math.floor(brushSize / 2); brushY++) {
            for (let brushX = x - Math.floor(brushSize / 2); brushX <= x + Math.floor(brushSize / 2); brushX++) {
                if (brushX >= 0 && brushY >= 0 && brushX < gridMap.width && brushY < gridMap.height) {
                    const cell = {
                        x: brushX,
                        y: brushY,
                        is_obstacle: false,
                        terrain_type: 0,
                        cost: 1.0
                    };
                    
                    if (currentTool === 'drawObstacle') {
                        cell.is_obstacle = true;
                    } else if (currentTool === 'eraseObstacle') {
                        cell.is_obstacle = false;
                        cell.terrain_type = 0;
                        cell.cost = 1.0;
                    } else if (document.getElementById('mapType').value === 'complex') {
                        // 地形编辑
                        if (document.getElementById('mountainTerrain').checked) {
                            cell.terrain_type = 1;
                            cell.cost = 2.0;
                        } else if (document.getElementById('waterTerrain').checked) {
                            cell.terrain_type = 2;
                            cell.cost = 3.0;
                        } else {
                            cell.terrain_type = 0;
                            cell.cost = 1.0;
                        }
                    }
                    
                    updateCellOnServer(cell);
                }
            }
        }
    }
    
    async function updateCellOnServer(cell) {
        try {
            const response = await fetch('/grid/cell/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(cell),
            });
            
            if (response.ok) {
                // 更新本地网格数据
                for (let i = 0; i < gridMap.cells.length; i++) {
                    if (gridMap.cells[i].x === cell.x && gridMap.cells[i].y === cell.y) {
                        gridMap.cells[i] = cell;
                        break;
                    }
                }
                
                drawGrid();
            }
        } catch (error) {
            console.error('更新单元格失败:', error);
        }
    }
    
    function setStartPosition(x, y) {
        if (!gridMap || x < 0 || y < 0 || x >= gridMap.width || y >= gridMap.height) {
            return;
        }
        
        // 检查是否是障碍物
        for (let cell of gridMap.cells) {
            if (cell.x === x && cell.y === y && cell.is_obstacle) {
                alert('起点不能设置在障碍物上');
                return;
            }
        }
        
        startPosition = { x, y };
        document.getElementById('startPosition').textContent = `起点: (${x}, ${y})`;
        drawGrid();
    }
    
    function setGoalPosition(x, y) {
        if (!gridMap || x < 0 || y < 0 || x >= gridMap.width || y >= gridMap.height) {
            return;
        }
        
        // 检查是否是障碍物
        for (let cell of gridMap.cells) {
            if (cell.x === x && cell.y === y && cell.is_obstacle) {
                alert('终点不能设置在障碍物上');
                return;
            }
        }
        
        goalPosition = { x, y };
        document.getElementById('goalPosition').textContent = `终点: (${x}, ${y})`;
        drawGrid();
    }
    
    async function createNewMap() {
        const width = parseInt(document.getElementById('mapWidth').value);
        const height = parseInt(document.getElementById('mapHeight').value);
        const mapType = document.getElementById('mapType').value;
        
        if (width <= 0 || height <= 0 || width > 200 || height > 200) {
            alert('地图尺寸无效，请输入1-200之间的值');
            return;
        }
        
        try {
            const response = await fetch('/grid/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    width: width,
                    height: height,
                    map_type: mapType
                }),
            });
            
            if (response.ok) {
                gridMap = await response.json();
                
                // 调整画布大小
                cellSize = Math.min(15, Math.min(800 / width, 600 / height));
                canvas.width = width * cellSize;
                canvas.height = height * cellSize;
                
                // 重置起点和终点
                startPosition = null;
                goalPosition = null;
                document.getElementById('startPosition').textContent = '起点: 未设置';
                document.getElementById('goalPosition').textContent = '终点: 未设置';
                
                // 清除路径
                clearPath();
                
                // 显示地形编辑工具
                if (mapType === 'complex' && currentTool !== 'select') {
                    document.getElementById('terrainTools').classList.remove('d-none');
                } else {
                    document.getElementById('terrainTools').classList.add('d-none');
                }
                
                drawGrid();
            }
        } catch (error) {
            console.error('创建地图失败:', error);
        }
    }
    
    async function clearMap() {
        try {
            const response = await fetch('/grid/clear', {
                method: 'POST'
            });
            
            if (response.ok) {
                // 重新获取地图数据
                const mapResponse = await fetch('/grid/current');
                if (mapResponse.ok) {
                    gridMap = await mapResponse.json();
                    clearPath();
                    drawGrid();
                }
            }
        } catch (error) {
            console.error('清空地图失败:', error);
        }
    }
    
    async function findPath() {
        if (!startPosition || !goalPosition) {
            alert('请先设置起点和终点');
            return;
        }
        
        const algorithm = document.getElementById('algorithm').value;
        const heuristic = document.getElementById('heuristic').value;
        const smoothPath = document.getElementById('smoothPath').checked;
        const checkCollision = document.getElementById('checkCollision').checked;
        
        try {
            const response = await fetch('/path/find', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_x: startPosition.x,
                    start_y: startPosition.y,
                    goal_x: goalPosition.x,
                    goal_y: goalPosition.y,
                    algorithm: algorithm,
                    heuristic: heuristic,
                    smooth: smoothPath,
                    check_collision: checkCollision
                }),
            });
            
            if (response.ok) {
                const result = await response.json();
                currentPath = result.path;
                exploredNodes = result.explored;
                
                // 更新统计信息
                const statsElem = document.getElementById('pathStats');
                if (result.path.length > 0) {
                    statsElem.innerHTML = `
                        <p>路径长度: ${result.path_length.toFixed(2)}</p>
                        <p>路径代价: ${result.path_cost.toFixed(2)}</p>
                        <p>探索节点数: ${result.nodes_explored}</p>
                        <p>计算时间: ${(result.computation_time * 1000).toFixed(2)} 毫秒</p>
                    `;
                } else {
                    statsElem.innerHTML = '<p>未找到路径!</p>';
                }
                
                drawGrid();
            } else {
                console.error('寻路请求失败:', await response.text());
                alert('寻路失败，请查看控制台了解详情');
            }
        } catch (error) {
            console.error('寻路失败:', error);
        }
    }
    
    function clearPath() {
        currentPath = null;
        exploredNodes = null;
        document.getElementById('pathStats').textContent = '尚未计算路径';
        drawGrid();
    }
    
    function drawGrid() {
        if (!gridMap) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 绘制网格
        for (let cell of gridMap.cells) {
            const x = cell.x * cellSize;
            const y = cell.y * cellSize;
            
            if (cell.is_obstacle) {
                ctx.fillStyle = 'black';
            } else if (gridMap.map_type === 'complex') {
                // 根据地形类型设置颜色
                switch (cell.terrain_type) {
                    case 1: // 山地
                        ctx.fillStyle = '#964B00';
                        break;
                    case 2: // 水域
                        ctx.fillStyle = '#3399FF';
                        break;
                    default: // 平地
                        ctx.fillStyle = 'white';
                }
            } else {
                ctx.fillStyle = 'white';
            }
            
            ctx.fillRect(x, y, cellSize, cellSize);
            ctx.strokeStyle = '#ccc';
            ctx.strokeRect(x, y, cellSize, cellSize);
        }
        
        // 绘制探索节点
        if (exploredNodes) {
            ctx.fillStyle = 'rgba(173, 216, 230, 0.5)';
            for (let node of exploredNodes) {
                ctx.beginPath();
                ctx.arc(node.x * cellSize + cellSize/2, node.y * cellSize + cellSize/2, cellSize/4, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        // 绘制路径
        if (currentPath && currentPath.length > 0) {
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(currentPath[0].x * cellSize + cellSize/2, currentPath[0].y * cellSize + cellSize/2);
            
            for (let i = 1; i < currentPath.length; i++) {
                ctx.lineTo(currentPath[i].x * cellSize + cellSize/2, currentPath[i].y * cellSize + cellSize/2);
            }
            
            ctx.stroke();
        }
        
        // 绘制起点和终点
        if (startPosition) {
            ctx.fillStyle = 'green';
            ctx.beginPath();
            ctx.arc(startPosition.x * cellSize + cellSize/2, startPosition.y * cellSize + cellSize/2, cellSize/2, 0, Math.PI * 2);
            ctx.fill();
        }
        
        if (goalPosition) {
            ctx.fillStyle = 'blue';
            ctx.beginPath();
            ctx.arc(goalPosition.x * cellSize + cellSize/2, goalPosition.y * cellSize + cellSize/2, cellSize/2, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}); 