#!/bin/bash
# 后端启动脚本

echo "🎙️  Echoes of Kin - 后端服务"
echo "=================================="

# 激活虚拟环境
source .venv/bin/activate

# 启动后端
echo "启动 FastAPI 服务..."
cd "$(dirname "$0")"
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
