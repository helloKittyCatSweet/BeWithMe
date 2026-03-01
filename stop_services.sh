#!/bin/bash
#
# 停止前后端服务
# Stop Frontend & Backend Services
#

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  🛑 Be With Me - 停止服务${NC}"
echo -e "${BLUE}============================================${NC}"

STOPPED=0

# 停止后端
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "\n${YELLOW}⏳ 停止后端 (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        
        # 强制杀死
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        
        echo -e "${GREEN}✅ 后端已停止${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "\n${YELLOW}⚠️  后端进程不存在${NC}"
    fi
    rm -f logs/backend.pid
else
    echo -e "\n${YELLOW}⚠️  未找到后端 PID 文件${NC}"
fi

# 停止前端
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "\n${YELLOW}⏳ 停止前端 (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        
        # 强制杀死
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        
        echo -e "${GREEN}✅ 前端已停止${NC}"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "\n${YELLOW}⚠️  前端进程不存在${NC}"
    fi
    rm -f logs/frontend.pid
else
    echo -e "\n${YELLOW}⚠️  未找到前端 PID 文件${NC}"
fi

# 额外清理：查找可能残留的进程
echo -e "\n${BLUE}🔍 清理残留进程...${NC}"

# 清理 uvicorn 进程
UVICORN_PIDS=$(pgrep -f "uvicorn src.api.main:app" || true)
if [ -n "$UVICORN_PIDS" ]; then
    echo -e "${YELLOW}⏳ 发现残留的 uvicorn 进程${NC}"
    echo "$UVICORN_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ 已清理 uvicorn 进程${NC}"
    STOPPED=$((STOPPED + 1))
fi

# 清理 Vite 前端进程
VITE_PIDS=$(pgrep -f "vite.*--host 0.0.0.0.*--port 5173|npm run dev -- --host 0.0.0.0 --port 5173" || true)
if [ -n "$VITE_PIDS" ]; then
    echo -e "${YELLOW}⏳ 发现残留的 Vite 前端进程${NC}"
    echo "$VITE_PIDS" | xargs kill 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ 已清理 Vite 前端进程${NC}"
    STOPPED=$((STOPPED + 1))
fi

# 检查端口占用
echo -e "\n${BLUE}🔍 检查端口占用...${NC}"

PORT_8000=$(lsof -ti:8000 || true)
if [ -n "$PORT_8000" ]; then
    echo -e "${YELLOW}⚠️  端口 8000 仍被占用 (PID: $PORT_8000)${NC}"
    echo -e "${YELLOW}   手动清理: kill $PORT_8000${NC}"
fi

PORT_5173=$(lsof -ti:5173 || true)
if [ -n "$PORT_5173" ]; then
    echo -e "${YELLOW}⚠️  端口 5173 仍被占用 (PID: $PORT_5173)${NC}"
    echo -e "${YELLOW}   手动清理: kill $PORT_5173${NC}"
fi

# 总结
echo -e "\n${GREEN}============================================${NC}"
if [ $STOPPED -gt 0 ]; then
    echo -e "${GREEN}  ✅ 已停止 $STOPPED 个服务${NC}"
else
    echo -e "${YELLOW}  ℹ️  没有运行中的服务${NC}"
fi
echo -e "${GREEN}============================================${NC}"

# 提示重启
echo -e "\n${BLUE}💡 提示:${NC}"
echo -e "   重新启动: ${YELLOW}./start_services.sh${NC}"
echo -e "   查看状态: ${YELLOW}ps aux | grep -E 'uvicorn|vite'${NC}"
echo -e ""
