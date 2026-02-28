"""
模块 A: 音色克隆初始化 (ElevenLabs)
Module A: Voice Cloning Initialization (ElevenLabs)
"""
import requests
from typing import Optional
import logging
from ..config import ELEVENLABS_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceCloner:
    """ElevenLabs 音色克隆管理器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
    
    def create_voice_from_file(
        self, 
        audio_file_path: str, 
        voice_name: str,
        description: str = "克隆的亲人声音"
    ) -> Optional[str]:
        """
        上传音频文件并创建克隆音色
        
        Args:
            audio_file_path: 音频文件路径 (30秒的 .mp3 或 .wav)
            voice_name: 音色名称
            description: 音色描述
            
        Returns:
            voice_id: 成功返回音色ID，失败返回 None
        """
        try:
            url = f"{self.base_url}/voices/add"
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'files': (audio_file_path.split('/')[-1], audio_file, 'audio/mpeg')
                }
                data = {
                    'name': voice_name,
                    'description': description
                }
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                voice_id = response.json().get('voice_id')
                logger.info(f"✅ 音色克隆成功！Voice ID: {voice_id}")
                return voice_id
            else:
                logger.error(f"❌ 音色克隆失败: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 创建音色时出错: {str(e)}")
            return None
    
    def get_all_voices(self) -> list:
        """获取所有可用音色列表"""
        try:
            url = f"{self.base_url}/voices"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                voices = response.json().get('voices', [])
                logger.info(f"📋 获取到 {len(voices)} 个音色")
                return voices
            else:
                logger.error(f"❌ 获取音色列表失败: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取音色列表时出错: {str(e)}")
            return []
    
    def delete_voice(self, voice_id: str) -> bool:
        """删除指定音色"""
        try:
            url = f"{self.base_url}/voices/{voice_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code == 200:
                logger.info(f"✅ 音色 {voice_id} 删除成功")
                return True
            else:
                logger.error(f"❌ 删除音色失败: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 删除音色时出错: {str(e)}")
            return False
    
    def generate_speech(
        self, 
        text: str, 
        voice_id: str,
        output_path: str = "output.mp3"
    ) -> Optional[str]:
        """
        使用克隆音色生成语音
        
        Args:
            text: 要转换的文本
            voice_id: 音色ID
            output_path: 输出文件路径
            
        Returns:
            output_path: 成功返回文件路径，失败返回 None
        """
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2",  # 使用 turbo 模型降低延迟
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(
                url,
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logger.info(f"✅ 语音生成成功: {output_path}")
                return output_path
            else:
                logger.error(f"❌ 语音生成失败: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 生成语音时出错: {str(e)}")
            return None


def quick_clone_voice(audio_path: str, name: str) -> Optional[str]:
    """快速克隆音色并返回 voice_id"""
    cloner = VoiceCloner()
    return cloner.create_voice_from_file(audio_path, name)
