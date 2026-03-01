"""
聊天相关的 API 路由
Chat Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import logging
import tempfile
import os
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...core.conversation import ConversationAgent
from ...core.asr import WhisperASR, GradioWhisperASR
from ...core.voice_cloning import VoiceCloner
from ...core.ipfs_service import IPFSService
from ...core.blockchain_service import get_blockchain_service
from ..models import ChatRequest, ChatResponse
from ...database.connection import get_db
from ...database.crud import conversation as conversation_crud
from ..auth import get_current_user_optional
from ...config import ASR_ENGINE

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# 全局组件
current_agent: Optional[ConversationAgent] = None
current_voice_id: Optional[str] = None
asr_engine: Optional[WhisperASR] = None
voice_cloner = VoiceCloner()


def _audio_response_meta(audio_path: str, default_name: str):
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == ".wav":
        return "audio/wav", f"{default_name}.wav"
    if ext == ".ogg":
        return "audio/ogg", f"{default_name}.ogg"
    return "audio/mpeg", f"{default_name}.mp3"


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
            if ASR_ENGINE == "gradio":
                logger.info("🌐 使用 Gradio Whisper API")
                asr_engine = GradioWhisperASR()
            else:
                logger.info("🖥️ 使用本地 Whisper 模型")
                asr_engine = WhisperASR()
        except ImportError as e:
            logger.error(f"❌ ASR 初始化失败: {str(e)}")
            raise HTTPException(status_code=500, detail="语音识别服务未就绪")
    return asr_engine


async def save_call_to_ipfs_and_blockchain(
    audio_blob: bytes,
    user_text: str,
    agent_response: str,
    agent_name: str,
    user_address: str = "anonymous"
) -> dict:
    """
    保存通话到IPFS和区块链
    
    Returns:
        包含ipfs_hash和blockchain_tx_hash的字典
    """
    ipfs_hash = None
    blockchain_tx_hash = None
    
    try:
        # 1. 上传到IPFS
        logger.info("📤 上传通话录音到IPFS...")
        ipfs_service = IPFSService()
        
        call_metadata = {
            "user_message": user_text,
            "agent_response": agent_response,
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "audio_size": len(audio_blob) if audio_blob else 0,
        }
        
        ipfs_hash = ipfs_service.upload_json(call_metadata)
        if ipfs_hash:
            logger.info(f"✅ IPFS上传成功: {ipfs_hash}")
        else:
            logger.warning("⚠️ IPFS上传失败，继续处理...")
        
        # 2. 保存到区块链
        if ipfs_hash:
            logger.info("📝 保存到区块链...")
            blockchain_service = get_blockchain_service()
            
            if blockchain_service and blockchain_service.available:
                duration = max(5, len(user_text))  # 简化的时长估算
                blockchain_result = blockchain_service.save_call_record(
                    user_address=user_address,
                    agent_name=agent_name,
                    ipfs_hash=ipfs_hash,
                    duration_seconds=duration,
                    user_text=user_text,
                    agent_response=agent_response
                )
                
                if blockchain_result and blockchain_result.get("status") == "success":
                    blockchain_tx_hash = blockchain_result.get("tx_hash")
                    logger.info(f"✅ 区块链保存成功: {blockchain_tx_hash}")
                else:
                    logger.warning("⚠️ 区块链保存失败，但IPFS已保存")
            else:
                logger.warning("⚠️ 区块链服务不可用")
    
    except Exception as e:
        logger.error(f"❌ 保存到IPFS/区块链失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    return {
        "ipfs_hash": ipfs_hash,
        "blockchain_tx_hash": blockchain_tx_hash
    }


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
    4. (可选) ElevenLabs 合成语音
    5. 返回语音文件（如果有 voice_id）或仅返回文本
    """
    global current_agent, current_voice_id
    
    logger.info("=" * 60)
    logger.info("📞 新的语音消息请求")
    logger.info(f"👤 当前代理: {current_agent}")
    logger.info(f"🎤 当前语音ID: {current_voice_id}")
    logger.info("=" * 60)
    
    if not current_agent:
        logger.error("❌ 错误: 未创建对话代理")
        raise HTTPException(status_code=400, detail="请先创建对话代理")
    
    try:
        # 1. 保存用户录音
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            content = await audio_file.read()
            tmp_audio.write(content)
            user_audio_path = tmp_audio.name
        
        logger.info(f"💾 录音已保存到: {user_audio_path}")
        logger.info(f"📏 音频大小: {len(content)} 字节")
        
        # 2. ASR 转录
        logger.info("🎙️ 开始转录用户语音...")
        asr = get_asr_engine()
        transcription = asr.transcribe_audio(user_audio_path, language="zh")
        
        logger.info(f"📝 ASR响应: {transcription}")
        
        if not transcription or not transcription["text"]:
            logger.error("❌ ASR错误: 无法识别语音")
            if os.path.exists(user_audio_path):
                os.unlink(user_audio_path)
            raise HTTPException(status_code=400, detail="语音识别失败，请重试")
        
        user_text = transcription["text"]
        logger.info(f"✅ 识别成功 - 用户说: '{user_text}'")
        
        # 3. Mistral 生成回复
        logger.info("🤖 调用Mistral生成回复...")
        response_text = current_agent.generate_response(user_text, stream=False)
        logger.info(f"✅ Mistral回复: {response_text}")
        
        # 4. 安全检查
        is_safe, filtered_response = current_agent.check_safety(response_text)
        logger.info(f"✔️ 安全检查完成 - 安全: {is_safe}")
        logger.info(f"💬 最终回复: {filtered_response}")
        
        # 清理用户录音
        if os.path.exists(user_audio_path):
            os.unlink(user_audio_path)
        
        # 5. 如果有 voice_id，合成语音；否则只返回文本
        if current_voice_id:
            logger.info(f"🔊 准备合成语音 (voice_id: {current_voice_id})...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_output:
                output_path = tmp_output.name
            
            logger.info(f"📞 调用ElevenLabs生成语音...")
            audio_result = voice_cloner.generate_speech(
                filtered_response,
                current_voice_id,
                output_path
            )
            
            if not audio_result:
                logger.error("❌ 语音合成失败")
                if os.path.exists(output_path):
                    os.unlink(output_path)
                raise HTTPException(status_code=500, detail="语音合成失败")
            
            logger.info(f"✅ 语音合成成功: {audio_result}")
            
            # 返回语音文件 - 使用 JSON 包装以支持自定义头
            import base64
            from fastapi.responses import JSONResponse
            
            # 读取生成的音频文件
            with open(audio_result, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"📏 音频文件大小: {len(audio_data)} 字节")
            
            # 清理临时文件
            if os.path.exists(output_path):
                os.unlink(output_path)
            
            # 保存到IPFS和区块链
            agent_name = current_agent.profile.name if current_agent and hasattr(current_agent, 'profile') else "AI Companion"
            blockchain_info = await save_call_to_ipfs_and_blockchain(
                audio_blob=audio_data,
                user_text=user_text,
                agent_response=filtered_response,
                agent_name=agent_name
            )
            
            logger.info("📤 返回JSON响应（包含base64音频）")
            # 返回 JSON 响应，包含 base64 编码的音频
            return JSONResponse(
                {
                    "user_message": user_text,
                    "agent_response": filtered_response,
                    "is_safe": is_safe,
                    "has_audio": True,
                    "audio_data": base64.b64encode(audio_data).decode('utf-8'),
                    "audio_format": "mp3",
                    "ipfs_hash": blockchain_info.get("ipfs_hash"),
                    "blockchain_tx_hash": blockchain_info.get("blockchain_tx_hash")
                }
            )
        else:
            # 仅返回文本（无语音）
            logger.info("📝 仅返回文本回复（未配置语音ID）")
            from fastapi.responses import JSONResponse
            
            # 保存到IPFS和区块链（即使没有音频）
            blockchain_info = await save_call_to_ipfs_and_blockchain(
                audio_blob=None,
                user_text=user_text,
                agent_response=filtered_response,
                agent_name="Assistant"
            )
            
            logger.info("📤 返回JSON响应（仅文本）")
            return JSONResponse(
                {
                    "user_message": user_text,
                    "agent_response": filtered_response,
                    "is_safe": is_safe,
                    "has_audio": False,
                    "audio_url": None,
                    "ipfs_hash": blockchain_info.get("ipfs_hash"),
                    "blockchain_tx_hash": blockchain_info.get("blockchain_tx_hash")
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error("=" * 60)
        logger.error(f"❌ 语音通话处理失败")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        logger.error("=" * 60)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(
    user = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    global current_agent
    
    # 如果用户已登录，从数据库获取持久化的对话记录
    if user:
        conversations = conversation_crud.get_user_conversations(db, user.id, limit=50)
        history = []
        for conv in conversations:
            history.append({
                "role": "user",
                "user": conv.user_message,
                "agent": "",
                "timestamp": conv.created_at.isoformat() if conv.created_at else None,
                "blockchain_tx_hash": conv.blockchain_tx_hash,
                "ipfs_hash": conv.ipfs_hash,
                "on_chain_timestamp": conv.on_chain_timestamp.isoformat() if conv.on_chain_timestamp else None,
            })
            history.append({
                "role": "agent",
                "user": "",
                "agent": conv.agent_response,
                "timestamp": conv.created_at.isoformat() if conv.created_at else None,
                "blockchain_tx_hash": conv.blockchain_tx_hash,
                "ipfs_hash": conv.ipfs_hash,
                "on_chain_timestamp": conv.on_chain_timestamp.isoformat() if conv.on_chain_timestamp else None,
            })
        return {
            "success": True,
            "history": history
        }
    
    # 否则，返回内存中的会话历史（向后兼容）
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
