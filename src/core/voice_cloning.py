"""
模块 A: 音色克隆初始化 (ElevenLabs)
Module A: Voice Cloning Initialization (ElevenLabs)
"""
import json
import os
import requests
import shutil
import uuid
from pathlib import Path
from typing import Optional, Any
import logging
from ..config import ELEVENLABS_API_KEY, VOICE_PROVIDER, XTTS_SPACE_ID, XTTS_LANGUAGE

try:
    from gradio_client import Client, handle_file
except Exception:  # optional dependency
    Client = None
    handle_file = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceCloner:
    """音色克隆管理器（支持 ElevenLabs / XTTS Space）"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.provider = (VOICE_PROVIDER or "auto").strip().lower()
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
        self.xtts_space_id = XTTS_SPACE_ID
        self.xtts_language = XTTS_LANGUAGE
        self._xtts_client = None
        self._xtts_registry_path = Path("data/xtts_voice_registry.json")
        self._xtts_ref_dir = Path("data/xtts_reference_audio")
        self._xtts_ref_dir.mkdir(parents=True, exist_ok=True)

    def _should_use_elevenlabs(self) -> bool:
        return self.provider in ["auto", "elevenlabs"] and bool(self.api_key)

    def _should_use_xtts(self) -> bool:
        return self.provider in ["auto", "xtts-space", "xtts"]

    def _load_xtts_registry(self) -> dict[str, Any]:
        if not self._xtts_registry_path.exists():
            return {}
        try:
            with open(self._xtts_registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_xtts_registry(self, data: dict[str, Any]) -> None:
        self._xtts_registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._xtts_registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_xtts_client(self):
        if self._xtts_client is not None:
            return self._xtts_client
        if Client is None:
            raise RuntimeError("gradio_client 未安装，请先安装 gradio_client")
        self._xtts_client = Client(self.xtts_space_id)
        return self._xtts_client

    def _create_xtts_voice_profile(self, audio_file_path: str, voice_name: str, description: str) -> str:
        voice_id = f"xtts_{uuid.uuid4().hex[:12]}"
        source_ext = Path(audio_file_path).suffix.lower() or ".wav"
        ref_path = self._xtts_ref_dir / f"{voice_id}{source_ext}"
        shutil.copy(audio_file_path, ref_path)

        registry = self._load_xtts_registry()
        registry[voice_id] = {
            "voice_id": voice_id,
            "name": voice_name,
            "description": description,
            "language": self.xtts_language,
            "ref_audio_path": str(ref_path),
        }
        self._save_xtts_registry(registry)
        return voice_id

    def _parse_xtts_result_path(self, result: Any) -> str:
        if isinstance(result, str):
            return result
        if isinstance(result, (list, tuple)) and len(result) > 0:
            first = result[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return first.get("path") or first.get("name") or ""
        if isinstance(result, dict):
            return result.get("path") or result.get("name") or ""
        return ""

    def _find_ref_audio_for_xtts_voice(self, voice_id: str) -> Optional[str]:
        # 先从注册表找
        registry = self._load_xtts_registry()
        profile = registry.get(voice_id)
        if isinstance(profile, dict):
            ref_audio_path = profile.get("ref_audio_path")
            if ref_audio_path and os.path.exists(ref_audio_path):
                return ref_audio_path

        # 兜底：从历史保存的 voice_samples 里反查
        samples_dir = Path("data/voice_samples")
        if not samples_dir.exists():
            return None

        candidates = sorted(samples_dir.glob(f"*_{voice_id}.*"), key=lambda p: p.stat().st_mtime, reverse=True)
        for candidate in candidates:
            if candidate.is_file():
                # 回写到注册表，避免下次再扫描
                registry[voice_id] = {
                    "voice_id": voice_id,
                    "name": voice_id,
                    "description": "Recovered XTTS voice profile",
                    "language": self.xtts_language,
                    "ref_audio_path": str(candidate),
                }
                self._save_xtts_registry(registry)
                return str(candidate)

        return None

    def _xtts_generate_speech(self, text: str, voice_id: str, output_path: str) -> Optional[str]:
        registry = self._load_xtts_registry()
        profile = registry.get(voice_id) if isinstance(registry.get(voice_id), dict) else {}
        ref_audio_path = self._find_ref_audio_for_xtts_voice(voice_id)
        if not ref_audio_path:
            logger.error(f"❌ XTTS voice 不存在: {voice_id}")
            return None

        try:
            client = self._get_xtts_client()
            result = client.predict(
                text=text,
                language=profile.get("language") or self.xtts_language,
                speaker_wav=handle_file(ref_audio_path),
                api_name="/predict"
            )
            generated_path = self._parse_xtts_result_path(result)
            if not generated_path or not os.path.exists(generated_path):
                logger.error(f"❌ XTTS 返回无效结果: {result}")
                return None

            generated_ext = Path(generated_path).suffix.lower() or ".wav"
            final_path = str(Path(output_path).with_suffix(generated_ext))
            shutil.copy(generated_path, final_path)
            logger.info(f"✅ XTTS 语音生成成功: {final_path}")
            return final_path
        except Exception as e:
            logger.error(f"❌ XTTS 语音生成失败: {str(e)}")
            return None
    
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
        if self._should_use_elevenlabs():
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
                    logger.info(f"✅ ElevenLabs 音色克隆成功！Voice ID: {voice_id}")
                    return voice_id
                else:
                    logger.error(f"❌ ElevenLabs 音色克隆失败: {response.text}")
            except Exception as e:
                logger.error(f"❌ ElevenLabs 创建音色出错: {str(e)}")

        if self._should_use_xtts():
            try:
                xtts_voice_id = self._create_xtts_voice_profile(audio_file_path, voice_name, description)
                logger.info(f"✅ XTTS 参考音色已保存: {xtts_voice_id}")
                return xtts_voice_id
            except Exception as e:
                logger.error(f"❌ XTTS 保存音色失败: {str(e)}")

        return None
    
    def get_all_voices(self) -> list:
        """获取所有可用音色列表"""
        voices = []

        if self._should_use_elevenlabs():
            try:
                url = f"{self.base_url}/voices"
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    eleven_voices = response.json().get('voices', [])
                    voices.extend(eleven_voices)
                else:
                    logger.error(f"❌ ElevenLabs 获取音色列表失败: {response.text}")
            except Exception as e:
                logger.error(f"❌ ElevenLabs 获取音色列表时出错: {str(e)}")

        if self._should_use_xtts():
            registry = self._load_xtts_registry()
            xtts_voices = [
                {
                    "voice_id": item.get("voice_id"),
                    "name": item.get("name"),
                    "labels": {
                        "description": item.get("description") or "XTTS Space Voice"
                    }
                }
                for item in registry.values()
                if isinstance(item, dict)
            ]
            voices.extend(xtts_voices)

        logger.info(f"📋 获取到 {len(voices)} 个音色")
        return voices
    
    def delete_voice(self, voice_id: str) -> bool:
        """删除指定音色"""
        if voice_id.startswith("xtts_"):
            registry = self._load_xtts_registry()
            profile = registry.get(voice_id)
            if not profile:
                return False
            ref_audio_path = profile.get("ref_audio_path")
            if ref_audio_path and os.path.exists(ref_audio_path):
                try:
                    os.unlink(ref_audio_path)
                except Exception:
                    pass
            registry.pop(voice_id, None)
            self._save_xtts_registry(registry)
            logger.info(f"✅ XTTS 音色 {voice_id} 删除成功")
            return True

        if not self._should_use_elevenlabs():
            logger.error("❌ 当前 provider 不支持删除该音色")
            return False

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
        if voice_id.startswith("xtts_"):
            return self._xtts_generate_speech(text, voice_id, output_path)

        if not self._should_use_elevenlabs():
            logger.error("❌ 当前 provider 未启用 ElevenLabs，且 voice_id 不是 XTTS 音色")
            return None

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
                logger.info(f"✅ ElevenLabs 语音生成成功: {output_path}")
                return output_path
            else:
                logger.error(f"❌ ElevenLabs 语音生成失败: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 生成语音时出错: {str(e)}")
            return None


def quick_clone_voice(audio_path: str, name: str) -> Optional[str]:
    """快速克隆音色并返回 voice_id"""
    cloner = VoiceCloner()
    return cloner.create_voice_from_file(audio_path, name)
