"""
数据库模块 - Database Module
"""
# 基础配置
from .base import Base, RelationshipType, VerificationStatus

# 模型
from .models import (
    User,
    Relationship,
    VoiceProfile,
    AgentProfile,
    Conversation,
    AuditLog,
    SystemConfig,
    VerificationDocument,
)

# 连接管理
from .connection import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    init_db,
    drop_db,
    test_connection
)

# CRUD 操作
from .crud import (
    # User
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    verify_user_password,
    update_user,
    delete_user,
    
    # Relationship
    create_relationship,
    get_relationship_by_id,
    get_user_relationships,
    get_pending_verifications,
    approve_relationship,
    reject_relationship,
    check_relationship_valid,
    delete_relationship,
    
    # Voice Profile
    create_voice_profile,
    get_voice_profile_by_id,
    get_voice_profile_by_voice_id,
    get_user_voice_profiles,
    increment_voice_usage,
    deactivate_voice_profile,
    delete_voice_profile,
    
    # Agent Profile
    create_agent_profile,
    get_agent_profile_by_id,
    get_agent_profile,
    get_user_agent_profiles,
    update_agent_profile,
    deactivate_agent_profile,
    delete_agent_profile,
    
    # Conversation
    create_conversation,
    get_conversation_by_id,
    get_user_conversations,
    get_conversation_stats,
    delete_user_conversations,
    
    # Audit
    log_action,
    get_user_audit_logs,
    get_audit_logs_by_action,
    get_failed_audit_logs,
    
    # Stats
    get_system_stats,
    get_user_summary,
    
    # Verification Document
    create_verification_document,
    get_document_by_id,
    get_documents_by_relationship,
    get_documents_by_user,
    delete_document,
    get_document_stats,
)

__all__ = [
    # Base
    "Base",
    "RelationshipType",
    "VerificationStatus",
    
    # Models
    "User",
    "Relationship",
    "VoiceProfile",
    "AgentProfile",
    "Conversation",
    "AuditLog",
    "SystemConfig",
    "VerificationDocument",
    
    # Connection
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "init_db",
    "drop_db",
    "test_connection",
    
    # CRUD - User
    "create_user",
    "get_user_by_id",
    "get_user_by_username",
    "get_user_by_email",
    "verify_user_password",
    "update_user",
    "delete_user",
    
    # CRUD - Relationship
    "create_relationship",
    "get_relationship_by_id",
    "get_user_relationships",
    "get_pending_verifications",
    "approve_relationship",
    "reject_relationship",
    "check_relationship_valid",
    "delete_relationship",
    
    # CRUD - Voice Profile
    "create_voice_profile",
    "get_voice_profile_by_id",
    "get_voice_profile_by_voice_id",
    "get_user_voice_profiles",
    "increment_voice_usage",
    "deactivate_voice_profile",
    "delete_voice_profile",
    
    # CRUD - Agent Profile
    "create_agent_profile",
    "get_agent_profile_by_id",
    "get_agent_profile",
    "get_user_agent_profiles",
    "update_agent_profile",
    "deactivate_agent_profile",
    "delete_agent_profile",
    
    # CRUD - Conversation
    "create_conversation",
    "get_conversation_by_id",
    "get_user_conversations",
    "get_conversation_stats",
    "delete_user_conversations",
    
    # CRUD - Audit
    "log_action",
    "get_user_audit_logs",
    "get_audit_logs_by_action",
    "get_failed_audit_logs",
    
    # CRUD - Stats
    "get_system_stats",
    "get_user_summary",
    
    # CRUD - Verification Document
    "create_verification_document",
    "get_document_by_id",
    "get_documents_by_relationship",
    "get_documents_by_user",
    "delete_document",
    "get_document_stats",
]
