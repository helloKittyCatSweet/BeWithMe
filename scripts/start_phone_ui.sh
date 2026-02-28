#!/bin/bash
# Be With Me - 手机界面快速启动脚本
# Quick Start Script for Phone UI

echo "📱 Be With Me - 手机通话界面"
echo "===================================="
echo ""

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    echo "   cd /home/kitty/BeWithMe && ./scripts/start_phone_ui.sh"
    exit 1
fi

# 显示菜单
echo "请选择启动方式："
echo ""
echo "1) 基础版 (phone_call_ui.py) - 快速演示，无需后端"
echo "2) AI 集成版 (phone_call_ai.py) - 完整功能，需要后端"
echo "3) 同时启动后端和前端"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动基础版手机界面..."
        echo "📍 访问地址: http://localhost:8501"
        echo "⏹️  按 Ctrl+C 停止"
        echo ""
        streamlit run src/frontend/phone_call_ui.py
        ;;
    
    2)
        echo ""
        echo "🔍 检查依赖..."
        
        # 检查 audio-recorder-streamlit
        if ! python -c "import audio_recorder_streamlit" 2>/dev/null; then
            echo "❌ 缺少依赖: audio-recorder-streamlit"
            echo "   正在安装..."
            uv pip install audio-recorder-streamlit==0.0.8
        fi
        
        echo "✅ 依赖检查完成"
        echo ""
        echo "⚠️  注意：请确保后端 API 已启动 (端口 8000)"
        echo "   如果未启动，请在另一个终端运行："
        echo "   uvicorn src.api.main:app --reload"
        echo ""
        read -p "按回车键继续启动..."
        echo ""
        echo "🚀 启动 AI 集成版手机界面..."
        echo "📍 访问地址: http://localhost:8501"
        echo "⏹️  按 Ctrl+C 停止"
        echo ""
        streamlit run src/frontend/phone_call_ai.py
        ;;
    
    3)
        echo ""
        echo "🚀 同时启动后端和前端..."
        echo ""
        
        # 检查依赖
        echo "🔍 检查依赖..."
        if ! python -c "import audio_recorder_streamlit" 2>/dev/null; then
            echo "正在安装 audio-recorder-streamlit..."
            uv pip install audio-recorder-streamlit==0.0.8
        fi
        
        # 启动后端（后台）
        echo "🔧 启动后端 API (端口 8000)..."
        uvicorn src.api.main:app --reload --port 8000 > logs/api.log 2>&1 &
        API_PID=$!
        echo "   后端进程 PID: $API_PID"
        echo "   日志: logs/api.log"
        
        # 等待后端启动
        sleep 3
        
        # 启动前端
        echo ""
        echo "🎨 启动前端界面 (端口 8501)..."
        echo "📍 访问地址: http://localhost:8501"
        echo ""
        echo "⏹️  按 Ctrl+C 停止所有服务"
        echo ""
        
        # 捕获 Ctrl+C，同时停止后端
        trap "echo ''; echo '🛑 正在停止服务...'; kill $API_PID 2>/dev/null; exit" INT
        
        streamlit run src/frontend/phone_call_ai.py
        
        # 停止后端
        kill $API_PID 2>/dev/null
        ;;
    
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
