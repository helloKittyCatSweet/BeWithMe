"""
统计查询 CRUD 操作
Statistics Query Operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import User, Relationship, VoiceProfile, Conversation
from ..base import VerificationStatus


def get_system_stats(db: Session) -> dict:
    """获取系统统计信息"""
    total_users = db.query(func.count(User.id)).scalar()
    total_relationships = db.query(func.count(Relationship.id)).scalar()
    
    approved_relationships = db.query(func.count(Relationship.id)).filter(
        Relationship.verification_status == VerificationStatus.APPROVED
    ).scalar()
    
    pending_relationships = db.query(func.count(Relationship.id)).filter(
        Relationship.verification_status == VerificationStatus.PENDING
    ).scalar()
    
    total_voice_profiles = db.query(func.count(VoiceProfile.id)).scalar()
    active_voice_profiles = db.query(func.count(VoiceProfile.id)).filter(
        VoiceProfile.is_active == True
    ).scalar()
    
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    voice_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.is_voice_output == True
    ).scalar()
    
    return {
        "total_users": total_users or 0,
        "total_relationships": total_relationships or 0,
        "approved_relationships": approved_relationships or 0,
        "pending_relationships": pending_relationships or 0,
        "total_voice_profiles": total_voice_profiles or 0,
        "active_voice_profiles": active_voice_profiles or 0,
        "total_conversations": total_conversations or 0,
        "voice_conversations": voice_conversations or 0,
        "text_conversations": (total_conversations or 0) - (voice_conversations or 0)
    }


def get_user_summary(db: Session, user_id: int) -> dict:
    """获取用户统计摘要"""
    relationships_count = db.query(func.count(Relationship.id)).filter(
        Relationship.user_id == user_id
    ).scalar()
    
    approved_relationships_count = db.query(func.count(Relationship.id)).filter(
        Relationship.user_id == user_id,
        Relationship.verification_status == VerificationStatus.APPROVED
    ).scalar()
    
    voice_profiles_count = db.query(func.count(VoiceProfile.id)).filter(
        VoiceProfile.user_id == user_id
    ).scalar()
    
    conversations_count = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == user_id
    ).scalar()
    
    return {
        "user_id": user_id,
        "total_relationships": relationships_count or 0,
        "approved_relationships": approved_relationships_count or 0,
        "voice_profiles": voice_profiles_count or 0,
        "conversations": conversations_count or 0
    }
