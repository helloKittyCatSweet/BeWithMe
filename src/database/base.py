"""
数据库基础配置
Database Base Configuration
"""
from sqlalchemy.ext.declarative import declarative_base
import enum

# SQLAlchemy Base
Base = declarative_base()


# ============ 枚举类型 ============

class RelationshipType(enum.Enum):
    """亲属关系类型"""
    PARENT = "parent"  # 父母
    GRANDPARENT = "grandparent"  # 祖父母/外祖父母
    SIBLING = "sibling"  # 兄弟姐妹
    CHILD = "child"  # 子女
    SPOUSE = "spouse"  # 配偶
    OTHER = "other"  # 其他


class VerificationStatus(enum.Enum):
    """验证状态"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期
