"""
亲属关系管理 CRUD 操作
Relationship Management CRUD Operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..models import Relationship
from ..base import RelationshipType, VerificationStatus


def create_relationship(
    db: Session,
    user_id: int,
    relative_name: str,
    relationship_type: RelationshipType,
    purpose: str,
    birth_date: Optional[datetime] = None,
    death_date: Optional[datetime] = None,
    verification_document: Optional[str] = None,
    additional_info: Optional[str] = None
) -> Relationship:
    """创建亲属关系申请"""
    is_deceased = death_date is not None
    
    relationship = Relationship(
        user_id=user_id,
        relative_name=relative_name,
        relationship_type=relationship_type,
        birth_date=birth_date,
        death_date=death_date,
        is_deceased=is_deceased,
        purpose=purpose,
        verification_document=verification_document,
        additional_info=additional_info,
        verification_status=VerificationStatus.PENDING
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    return relationship


def get_relationship_by_id(db: Session, relationship_id: int) -> Optional[Relationship]:
    """根据 ID 获取关系"""
    return db.query(Relationship).filter(Relationship.id == relationship_id).first()


def get_user_relationships(
    db: Session, 
    user_id: int, 
    status: Optional[VerificationStatus] = None
) -> List[Relationship]:
    """获取用户的所有亲属关系"""
    query = db.query(Relationship).filter(Relationship.user_id == user_id)
    
    if status:
        query = query.filter(Relationship.verification_status == status)
    
    return query.order_by(Relationship.created_at.desc()).all()


def get_pending_verifications(db: Session) -> List[Relationship]:
    """获取所有待审核的关系"""
    return db.query(Relationship).filter(
        Relationship.verification_status == VerificationStatus.PENDING
    ).order_by(Relationship.created_at.asc()).all()


def approve_relationship(
    db: Session,
    relationship_id: int,
    reviewer: str,
    notes: Optional[str] = None,
    expires_in_days: int = 365
) -> Relationship:
    """审核通过亲属关系"""
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise ValueError("关系不存在")
    
    relationship.verification_status = VerificationStatus.APPROVED
    relationship.verified_at = datetime.utcnow()
    relationship.verified_by = reviewer
    relationship.reviewer_notes = notes
    relationship.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    db.commit()
    db.refresh(relationship)
    
    return relationship


def reject_relationship(
    db: Session,
    relationship_id: int,
    reviewer: str,
    reason: str
) -> Relationship:
    """审核拒绝亲属关系"""
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        raise ValueError("关系不存在")
    
    relationship.verification_status = VerificationStatus.REJECTED
    relationship.verified_at = datetime.utcnow()
    relationship.verified_by = reviewer
    relationship.reviewer_notes = reason
    
    db.commit()
    db.refresh(relationship)
    
    return relationship


def check_relationship_valid(db: Session, relationship_id: int) -> bool:
    """检查关系是否有效（已审核且未过期）"""
    relationship = get_relationship_by_id(db, relationship_id)
    
    if not relationship:
        return False
    
    if relationship.verification_status != VerificationStatus.APPROVED:
        return False
    
    if relationship.expires_at and relationship.expires_at < datetime.utcnow():
        # 标记为过期
        relationship.verification_status = VerificationStatus.EXPIRED
        db.commit()
        return False
    
    return True


def delete_relationship(db: Session, relationship_id: int) -> bool:
    """删除关系记录"""
    relationship = get_relationship_by_id(db, relationship_id)
    if not relationship:
        return False
    
    db.delete(relationship)
    db.commit()
    return True
