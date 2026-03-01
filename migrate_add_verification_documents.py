"""
数据库迁移脚本：添加 verification_documents 表
Add verification_documents table for multiple document uploads
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.connection import engine
from src.database.base import Base
from src.database.models.verification_document import VerificationDocument


def upgrade():
    """创建 verification_documents 表"""
    print("Creating verification_documents table...")
    
    # 导入所有模型以确保关系正确建立
    from src.database.models import (
        User, Relationship, VoiceProfile, AgentProfile, 
        Conversation, AuditLog, SystemConfig
    )
    
    # 只创建 verification_documents 表
    VerificationDocument.__table__.create(engine, checkfirst=True)
    print("✅ Successfully created verification_documents table")


def downgrade():
    """删除 verification_documents 表"""
    print("Dropping verification_documents table...")
    VerificationDocument.__table__.drop(engine, checkfirst=True)
    print("✅ Successfully dropped verification_documents table")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for verification_documents table')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], help='Migration action')
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    else:
        downgrade()
