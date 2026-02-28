"""
用户管理 CRUD 操作
User Management CRUD Operations
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import hashlib

from ..models import User


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    phone: Optional[str] = None
) -> User:
    """创建新用户"""
    # 密码哈希（实际应用中使用 bcrypt/argon2）
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone=phone
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def verify_user_password(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户密码"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.password_hash == password_hash:
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        return user
    
    return None


def update_user(
    db: Session,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """更新用户信息"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True
