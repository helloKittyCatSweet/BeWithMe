"""
Core modules for Echoes of Kin
"""
from .voice_cloning import VoiceCloner, quick_clone_voice
from .conversation import ConversationAgent, PersonalityProfile, create_grandmother_agent
from .asr import WhisperASR, quick_transcribe, analyze_voice_sample

__all__ = [
    "VoiceCloner",
    "quick_clone_voice",
    "ConversationAgent",
    "PersonalityProfile",
    "create_grandmother_agent",
    "WhisperASR",
    "quick_transcribe",
    "analyze_voice_sample",
]
