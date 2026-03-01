"""
数据库迁移脚本：添加 IPFS 字段到 voice_profiles 表
Add IPFS fields to voice_profiles table
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.connection import engine
from sqlalchemy import text


def upgrade():
    """添加 IPFS 字段到 voice_profiles 表"""
    print("Adding IPFS fields to voice_profiles table...")
    
    with engine.connect() as conn:
        # 添加 ipfs_hash 字段
        try:
            conn.execute(text("""
                ALTER TABLE voice_profiles 
                ADD COLUMN ipfs_hash VARCHAR(200);
            """))
            print("✅ Added ipfs_hash column")
        except Exception as e:
            print(f"⚠️ ipfs_hash column may already exist: {e}")
        
        # 添加 ipfs_gateway_url 字段
        try:
            conn.execute(text("""
                ALTER TABLE voice_profiles 
                ADD COLUMN ipfs_gateway_url VARCHAR(500);
            """))
            print("✅ Added ipfs_gateway_url column")
        except Exception as e:
            print(f"⚠️ ipfs_gateway_url column may already exist: {e}")
        
        # 添加 ipfs_uploaded_at 字段
        try:
            conn.execute(text("""
                ALTER TABLE voice_profiles 
                ADD COLUMN ipfs_uploaded_at TIMESTAMP;
            """))
            print("✅ Added ipfs_uploaded_at column")
        except Exception as e:
            print(f"⚠️ ipfs_uploaded_at column may already exist: {e}")
        
        conn.commit()
    
    print("✅ Migration completed successfully")


def downgrade():
    """移除 IPFS 字段"""
    print("Removing IPFS fields from voice_profiles table...")
    
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE voice_profiles 
                DROP COLUMN IF EXISTS ipfs_hash,
                DROP COLUMN IF EXISTS ipfs_gateway_url,
                DROP COLUMN IF EXISTS ipfs_uploaded_at;
            """))
            conn.commit()
            print("✅ IPFS fields removed")
        except Exception as e:
            print(f"❌ Error removing fields: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration for IPFS fields in voice_profiles')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], help='Migration action')
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    else:
        downgrade()
