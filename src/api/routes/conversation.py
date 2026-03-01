"""
对话相关的 API 路由
Conversation Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
from typing import Optional
from pydantic import BaseModel

from ...core.conversation import ConversationAgent, create_custom_agent
from ..models import ProfileRequest, CreateAgentResponse, ChatRequest, ChatResponse
from ...database import (
    get_db, 
    log_action, 
    get_agent_profile,
    get_user_agent_profiles
)
from ..auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])

# 全局对话代理（会话存储）
current_agent: Optional[ConversationAgent] = None


@router.post("/create", response_model=CreateAgentResponse)
async def create_agent(profile: ProfileRequest):
    """
    创建对话代理
    
    - **name**: 亲人姓名
    - **relationship**: 关系（如：奶奶、爷爷、妈妈）
    - **personality_traits**: 性格特征描述
    - **speech_patterns**: 说话习惯列表
    - **voice_id**: 绑定的声音 ID（可选）
    """
    global current_agent
    
    try:
        agent = create_custom_agent(
            name=profile.name,
            relationship=profile.relationship,
            traits=profile.personality_traits,
            patterns=profile.speech_patterns
        )
        
        # Store voice_id if provided
        if profile.voice_id:
            agent.voice_id = profile.voice_id
        
        current_agent = agent
        
        # 同时设置到 chat 路由中
        from . import chat
        chat.current_agent = agent
        if profile.voice_id:
            chat.current_voice_id = profile.voice_id
        
        return CreateAgentResponse(
            success=True,
            message=f"对话代理 '{profile.name}' 创建成功！",
            profile={
                "name": profile.name,
                "relationship": profile.relationship,
                "personality": profile.personality_traits,
                "voice_id": profile.voice_id,
            }
        )
        
    except Exception as e:
        logger.error(f"创建代理时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_agent():
    """重置当前对话代理"""
    global current_agent
    current_agent = None
    return {"success": True, "message": "对话代理已重置"}


@router.get("/current")
async def get_current_agent():
    """获取当前对话代理信息"""
    global current_agent
    
    if not current_agent:
        raise HTTPException(status_code=400, detail="未创建对话代理")
    
    return {
        "success": True,
        "name": current_agent.profile.name,
        "relationship": current_agent.profile.relationship,
        "personality": current_agent.profile.personality_traits,
        "speech_patterns": current_agent.profile.speech_patterns
    }


# 注意：区块链保存功能已移至前端，前端直接调用智能合约