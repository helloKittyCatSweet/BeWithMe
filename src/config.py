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

# Pinata IPFS Configuration
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "f287105113f97222914c")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY", "b9c8d88f86539e515a4b87fc426b321adc81496294ec73d74bc6fe3d31e8b78d")
IPFS_ENABLED = os.getenv("IPFS_ENABLED", "true").lower() == "true"

# W&B Configuration
WANDB_PROJECT = os.getenv("WANDB_PROJECT", "echoes-of-kin")
WANDB_ENTITY = os.getenv("WANDB_ENTITY", "")

# Model Settings
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-7b")
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

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# Database (预留)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Blockchain Configuration
BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "https://sepolia.infura.io/v3/placeholder")
BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "")
BLOCKCHAIN_ENABLED = os.getenv("BLOCKCHAIN_ENABLED", "true").lower() == "true"

# Contract ABI (simplified for now)
BLOCKCHAIN_CONTRACT_ABI = os.getenv("BLOCKCHAIN_CONTRACT_ABI", "[]")
