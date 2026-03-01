#!/usr/bin/env python3
"""
数据库初始化脚本
Initialize Database Script
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import (
    init_db, 
    drop_db, 
    test_connection,
    create_user,
    get_db_session
)

def main():
    """初始化数据库"""
    print("=" * 60)
    print("📦 Be With Me - Database Initialization")
    print("=" * 60)
    
    # 测试连接
    print("\n1️⃣ Testing database connection...")
    if test_connection():
        print("   ✅ Database connection successful")
    else:
        print("   ❌ Database connection failed")
        return
    
    # 询问是否重新创建表
    print("\n2️⃣ Initialize database tables")
    choice = input("   Do you want to DROP existing tables and recreate? (yes/no): ").strip().lower()
    
    if choice == "yes":
        print("   🗑️  Dropping existing tables...")
        drop_db()
        print("   ✅ Tables dropped")
    
    # 创建表
    print("   🔨 Creating tables...")
    init_db()
    print("   ✅ Tables created successfully")
    
    # 创建测试用户
    print("\n3️⃣ Create demo user")
    create_demo = input("   Create a demo user? (yes/no): ").strip().lower()
    
    if create_demo == "yes":
        try:
            with get_db_session() as db:
                # 检查用户是否已存在
                from src.database import get_user_by_username
                existing_user = get_user_by_username(db, "demo_user")
                
                if existing_user:
                    print("   ℹ️  Demo user already exists")
                else:
                    demo_user = create_user(
                        db=db,
                        username="demo_user",
                        email="demo@bewithme.ai",
                        password="demo123",
                        full_name="Demo User",
                        phone="1234567890"
                    )
                    print(f"   ✅ Demo user created: ID={demo_user.id}, username={demo_user.username}")
                    print(f"   📝 Login credentials: demo_user / demo123")
        except Exception as e:
            print(f"   ❌ Failed to create demo user: {e}")
    
    # 创建管理员用户
    print("\n4️⃣ Create admin user")
    create_admin = input("   Create an admin user? (yes/no): ").strip().lower()
    
    if create_admin == "yes":
        try:
            with get_db_session() as db:
                from src.database import get_user_by_email
                existing_admin = get_user_by_email(db, "admin@bewithme.ai")
                
                if existing_admin:
                    print("   ℹ️  Admin user already exists")
                else:
                    admin_user = create_user(
                        db=db,
                        username="admin",
                        email="admin@bewithme.ai",
                        password="admin123",
                        full_name="System Administrator",
                        phone=None,
                        is_admin=True
                    )
                    print(f"   ✅ Admin user created: ID={admin_user.id}, username={admin_user.username}")
                    print(f"   📝 Login credentials: admin@bewithme.ai / admin123")
                    print(f"   🔐 Admin privileges: ENABLED")
        except Exception as e:
            print(f"   ❌ Failed to create admin user: {e}")
    
    # 显示数据库统计
    print("\n5️⃣ Database Statistics")
    try:
        with get_db_session() as db:
            from src.database import get_system_stats
            stats = get_system_stats(db)
            print(f"   Users: {stats['total_users']}")
            print(f"   Relationships: {stats['total_relationships']}")
            print(f"   Voice Profiles: {stats['total_voice_profiles']}")
            print(f"   Conversations: {stats['total_conversations']}")
    except Exception as e:
        print(f"   ❌ Failed to get statistics: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Start the backend: ./start_services.sh")
    print("   2. Open the frontend: http://localhost:8501")
    print("   3. Register family relationships in the 'Family Verification' tab")
    print()


if __name__ == "__main__":
    main()
