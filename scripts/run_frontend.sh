#!/bin/bash
# 前端启动脚本

echo "🎙️  Echoes of Kin - 前端应用"
echo "=================================="

# 激活虚拟环境
source .venv/bin/activate

# 启动前端
echo "启动 Streamlit 应用..."
cd "$(dirname "$0")" 
streamlit run src/frontend/app.py
