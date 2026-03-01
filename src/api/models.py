"""
Pydantic 数据模型定义
API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ProfileRequest(BaseModel):
    """创建对话代理的请求模型"""
    name: str = Field(..., description="亲人姓名")
    relationship: str = Field(..., description="关系（如：奶奶、爷爷、妈妈）")
    personality_traits: str = Field(..., description="性格特征描述")
    speech_patterns: List[str] = Field(..., description="说话习惯列表")
    custom_prompt: Optional[str] = Field("", description="自定义系统提示词")
    voice_id: Optional[str] = Field(None, description="绑定的声音 ID")


class ChatRequest(BaseModel):
    """文字对话请求"""
    message: str = Field(..., description="用户消息")
    use_voice: bool = Field(False, description="是否使用语音响应")


class ChatResponse(BaseModel):
    """对话响应"""
    success: bool
    user_message: str
    agent_response: str
    is_safe: bool = True


class VoiceInfo(BaseModel):
    """音色信息（系统声音列表）"""
    model_config = {"from_attributes": True}
    
    voice_id: str
    name: str
    description: Optional[str] = None


class VoiceProfileResponse(BaseModel):
    """音色档案响应（数据库中的 voice profiles）"""
    model_config = {"from_attributes": True, "populate_by_name": True}
    
    id: int
    voice_id: str
    voice_name: str = Field(..., serialization_alias="name")  # 序列化时使用 name
    description: Optional[str] = None
    user_id: int
    relationship_id: int
    blockchain_minted: bool = False
    blockchain_tx_hash: Optional[str] = None
    ipfs_hash: Optional[str] = None


class SystemStatus(BaseModel):
    """系统状态"""
    agent_ready: bool
    voice_ready: bool
    agent_name: Optional[str] = None
    voice_id: Optional[str] = None


class CloneVoiceResponse(BaseModel):
    """音色克隆响应"""
    success: bool
    voice_id: str
    voice_name: str
    message: str
    analysis: Optional[dict] = None
    ipfs_hash: Optional[str] = None
    ipfs_gateway_url: Optional[str] = None


class CreateAgentResponse(BaseModel):
    """创建代理响应"""
    success: bool
    message: str
    profile: dict
