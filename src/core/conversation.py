"""
模块 B: 语气注入与对话生成 (Mistral API)
Module B: Conversation Generation with Personality Injection (Mistral)
"""
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    # Fallback for different mistralai versions
    try:
        from mistralai import MistralClient
        ChatMessage = None  # Will use dict format
    except ImportError:
        MistralClient = None
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
        """生成系统提示词"""
        patterns_str = "、".join(self.speech_patterns) if self.speech_patterns else "温暖亲切"
        
        prompt = f"""你现在是{self.name}，是用户的{self.relationship}。

你的性格特征：{self.personality_traits}

你的说话风格特点：{patterns_str}

重要规则：
1. 保持回复简短，不超过30字，像真正的电话通话一样自然
2. 用口语化的表达，不要书面语
3. 体现长辈的关怀和温暖
4. 可以适当重复一些口头禅

{self.custom_prompt}

请根据用户的输入进行回复，让对方感受到真实的亲情温暖。"""
        
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
        self.client = MistralClient(api_key=self.api_key)
        self.conversation_history: List[Dict] = []
        
        # 初始化 W&B Weave（可选）
        if enable_weave and WEAVE_AVAILABLE:
            try:
                weave.init(WANDB_PROJECT)
                logger.info("✅ W&B Weave 追踪已启用")
            except Exception as e:
                logger.warning(f"⚠️  W&B Weave 初始化失败: {str(e)}")
    
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
            # 构建消息历史
            system_msg = self.profile.generate_system_prompt()
            
            if ChatMessage:
                messages = [ChatMessage(role="system", content=system_msg)]
            else:
                messages = [{"role": "system", "content": system_msg}]
            
            # 添加历史对话（保留最近5轮）
            for msg in self.conversation_history[-10:]:
                if ChatMessage:
                    messages.append(ChatMessage(
                        role=msg["role"], 
                        content=msg["content"]
                    ))
                else:
                    messages.append(msg)
            
            # 添加当前用户输入
            if ChatMessage:
                messages.append(ChatMessage(role="user", content=user_input))
            else:
                messages.append({"role": "user", "content": user_input})
            
            # 调用 Mistral API（优先使用 open-* 模型）
            if stream:
                response_text = ""
                for chunk in self.client.chat_stream(
                    model=MISTRAL_MODEL,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                ):
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response_text += content
                        yield content
                
                # 保存对话历史
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": response_text})
                
            else:
                response = self.client.chat(
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
