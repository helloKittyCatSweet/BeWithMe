"""
聊天相关的 API 路由
Chat Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
import tempfile
import os
from typing import Optional

from ...core.conversation import ConversationAgent
from ...core.asr import WhisperASR
from ...core.voice_cloning import VoiceCloner
from ..models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# 全局组件
current_agent: Optional[ConversationAgent] = None
current_voice_id: Optional[str] = None
asr_engine: Optional[WhisperASR] = None
voice_cloner = VoiceCloner()


def set_agent(agent: ConversationAgent, voice_id: str = None):
    """设置全局对话代理和音色"""
    global current_agent, current_voice_id
    current_agent = agent
    current_voice_id = voice_id


def get_asr_engine():
    """获取 ASR 引擎（延迟初始化）"""
    global asr_engine
    if asr_engine is None:
        try:
            asr_engine = WhisperASR()
        except ImportError as e:
            logger.error(f"ASR 初始化失败: {str(e)}")
            raise HTTPException(status_code=500, detail="语音识别服务未就绪")
    return asr_engine


@router.post("/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    """
    文字对话（不使用语音）
    
    - **message**: 用户消息
    """
    global current_agent
    
    if not current_agent:
        raise HTTPException(status_code=400, detail="请先创建对话代理")
    
    try:
        response = current_agent.generate_response(
            request.message, 
            stream=False
        )
        
        # 安全检查
        is_safe, filtered_response = current_agent.check_safety(response)
        
        return ChatResponse(
            success=True,
            user_message=request.message,
            agent_response=filtered_response,
            is_safe=is_safe
        )
        
    except Exception as e:
        logger.error(f"对话生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice")
async def chat_voice(audio_file: UploadFile = File(...)):
    """
    语音通话完整流程
    
    1. 接收用户录音
    2. ASR 转文字
    3. Mistral 生成回复
    4. ElevenLabs 合成语音
    5. 返回语音文件
    """
    global current_agent, current_voice_id
    
    if not current_agent:
        raise HTTPException(status_code=400, detail="请先创建对话代理")
    
    if not current_voice_id:
        raise HTTPException(status_code=400, detail="请先克隆音色")
    
    try:
        # 1. 保存用户录音
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            content = await audio_file.read()
            tmp_audio.write(content)
            user_audio_path = tmp_audio.name
        
        # 2. ASR 转录
        logger.info("🎙️  转录用户语音...")
        asr = get_asr_engine()
        transcription = asr.transcribe_audio(user_audio_path, language="zh")
        
        if not transcription or not transcription["text"]:
            if os.path.exists(user_audio_path):
                os.unlink(user_audio_path)
            raise HTTPException(status_code=400, detail="语音识别失败，请重试")
        
        user_text = transcription["text"]
        logger.info(f"📝 用户说: {user_text}")
        
        # 3. Mistral 生成回复
        logger.info("🤖 生成回复...")
        response_text = current_agent.generate_response(user_text, stream=False)
        
        # 4. 安全检查
        is_safe, filtered_response = current_agent.check_safety(response_text)
        logger.info(f"💬 回复: {filtered_response}")
        
        # 5. ElevenLabs 合成语音
        logger.info("🔊 合成语音...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_output:
            output_path = tmp_output.name
        
        audio_result = voice_cloner.generate_speech(
            filtered_response,
            current_voice_id,
            output_path
        )
        
        # 清理用户录音
        if os.path.exists(user_audio_path):
            os.unlink(user_audio_path)
        
        if not audio_result:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        # 6. 返回语音文件
        from fastapi.responses import FileResponse
        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="response.mp3",
            headers={
                "X-User-Text": user_text,
                "X-Response-Text": filtered_response,
                "X-Is-Safe": str(is_safe)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音通话处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history():
    """获取对话历史"""
    global current_agent
    
    if not current_agent:
        return {"history": []}
    
    return {
        "success": True,
        "history": current_agent.get_conversation_history()
    }


@router.post("/clear")
async def clear_history():
    """清空对话历史"""
    global current_agent
    
    if current_agent:
        current_agent.clear_history()
    
    return {"success": True, "message": "对话历史已清空"}
