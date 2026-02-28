"""
数据库连接和会话管理
Database Connection & Session Management
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from contextlib import contextmanager
from typing import Generator

from .base import Base

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bewithme.db")

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite 特殊配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # 生产环境设为False
    )
    
    # 启用外键约束（SQLite 默认关闭）
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL/MySQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库（创建所有表）"""
    # 导入所有模型以确保它们被注册
    from . import models  # noqa
    
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表已创建")


def drop_db():
    """删除所有表（谨慎使用！）"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  数据库表已删除")


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于 FastAPI 依赖注入）
    
    使用示例:
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于上下文管理器）
    
    使用示例:
    with get_db_session() as db:
        user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# 测试连接
def test_connection():
    """测试数据库连接"""
    try:
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    # 测试数据库连接并初始化
    print("🔧 初始化数据库...")
    test_connection()
    init_db()
    print("✅ 数据库初始化完成")
