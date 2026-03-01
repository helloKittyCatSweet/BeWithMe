"""
音色档案管理 CRUD 操作
Voice Profile Management CRUD Operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from ..models import VoiceProfile
from .relationship import check_relationship_valid


def create_voice_profile(
    db: Session,
    user_id: int,
    relationship_id: int,
    voice_id: str,
    voice_name: str,
    description: Optional[str] = None,
    source_audio_path: Optional[str] = None,
    audio_duration: Optional[int] = None,
    ipfs_hash: Optional[str] = None,
    ipfs_gateway_url: Optional[str] = None,
    ipfs_uploaded_at: Optional[datetime] = None
) -> VoiceProfile:
    """创建音色档案（需要验证关系）"""
    # 验证关系有效性
    if not check_relationship_valid(db, relationship_id):
        raise ValueError("亲属关系未通过验证或已过期")
    
    voice_profile = VoiceProfile(
        user_id=user_id,
        relationship_id=relationship_id,
        voice_id=voice_id,
        voice_name=voice_name,
        description=description,
        source_audio_path=source_audio_path,
        audio_duration=audio_duration,
        ipfs_hash=ipfs_hash,
        ipfs_gateway_url=ipfs_gateway_url,
        ipfs_uploaded_at=ipfs_uploaded_at
    )
    
    db.add(voice_profile)
    db.commit()
    db.refresh(voice_profile)
    
    return voice_profile


def get_voice_profile_by_id(db: Session, profile_id: int) -> Optional[VoiceProfile]:
    """根据 ID 获取音色档案"""
    return db.query(VoiceProfile).filter(VoiceProfile.id == profile_id).first()


def get_voice_profile_by_voice_id(db: Session, voice_id: str) -> Optional[VoiceProfile]:
    """根据 ElevenLabs voice_id 获取档案"""
    return db.query(VoiceProfile).filter(VoiceProfile.voice_id == voice_id).first()


def get_user_voice_profiles(
    db: Session, 
    user_id: int,
    active_only: bool = True
) -> List[VoiceProfile]:
    """获取用户的所有音色档案"""
    query = db.query(VoiceProfile).filter(VoiceProfile.user_id == user_id)
    
    if active_only:
        query = query.filter(VoiceProfile.is_active == True)
    
    return query.order_by(VoiceProfile.created_at.desc()).all()


def increment_voice_usage(db: Session, voice_profile_id: int):
    """增加音色使用次数"""
    voice_profile = get_voice_profile_by_id(db, voice_profile_id)
    if voice_profile:
        voice_profile.usage_count += 1
        voice_profile.last_used_at = datetime.utcnow()
        db.commit()


def deactivate_voice_profile(db: Session, profile_id: int) -> bool:
    """停用音色档案"""
    voice_profile = get_voice_profile_by_id(db, profile_id)
    if not voice_profile:
        return False
    
    voice_profile.is_active = False
    db.commit()
    return True


def delete_voice_profile(db: Session, profile_id: int) -> bool:
    """删除音色档案"""
    voice_profile = get_voice_profile_by_id(db, profile_id)
    if not voice_profile:
        return False
    
    db.delete(voice_profile)
    db.commit()
    return True
