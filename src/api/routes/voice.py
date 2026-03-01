"""
音色克隆相关的 API 路由
Voice Cloning Routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import tempfile
import os
import logging
import shutil
import subprocess
from datetime import datetime

from ...core.voice_cloning import VoiceCloner
from ...core.asr import analyze_voice_sample, transcribe_audio
from ...core.conversation import ConversationAgent
from ...core.ipfs_service import get_ipfs_service
from ...config import PINATA_API_KEY, PINATA_SECRET_KEY, IPFS_ENABLED
from ..models import VoiceInfo, CloneVoiceResponse
from ...database import (
    get_db, 
    check_relationship_valid, 
    create_voice_profile,
    log_action,
    get_user_voice_profiles,
    get_voice_profile_by_voice_id
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])

# 全局音色克隆器
voice_cloner = VoiceCloner()


def _audio_response_meta(audio_path: str, default_name: str):
    ext = os.path.splitext(audio_path)[1].lower()
    if ext == ".wav":
        return "audio/wav", f"{default_name}.wav"
    if ext == ".ogg":
        return "audio/ogg", f"{default_name}.ogg"
    return "audio/mpeg", f"{default_name}.mp3"


def _extract_audio_from_mp4(input_path: str) -> str:
    """从 MP4 文件提取音轨为 MP3 文件，返回 MP3 路径。"""
    if not shutil.which("ffmpeg"):
        raise HTTPException(
            status_code=500,
            detail="服务器未安装 ffmpeg，无法处理 MP4。请安装 ffmpeg 后重试。"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as output_file:
        output_path = output_file.name

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-vn",
                "-acodec",
                "libmp3lame",
                "-ar",
                "44100",
                "-ac",
                "1",
                output_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return output_path
    except subprocess.CalledProcessError as exc:
        logger.error(f"从 MP4 提取音频失败: {exc.stderr}")
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=400, detail="MP4 文件音轨提取失败，请确认文件包含可用音频")


@router.get("/list", response_model=List[VoiceInfo])
async def list_voice_profiles(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户的所有音色档案
    """
    profiles = get_user_voice_profiles(db, user_id)
    return profiles


