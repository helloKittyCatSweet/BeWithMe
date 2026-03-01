"""
代理档案管理 CRUD 操作
Agent Profile Management CRUD Operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models import AgentProfile


def create_agent_profile(
    db: Session,
    user_id: int,
    name: str,
    relationship: str,
    personality_traits: str,
    speech_patterns: Optional[List[str]] = None,
    background_story: Optional[str] = None,
    memories: Optional[List[str]] = None
) -> AgentProfile:
    """创建代理档案"""
    agent_profile = AgentProfile(
        user_id=user_id,
        name=name,
        relationship=relationship,
        personality_traits=personality_traits,
        speech_patterns=speech_patterns or [],
        background_story=background_story,
        memories=memories or []
    )
    
    db.add(agent_profile)
    db.commit()
    db.refresh(agent_profile)
    
    return agent_profile


def get_agent_profile_by_id(db: Session, profile_id: int) -> Optional[AgentProfile]:
    """根据 ID 获取代理档案"""
    return db.query(AgentProfile).filter(AgentProfile.id == profile_id).first()


def get_agent_profile(
    db: Session, 
    user_id: int
) -> Optional[AgentProfile]:
    """获取用户的代理档案"""
    return db.query(AgentProfile).filter(AgentProfile.user_id == user_id).first()


def get_user_agent_profiles(
    db: Session, 
    user_id: int,
    active_only: bool = True
) -> List[AgentProfile]:
    """获取用户的所有代理档案"""
    query = db.query(AgentProfile).filter(AgentProfile.user_id == user_id)
    
    if active_only:
        query = query.filter(AgentProfile.is_active == True)
    
    return query.all()


def update_agent_profile(
    db: Session,
    profile_id: int,
    **kwargs
) -> Optional[AgentProfile]:
    """更新代理档案"""
    agent = get_agent_profile_by_id(db, profile_id)
    
    if not agent:
        return None
    
    # 只更新提供的字段
    for key, value in kwargs.items():
        if hasattr(agent, key):
            setattr(agent, key, value)
    
    db.commit()
    db.refresh(agent)
    
    return agent


def deactivate_agent_profile(db: Session, profile_id: int) -> bool:
    """停用代理档案"""
    agent = get_agent_profile_by_id(db, profile_id)
    
    if not agent:
        return False
    
    agent.is_active = False
    db.commit()
    
    return True


def delete_agent_profile(db: Session, profile_id: int) -> bool:
    """删除代理档案"""
    agent = get_agent_profile_by_id(db, profile_id)
    
    if not agent:
        return False
    
    db.delete(agent)
    db.commit()
    
    return True
