"""
微调模型推理脚本
Fine-tuned Model Inference Script
"""
import os
from pathlib import Path
from typing import List, Optional
import torch
from transformers import AutoTokenizer
from peft import AutoPeftModelForCausalLM
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = "be-with-me-kin"
MODEL_DIR = Path(__file__).parent / "models" / PROJECT_NAME
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class KinAgent:
    """微调后的亲属关系 Agent"""
    
    def __init__(self, model_dir: Path = MODEL_DIR):
        """初始化 Agent"""
        if not model_dir.exists():
            raise FileNotFoundError(f"模型目录不存在: {model_dir}")
        
        print(f"📥 加载模型: {model_dir}")
        
        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        
        # 加载模型
        self.model = AutoPeftModelForCausalLM.from_pretrained(
            str(model_dir),
            device_map={"": 0} if DEVICE == "cuda" else "cpu",
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        )
        
        self.model.eval()
        print(f"✅ 模型加载完成")
    
    def generate(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> str:
        """生成回复"""
        
        # 构造提示
        if system_prompt:
            prompt = f"[SYSTEM] {system_prompt}\n[USER] {user_message}\n[ASSISTANT]"
        else:
            prompt = f"[USER] {user_message}\n[ASSISTANT]"
        
        # 分词
        input_ids = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048,
        )["input_ids"].to(DEVICE)
        
        # 生成
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=256,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # 解码
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # 提取 assistant 的回复
        if "[ASSISTANT]" in output:
            response = output.split("[ASSISTANT]")[-1].strip()
        else:
            response = output.strip()
        
        return response
    
    def chat(
        self,
        conversation: List[dict],
        system_prompt: Optional[str] = None,
    ) -> str:
        """多轮对话"""
        
        # 构造完整的对话历史
        prompt = ""
        
        if system_prompt:
            prompt += f"[SYSTEM] {system_prompt}\n"
        
        for msg in conversation:
            role = msg.get("role", "").upper()
            content = msg.get("content", "")
            prompt += f"[{role}] {content}\n"
        
        prompt += "[ASSISTANT]"
        
        # 分词
        input_ids = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048,
        )["input_ids"].to(DEVICE)
        
        # 生成
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # 解码
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # 提取 assistant 的回复
        if "[ASSISTANT]" in output:
            response = output.split("[ASSISTANT]")[-1].strip()
        else:
            response = output.strip()
        
        return response


def interactive_chat():
    """交互式聊天"""
    print("""
╔════════════════════════════════════════╗
║  🎙️  Be With Me - Chat Interface    ║
║  微调模型交互式聊天                    ║
╚════════════════════════════════════════╝
    """)
    
    try:
        agent = KinAgent()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\n提示: 请先运行微调脚本:")
        print("   python src/training/local_mistral_finetuner.py")
        return
    
    # 系统提示
    system_prompt = input("🧠 系统提示（回车使用默认）: ").strip()
    if not system_prompt:
        system_prompt = "You are a compassionate companion who helps users by listening and providing emotional support."
    
    print("\n💬 开始聊天（输入 'quit' 或 'exit' 退出）\n")
    
    conversation = []
    
    while True:
        user_input = input("👤 你: ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        # 添加到对话历史
        conversation.append({"role": "USER", "content": user_input})
        
        # 生成回复
        print("⏳ 生成中...")
        response = agent.chat(conversation, system_prompt)
        
        # 添加回复到对话历史
        conversation.append({"role": "ASSISTANT", "content": response})
        
        print(f"🤖 Agent: {response}\n")


def batch_inference():
    """批量推理"""
    print("""
╔════════════════════════════════════════╗
║  🎙️  Batch Inference Mode           ║
║  批量推理模式                         ║
╚════════════════════════════════════════╝
    """)
    
    try:
        agent = KinAgent()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # 测试问题
    test_questions = [
        "你好，我是来自北京的学生，今年18岁。",
        "我很想念我的祖母，她已经去世5年了。",
        "今天天气真好，我很开心。",
        "我在工作中遇到了一些困难。",
    ]
    
    print("\n" + "=" * 80)
    print("批量推理示例")
    print("=" * 80 + "\n")
    
    for idx, question in enumerate(test_questions, 1):
        print(f"【示例 {idx}】")
        print(f"👤 输入: {question}")
        
        response = agent.generate(question)
        print(f"🤖 输出: {response}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_inference()
    else:
        interactive_chat()
