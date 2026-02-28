"""
主应用入口 - FastAPI
Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .routes import voice, conversation, chat
from .models import SystemStatus
from ..config import API_HOST, API_PORT

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Echoes of Kin API",
    description="亲人模拟通话 Agent API",
    version="1.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(voice.router)
app.include_router(conversation.router)
app.include_router(chat.router)


# ============ 系统端点 ============

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "Echoes of Kin",
        "message": "亲情回响 - 让思念有声"
    }


@app.get("/status", response_model=SystemStatus)
async def get_status():
    """获取系统状态"""
    agent_ready = conversation.current_agent is not None
    voice_ready = chat.current_voice_id is not None
    
    return SystemStatus(
        agent_ready=agent_ready,
        voice_ready=voice_ready,
        agent_name=conversation.current_agent.profile.name if agent_ready else None,
        voice_id=chat.current_voice_id
    )


@app.get("/health")
async def health_check():
    """健康检查（简单版）"""
    return {"status": "healthy"}


# ============ 错误处理 ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """自定义 HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误"
        }
    )


# ============ 启动函数 ============

def main():
    """运行应用"""
    import uvicorn
    
    print("""
╔════════════════════════════════════════╗
║  🎙️  Echoes of Kin API Server      ║
║  亲情回响 - 让思念有声              ║
╚════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
