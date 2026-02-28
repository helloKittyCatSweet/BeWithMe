"""
数据库 CRUD 操作模块
Database CRUD Operations Module
"""
# 用户管理
from .user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    verify_user_password,
    update_user,
    delete_user,
)

# 关系管理
from .relationship import (
    create_relationship,
    get_relationship_by_id,
    get_user_relationships,
    get_pending_verifications,
    approve_relationship,
    reject_relationship,
    check_relationship_valid,
    delete_relationship,
)

# 音色档案管理
from .voice_profile import (
    create_voice_profile,
    get_voice_profile_by_id,
    get_voice_profile_by_voice_id,
    get_user_voice_profiles,
    increment_voice_usage,
    deactivate_voice_profile,
    delete_voice_profile,
)

# 对话记录管理
from .conversation import (
    create_conversation,
    get_conversation_by_id,
    get_user_conversations,
    get_conversation_stats,
    delete_user_conversations,
)

# 审计日志
from .audit import (
    log_action,
    get_user_audit_logs,
    get_audit_logs_by_action,
    get_failed_audit_logs,
)

# 统计查询
from .stats import (
    get_system_stats,
    get_user_summary,
)

__all__ = [
    # User
    "create_user",
    "get_user_by_id",
    "get_user_by_username",
    "get_user_by_email",
    "verify_user_password",
    "update_user",
    "delete_user",
    
    # Relationship
    "create_relationship",
    "get_relationship_by_id",
    "get_user_relationships",
    "get_pending_verifications",
    "approve_relationship",
    "reject_relationship",
    "check_relationship_valid",
    "delete_relationship",
    
    # Voice Profile
    "create_voice_profile",
    "get_voice_profile_by_id",
    "get_voice_profile_by_voice_id",
    "get_user_voice_profiles",
    "increment_voice_usage",
    "deactivate_voice_profile",
    "delete_voice_profile",
    
    # Conversation
    "create_conversation",
    "get_conversation_by_id",
    "get_user_conversations",
    "get_conversation_stats",
    "delete_user_conversations",
    
    # Audit
    "log_action",
    "get_user_audit_logs",
    "get_audit_logs_by_action",
    "get_failed_audit_logs",
    
    # Stats
    "get_system_stats",
    "get_user_summary",
]
