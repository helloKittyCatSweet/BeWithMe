"""
审计日志 CRUD 操作
Audit Log CRUD Operations
"""
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models import AuditLog


def log_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None
):
    """记录审计日志"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message
    )
    
    db.add(log)
    db.commit()


def get_user_audit_logs(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[AuditLog]:
    """获取用户的审计日志"""
    return db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).offset(offset).all()


def get_audit_logs_by_action(
    db: Session,
    action: str,
    limit: int = 100
) -> List[AuditLog]:
    """根据操作类型获取审计日志"""
    return db.query(AuditLog).filter(
        AuditLog.action == action
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).all()


def get_failed_audit_logs(
    db: Session,
    limit: int = 100
) -> List[AuditLog]:
    """获取失败的操作日志"""
    return db.query(AuditLog).filter(
        AuditLog.success == False
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).all()
