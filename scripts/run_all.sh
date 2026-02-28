#!/bin/bash
# 同时启动后端和前端

echo "🎙️  Echoes of Kin - 完整启动"
echo "=================================="

source .venv/bin/activate

# 启动后端
echo "启动后端服务..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

# 启动前端
echo "启动前端应用..."
streamlit run src/frontend/app.py

# 清理
wait $BACKEND_PID
