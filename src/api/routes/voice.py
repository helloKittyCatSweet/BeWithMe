"""
音色克隆相关的 API 路由
Voice Cloning Routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import tempfile
import os
import logging

from ...core.voice_cloning import VoiceCloner
from ...core.asr import analyze_voice_sample
from ..models import VoiceInfo, CloneVoiceResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])

# 全局音色克隆器
voice_cloner = VoiceCloner()


@router.post("/clone")
async def clone_voice(
    audio_file: UploadFile = File(...),
    voice_name: str = Form(...),
    description: str = Form("克隆的亲人声音")
) -> CloneVoiceResponse:
    """
    上传音频克隆音色
    
    - **audio_file**: 30秒音频文件 (.mp3 或 .wav)
    - **voice_name**: 音色名称
    - **description**: 音色描述
    """
    try:
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # 克隆音色
        voice_id = voice_cloner.create_voice_from_file(
            tmp_path, 
            voice_name, 
            description
        )
        
        # 分析音频特征
        analysis = None
        try:
            analysis = analyze_voice_sample(tmp_path)
        except:
            pass
        
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        if voice_id:
            return CloneVoiceResponse(
                success=True,
                voice_id=voice_id,
                voice_name=voice_name,
                message="音色克隆成功！",
                analysis=analysis
            )
        else:
            raise HTTPException(status_code=500, detail="音色克隆失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"克隆音色时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
