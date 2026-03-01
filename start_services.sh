#!/bin/bash
#
# 一键启动前后端服务
# Start Frontend & Backend Services
#

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

FRONTEND_DIR="src/vue-frontend"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  🎯 Be With Me - 启动服务${NC}"
echo -e "${BLUE}============================================${NC}"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在${NC}"
    echo -e "${YELLOW}请先运行: python -m venv .venv${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "\n${GREEN}✅ 激活虚拟环境...${NC}"
source .venv/bin/activate

# 检查环境变量
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env 文件不存在${NC}"
    echo -e "${YELLOW}请创建 .env 文件并配置 API Keys${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 环境变量已加载${NC}"

# 检查前端目录
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 前端目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 检查 npm
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}❌ 未检测到 npm，请先安装 Node.js (含 npm)${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 安装前端依赖（如缺失）
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "\n${BLUE}📦 安装前端依赖 (npm install)...${NC}"
    (
        cd "$FRONTEND_DIR"
        npm install > "$PROJECT_DIR/logs/frontend-install.log" 2>&1
    )
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
fi

# 启动后端
echo -e "\n${BLUE}📡 启动后端 (FastAPI)...${NC}"
uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --log-level info \
    > logs/backend.log 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✅ 后端启动中 (PID: $BACKEND_PID)${NC}"

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端就绪...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端已就绪！${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 后端启动超时${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# 启动前端
echo -e "\n${BLUE}🎨 启动前端 (Vue + Vite)...${NC}"
(
    cd "$FRONTEND_DIR"
    npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > "$PROJECT_DIR/logs/frontend.log" 2>&1
) &

FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端启动中 (PID: $FRONTEND_PID)${NC}"

# 等待前端启动
echo -e "${YELLOW}⏳ 等待前端就绪...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端已就绪！${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 前端启动超时${NC}"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
done

# 保存 PID
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

# 显示信息
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ 所有服务已启动！${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e ""
echo -e "${BLUE}🔗 访问地址:${NC}"
echo -e "   前端 (Vue):       ${YELLOW}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   后端 (FastAPI):   ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "   API 文档:         ${YELLOW}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e ""
echo -e "${BLUE}📊 日志文件:${NC}"
echo -e "   后端: logs/backend.log"
echo -e "   前端: logs/frontend.log"
echo -e ""
echo -e "${BLUE}🛑 停止服务:${NC}"
echo -e "   ${YELLOW}./stop_services.sh${NC}"
echo -e ""
echo -e "${BLUE}🔧 实时日志:${NC}"
echo -e "   ${YELLOW}tail -f logs/backend.log${NC}"
echo -e "   ${YELLOW}tail -f logs/frontend.log${NC}"
echo -e ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  🎉 准备就绪！开始使用吧！${NC}"
echo -e "${GREEN}============================================${NC}"

# 保持脚本运行
echo -e "\n${YELLOW}按 Ctrl+C 停止所有服务${NC}\n"

# 捕获退出信号
trap "echo -e '\n${YELLOW}⏳ 正在停止服务...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; echo -e '${GREEN}✅ 所有服务已停止${NC}'; exit 0" INT TERM

# 等待进程
wait
