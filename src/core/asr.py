"""
模块 C: 语音识别 (Whisper ASR)
Module C: Automatic Speech Recognition (Whisper)
"""
import logging
from typing import Optional, Dict
import time

try:
    import whisper
    import torch
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from ..config import WHISPER_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperASR:
    """Whisper 语音识别引擎"""
    
    def __init__(self, model_name: str = None):
        """
        初始化 Whisper 模型
        
        Args:
            model_name: 模型名称 (tiny, base, small, medium, large)
                       建议使用 base 平衡速度和准确度
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("whisper 和 torch 未安装，请运行: pip install openai-whisper torch")
        
        self.model_name = model_name or WHISPER_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🎙️  加载 Whisper 模型: {self.model_name} on {self.device}")
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f"✅ Whisper 模型加载成功")
        except Exception as e:
            logger.error(f"❌ Whisper 模型加载失败: {str(e)}")
            raise
    
    def transcribe_audio(
        self, 
        audio_path: str,
        language: str = "zh",
        return_timestamps: bool = False
    ) -> Optional[Dict]:
        """
        转录音频文件
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh=中文, en=英文)
            return_timestamps: 是否返回时间戳
            
        Returns:
            包含转录结果的字典
        """
        try:
            start_time = time.time()
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                fp16=(self.device == "cuda"),
                verbose=False
            )
            
            elapsed_time = time.time() - start_time
            
            transcribed_text = result["text"].strip()
            
            logger.info(f"✅ 转录完成 (耗时: {elapsed_time:.2f}s)")
            logger.info(f"📝 识别结果: {transcribed_text}")
            
            return {
                "text": transcribed_text,
                "language": result.get("language"),
                "segments": result.get("segments") if return_timestamps else [],
                "elapsed_time": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"❌ 转录失败: {str(e)}")
            return None
    
    def extract_speech_patterns(self, audio_path: str) -> list:
        """
        从音频中提取说话特征（用于构建 PersonalityProfile）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            提取的口头禅和语言特征列表
        """
        try:
            result = self.transcribe_audio(audio_path, return_timestamps=True)
            
            if not result:
                return []
            
            text = result["text"]
            
            # 简单的关键词提取（可以后续用 NLP 优化）
            common_phrases = []
            
            # 检测常见口头禅
            patterns = [
                "嗯", "啊", "呀", "哦", "哎", "诶",
                "你知道吗", "对吧", "是不是", "怎么说呢",
                "那个", "这个", "然后", "所以"
            ]
            
            for pattern in patterns:
                if pattern in text:
                    common_phrases.append(pattern)
            
            logger.info(f"🎯 提取到的语言特征: {common_phrases}")
            return common_phrases
            
        except Exception as e:
            logger.error(f"❌ 提取语言特征失败: {str(e)}")
            return []
    
    def real_time_transcribe(self, audio_stream):
        """
        实时转录（预留接口，可用于后续优化）
        
        TODO: 实现基于 chunk 的实时转录
        """
        # 需要实现音频流的实时处理
        # 建议使用 faster-whisper 或 distil-whisper 优化延迟
        pass


def quick_transcribe(audio_path: str, language: str = "zh") -> str:
    """快速转录音频文件"""
    asr = WhisperASR()
    result = asr.transcribe_audio(audio_path, language)
    return result["text"] if result else ""


def analyze_voice_sample(audio_path: str) -> Dict:
    """
    分析语音样本，提取特征用于创建 PersonalityProfile
    
    Args:
        audio_path: 30秒音频样本路径
        
    Returns:
        包含转录文本和语言特征的字典
    """
    asr = WhisperASR()
    
    result = asr.transcribe_audio(audio_path, return_timestamps=True)
    patterns = asr.extract_speech_patterns(audio_path)
    
    if result:
        return {
            "transcribed_text": result["text"],
            "language": result["language"],
            "speech_patterns": patterns,
            "duration": sum([seg["end"] - seg["start"] for seg in result["segments"]])
        }
    else:
        return {
            "transcribed_text": "",
            "language": "zh",
            "speech_patterns": [],
            "duration": 0
        }
