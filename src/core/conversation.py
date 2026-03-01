"""
模块 B: 语气注入与对话生成 (Mistral API)
Module B: Conversation Generation with Personality Injection (Mistral)
"""
try:
    # Try mistralai >= 1.0
    from mistralai import Mistral
    # For newer versions, also try to get ChatMessage
    try:
        from mistralai.models.chat_completion import ChatMessage
    except (ImportError, ModuleNotFoundError):
        ChatMessage = None
except (ImportError, ModuleNotFoundError):
    try:
        # Fallback for 0.1.x versions
        from mistralai import MistralClient as Mistral
        ChatMessage = None
    except (ImportError, ModuleNotFoundError):
        Mistral = None
        ChatMessage = None

from ..config import MISTRAL_API_KEY, MISTRAL_MODEL, TEMPERATURE, MAX_TOKENS, WANDB_PROJECT
import logging
from typing import Generator, List, Dict, Optional

try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalityProfile:
    """亲人性格档案"""
    
    def __init__(
        self,
        name: str,
        relationship: str,
        personality_traits: str,
        speech_patterns: List[str],
        custom_prompt: str = ""
    ):
        self.name = name
        self.relationship = relationship
        self.personality_traits = personality_traits
        self.speech_patterns = speech_patterns
        self.custom_prompt = custom_prompt
    
    def generate_system_prompt(self) -> str:
        """生成系统提示词 (English focused for international presentation)"""
        patterns_str = ", ".join(self.speech_patterns) if self.speech_patterns else "warm and kind"
        
        prompt = f"""You are now playing the role of {self.name}, who is the user's {self.relationship}.

Personality Traits: {self.personality_traits}
Speech Style/Patterns: {patterns_str}

CRITICAL RULES:
1. RESPONSE LANGUAGE: You MUST respond in ENGLISH. Even if the user speaks to you in another language, you must reply in English for this international presentation.
2. BREVITY: Keep your responses very short (under 30 words), natural, and concise, just like a real phone conversation.
3. TONE: Use a colloquial, spoken style. Avoid formal or written language.
4. EMOTION: Show the warmth, care, and love of a family member.
5. HABITS: You may occasionally use characteristic catchphrases or repetitive patterns consistent with your role.

{self.custom_prompt}

Please respond to the user's input now, ensuring they feel the genuine warmth of family connection in English."""
        
        return prompt


class ConversationAgent:
    """对话代理 - 集成 Mistral 和 W&B Weave 追踪"""
    
    def __init__(
        self, 
        profile: PersonalityProfile,
        api_key: str = None,
        enable_weave: bool = True
    ):
        self.profile = profile
        self.api_key = api_key or MISTRAL_API_KEY
        
        # Verify Mistral import
        if Mistral is None:
            raise ImportError(
                "mistralai library is not installed. "
                "Please install it with: uv pip install mistralai"
            )
        
        # Verify API key is available
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not configured. Please check your .env file "
                "or pass api_key parameter explicitly."
            )
        
        self.client = Mistral(api_key=self.api_key)
        self.conversation_history: List[Dict] = []
        self.voice_id: Optional[str] = None  # Optional voice ID for TTS
    
    def generate_response(
        self, 
        user_input: str,
        stream: bool = True
    ) -> str:
        """
        生成对话回复
        
        Args:
            user_input: 用户输入文本
            stream: 是否使用流式输出
            
        Returns:
            回复文本
        """
        try:
            # 构建消息历史 - 总是使用字典格式以保证兼容性
            system_msg = self.profile.generate_system_prompt()
            
            messages = [{"role": "system", "content": system_msg}]
            
            # 添加历史对话（保留最近5轮）
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": user_input})
            
            # 调用 Mistral API
            if stream:
                return self._generate_stream(messages, user_input)
            else:
                response = self.client.chat.complete(
                    model=MISTRAL_MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                
                response_text = response.choices[0].message.content
                
                # 保存对话历史
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": response_text})
                
                return response_text
                
        except Exception as e:
            logger.error(f"❌ 生成回复时出错: {str(e)}")
            return "抱歉，我现在说不出话来了..."

    def _generate_stream(self, messages, user_input):
        try:
            response_text = ""
            for chunk in self.client.chat_stream(
                model=MISTRAL_MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            ):
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta:
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            response_text += content
                            yield content
            
            # 保存对话历史
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_text})
        except Exception as e:
            logger.error(f"❌ 流式生成回复时出错: {str(e)}")
            yield "抱歉，我现在说不出话来了..."
    
    def check_safety(self, text: str) -> tuple[bool, str]:
        """
        安全护栏检查 (预留 NeMo Guardrails 接口)
        
        Args:
            text: 待检查的文本
            
        Returns:
            (is_safe, filtered_text): 是否安全，过滤后的文本
        """
        # TODO: 接入 NVIDIA NeMo Guardrails
        # 目前返回原文本，后续集成安全检查
        
        # 简单的关键词过滤（示例）
        sensitive_words = ["去死", "自杀", "伤害"]
        for word in sensitive_words:
            if word in text:
                logger.warning(f"⚠️  检测到敏感词: {word}")
                return False, "对不起，我不应该说这种话..."
        
        return True, text
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("🗑️  对话历史已清空")


def create_grandmother_agent() -> ConversationAgent:
    """创建奶奶角色的对话代理（示例）"""
    profile = PersonalityProfile(
        name="奶奶",
        relationship="祖母",
        personality_traits="慈祥温柔，喜欢唠叨，总是担心孙子孙女吃不饱穿不暖",
        speech_patterns=["乖囡", "多穿点", "吃饱了吗", "要听话啊"],
        custom_prompt="记得经常问对方有没有好好吃饭，天冷要多穿衣服。"
    )
    return ConversationAgent(profile)


def create_custom_agent(
    name: str,
    relationship: str,
    traits: str,
    patterns: List[str]
) -> ConversationAgent:
    """创建自定义角色的对话代理"""
    profile = PersonalityProfile(
        name=name,
        relationship=relationship,
        personality_traits=traits,
        speech_patterns=patterns
    )
    return ConversationAgent(profile)
