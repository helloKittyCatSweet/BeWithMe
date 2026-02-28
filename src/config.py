"""
配置管理模块
Configuration Management Module
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "")

# W&B Configuration
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "echoes-of-kin")
WANDB_ENTITY = os.getenv("WANDB_ENTITY", "")

# Model Settings
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Audio Settings
SAMPLE_RATE = 16000
AUDIO_FORMAT = "wav"

# Conversation Settings
MAX_RESPONSE_LENGTH = 30  # 最大回复字数
TEMPERATURE = 0.7
MAX_TOKENS = 100

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Database (预留)
DATABASE_URL = os.getenv("DATABASE_URL", "")