@router.post("/clone")
async def clone_voice(
    audio_file: UploadFile = File(...),
    voice_name: str = Form(...),
    description: str = Form("克隆的亲人声音"),
    user_id: int = Form(...),  # 实际应用中从 JWT token 获取
    relationship_id: Optional[int] = Form(None),  # 关系 ID（可选：用于演示）
    db: Session = Depends(get_db)
) -> CloneVoiceResponse:
    """
    上传音频克隆音色
    
    - **audio_file**: 音频样本文件（支持 .mp3/.wav/.m4a/.flac/.mp4，MP4 将自动提取音轨）
    - **voice_name**: 音色名称
    - **description**: 音色描述
    - **user_id**: 用户 ID
    - **relationship_id**: 亲属关系 ID（如果提供，将验证关系）
    """
    # 如果提供了关系 ID，验证关系有效性
    if relationship_id is not None:
        if not check_relationship_valid(db, relationship_id):
            log_action(db, user_id, "voice_clone_blocked", "VoiceProfile", None,
                      success=False, error_message="Relationship not verified")
            raise HTTPException(
                status_code=403, 
                detail="亲属关系未通过验证或已过期，无法进行声音克隆。请先完成关系验证。"
            )
    else:
        # 没有提供关系 ID，记录警告日志（演示模式）
        logger.warning(f"用户 {user_id} 进行声音克隆但未提供关系验证")
        log_action(db, user_id, "voice_clone_no_verification", "VoiceProfile", None,
                  details="Voice cloning without relationship verification")
    
    temp_files_to_cleanup = []

    try:
        # 保存上传文件，并在 MP4 情况下提取音轨
        original_suffix = os.path.splitext(audio_file.filename or "")[1].lower()
        upload_suffix = original_suffix if original_suffix else ".mp3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=upload_suffix) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            uploaded_path = tmp_file.name
            temp_files_to_cleanup.append(uploaded_path)

        processing_path = uploaded_path
        if upload_suffix == ".mp4":
            processing_path = _extract_audio_from_mp4(uploaded_path)
            temp_files_to_cleanup.append(processing_path)
        
        # 克隆音色
        voice_id = voice_cloner.create_voice_from_file(
            processing_path,
            voice_name, 
            description
        )
        
        # 分析音频特征
        analysis = None
        try:
            analysis = analyze_voice_sample(processing_path)
        except:
            pass
        
        # 保存音频文件到永久位置
        audio_dir = "data/voice_samples"
        os.makedirs(audio_dir, exist_ok=True)
        processed_ext = os.path.splitext(processing_path)[1].lower() or ".mp3"
        audio_filename = f"voice_{user_id}_{voice_id}{processed_ext}"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # 复制到永久位置
        shutil.copy(processing_path, audio_path)
        
        # 上传到 IPFS (如果启用)
        ipfs_hash = None
        ipfs_gateway_url = None
        ipfs_uploaded_at = None
        
        if IPFS_ENABLED and PINATA_API_KEY and PINATA_SECRET_KEY:
            try:
                logger.info(f"Uploading audio to IPFS via Pinata...")
                ipfs_service = get_ipfs_service()
                
                # 上传文件到 IPFS
                result = ipfs_service.upload_file(
                    file_path=audio_path,
                    pin_name=f"voice_{voice_name}_{user_id}",
                    metadata={
                        "user_id": str(user_id),
                        "voice_name": voice_name,
                        "voice_id": voice_id,
                        "relationship_id": str(relationship_id) if relationship_id else "none",
                        "upload_time": datetime.utcnow().isoformat()
                    }
                )
                
                if result and 'IpfsHash' in result:
                    ipfs_hash = result['IpfsHash']
                    ipfs_gateway_url = ipfs_service.get_gateway_url(ipfs_hash)
                    ipfs_uploaded_at = datetime.utcnow()
                    logger.info(f"✅ Audio uploaded to IPFS: {ipfs_hash}")
                    logger.info(f"   Gateway URL: {ipfs_gateway_url}")
                else:
                    logger.warning("IPFS upload failed, continuing without IPFS hash")
            except Exception as e:
                logger.error(f"IPFS upload error: {e}")
                # 不抛出异常，允许继续执行（IPFS 上传是可选的）
        
        if voice_id:
            # 创建音色档案记录（如果提供了关系 ID）
            if relationship_id is not None:
                try:
                    voice_profile = create_voice_profile(
                        db=db,
                        user_id=user_id,
                        relationship_id=relationship_id,
                        voice_id=voice_id,
                        voice_name=voice_name,
                        description=description,
                        source_audio_path=audio_path,
                        audio_duration=analysis.get("duration") if analysis else None,
                        ipfs_hash=ipfs_hash,
                        ipfs_gateway_url=ipfs_gateway_url,
                        ipfs_uploaded_at=ipfs_uploaded_at
                    )
                    logger.info(f"创建音色档案: {voice_profile.id}")
                    if ipfs_hash:
                        logger.info(f"   IPFS Hash: {ipfs_hash}")
                except Exception as e:
                    logger.error(f"创建音色档案失败: {e}")
            
            # 同时设置到 chat 路由中
            from . import chat
            chat.current_voice_id = voice_id
            
            log_action(db, user_id, "voice_cloned", "VoiceProfile", None,
                      details=f"Voice ID: {voice_id}, Name: {voice_name}, IPFS: {ipfs_hash or 'N/A'}")
            
            return CloneVoiceResponse(
                success=True,
                voice_id=voice_id,
                voice_name=voice_name,
                message="音色克隆成功！" + (f" (已上传到 IPFS: {ipfs_hash})" if ipfs_hash else ""),
                analysis=analysis,
                ipfs_hash=ipfs_hash,
                ipfs_gateway_url=ipfs_gateway_url
            )
        else:
            log_action(db, user_id, "voice_clone_failed", "VoiceProfile", None,
                      success=False, error_message="ElevenLabs API failed")
            raise HTTPException(status_code=500, detail="音色克隆失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"克隆音色时出错: {str(e)}")
        log_action(db, user_id, "voice_clone_error", "VoiceProfile", None,
                  success=False, error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for temp_file in temp_files_to_cleanup:
            try:
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass


@router.get("/list", response_model=dict)
async def list_voices():
    """获取所有可用音色"""
    try:
        voices = voice_cloner.get_all_voices()
        return {
            "success": True,
            "count": len(voices),
            "voices": voices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{voice_id}")
async def delete_voice(voice_id: str):
    """删除指定音色"""
    try:
        success = voice_cloner.delete_voice(voice_id)
        if success:
            return {"success": True, "message": "音色删除成功"}
        else:
            raise HTTPException(status_code=500, detail="音色删除失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-call")
async def simulate_call(
    audio_file: UploadFile = File(...),
    voice_id: str = Form(...),
    agent_name: Optional[str] = Form("亲人")
):
    """
    🎯 点睛之笔：模拟通话完整流程
    
    上传用户录音 → ASR → LLM 生成回复 → TTS → 返回音频
    
    - **audio_file**: 用户录音文件 (.mp3, .wav, .m4a)
    - **voice_id**: 克隆的音色ID
    - **agent_name**: 对话代理名称（可选）
    
    返回: 亲人的语音回复 (MP3)
    """
    tmp_input = None
    tmp_output = None
    
    try:
        # Step 1: 保存用户上传的音频
        logger.info(f"📞 模拟通话开始 - 接收用户录音")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_input = tmp_file.name
        
        # Step 2: ASR - 语音转文字
        logger.info(f"🎧 正在识别语音...")
        user_text = transcribe_audio(tmp_input)
        
        if not user_text:
            raise HTTPException(status_code=400, detail="无法识别语音内容")
        
        logger.info(f"👤 用户说: {user_text}")
        
        # Step 3: LLM 生成回复
        logger.info(f"🧠 正在生成回复...")
        
        # 尝试从 conversation 路由获取当前 agent
        from . import conversation as conv_module
        agent = conv_module.current_agent
        
        if agent:
            # 使用已激活的 agent
            ai_response = agent.chat(user_text)
        else:
            # 使用默认的简单回复
            from ...core.conversation import ConversationAgent
            default_agent = ConversationAgent(
                name=agent_name,
                relationship="亲人",
                personality_traits="温暖、关怀、耐心",
                speech_patterns=["说话温柔", "总是关心你"]
            )
            ai_response = default_agent.chat(user_text)
        
        logger.info(f"👵 AI 回复: {ai_response}")
        
        # Step 4: TTS - 文字转语音
        logger.info(f"🎙️ 正在合成语音...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_output = tmp_file.name
        
        audio_path = voice_cloner.generate_speech(
            text=ai_response,
            voice_id=voice_id,
            output_path=tmp_output
        )
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        # Step 5: 返回音频文件
        logger.info(f"✅ 通话完成，返回音频")
        
        # 返回文件后自动清理
        background_tasks = None
        
        return FileResponse(
            path=audio_path,
            media_type=_audio_response_meta(audio_path, "response")[0],
            filename=_audio_response_meta(audio_path, "response")[1],
            headers={
                "X-User-Message": user_text,
                "X-AI-Response": ai_response
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 模拟通话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"通话处理失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if tmp_input and os.path.exists(tmp_input):
            try:
                os.unlink(tmp_input)
            except:
                pass
        # 注意: tmp_output 在 FileResponse 返回后才会被自动清理


@router.post("/quick-tts")
async def quick_tts(
    text: str = Form(...),
    voice_id: str = Form(...)
):
    """
    快速 TTS 接口（仅文本转语音）
    
    - **text**: 要合成的文本
    - **voice_id**: 音色ID
    
    返回: 语音文件 (MP3)
    """
    tmp_output = None
    
    try:
        logger.info(f"🎙️ 快速 TTS: {text[:30]}...")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_output = tmp_file.name
        
        audio_path = voice_cloner.generate_speech(
            text=text,
            voice_id=voice_id,
            output_path=tmp_output
        )
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="语音合成失败")
        
        return FileResponse(
            path=audio_path,
            media_type=_audio_response_meta(audio_path, "tts_output")[0],
            filename=_audio_response_meta(audio_path, "tts_output")[1]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ TTS 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 注意：区块链保存功能已移至前端，前端直接调用智能合约