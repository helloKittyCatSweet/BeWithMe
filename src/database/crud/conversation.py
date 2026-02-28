"""
对话记录管理 CRUD 操作
Conversation Management CRUD Operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..models import Conversation


def create_conversation(
    db: Session,
    user_id: int,
    user_message: str,
    agent_response: str,
    voice_profile_id: Optional[int] = None,
    agent_profile_id: Optional[int] = None,
    is_voice_input: bool = False,
    is_voice_output: bool = False,
    input_audio_path: Optional[str] = None,
    output_audio_path: Optional[str] = None,
    asr_latency: Optional[int] = None,
    llm_latency: Optional[int] = None,
    tts_latency: Optional[int] = None
) -> Conversation:
    """记录对话"""
    total_latency = sum(filter(None, [asr_latency, llm_latency, tts_latency]))
    
    conversation = Conversation(
        user_id=user_id,
        voice_profile_id=voice_profile_id,
        agent_profile_id=agent_profile_id,
        user_message=user_message,
        agent_response=agent_response,
        is_voice_input=is_voice_input,
        is_voice_output=is_voice_output,
        input_audio_path=input_audio_path,
        output_audio_path=output_audio_path,
        asr_latency=asr_latency,
        llm_latency=llm_latency,
        tts_latency=tts_latency,
        total_latency=total_latency
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    """根据 ID 获取对话"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_user_conversations(
    db: Session, 
    user_id: int, 
    limit: int = 50,
    offset: int = 0
) -> List[Conversation]:
    """获取用户的对话历史"""
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(
        Conversation.created_at.desc()
    ).limit(limit).offset(offset).all()


def get_conversation_stats(db: Session, user_id: int) -> dict:
    """获取用户的对话统计"""
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == user_id
    ).scalar()
    
    voice_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == user_id,
        Conversation.is_voice_output == True
    ).scalar()
    
    avg_latency = db.query(func.avg(Conversation.total_latency)).filter(
        Conversation.user_id == user_id
    ).scalar()
    
    return {
        "total_conversations": total_conversations or 0,
        "voice_conversations": voice_conversations or 0,
        "text_conversations": (total_conversations or 0) - (voice_conversations or 0),
        "average_latency_ms": int(avg_latency) if avg_latency else 0
    }


def delete_user_conversations(db: Session, user_id: int) -> int:
    """删除用户的所有对话记录"""
    count = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).delete()
    db.commit()
    return count
