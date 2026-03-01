"""
主应用入口 - FastAPI
Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .routes import voice, conversation, chat, relationships
from .routes import auth
from .models import SystemStatus
from ..config import API_HOST, API_PORT
from ..database import init_db, test_connection, get_system_stats, get_db_session

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Be With Me API",
    description="AI 语音克隆对话系统 - 陪伴从心开始",
    version="2.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 应用生命周期 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("初始化数据库...")
    try:
        init_db()
        if test_connection():
            logger.info("✅ 数据库连接成功")
        else:
            logger.warning("⚠️ 数据库连接失败")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("关闭应用...")


# 包含路由
app.include_router(voice.router)
app.include_router(conversation.router)
app.include_router(chat.router)
app.include_router(relationships.router, prefix="/relationships", tags=["relationships"])
app.include_router(auth.router)

# 注意：区块链功能由前端直接通过 ethers.js/web3.js 调用智能合约


# ============ 系统端点 ============

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "Be With Me",
        "message": "陪伴从心开始 - AI 语音克隆对话系统",
        "version": "2.0.0"
    }


@app.get("/status")
async def get_status():
    """获取系统状态"""
    agent_ready = conversation.current_agent is not None
    voice_ready = chat.current_voice_id is not None
    db_connected = test_connection()
    
    # 获取数据库统计
    db_stats = None
    if db_connected:
        try:
            with get_db_session() as db:
                db_stats = get_system_stats(db)
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
    
    return {
        "agent_ready": agent_ready,
        "voice_ready": voice_ready,
        "database_connected": db_connected,
        "agent_name": conversation.current_agent.profile.name if agent_ready else None,
        "voice_id": chat.current_voice_id,
        "database_stats": db_stats
    }


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
║  🎙️  Be With Me API Server         ║
║  陪伴从心开始 - AI 语音克隆对话    ║
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
