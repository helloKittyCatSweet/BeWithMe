import json
import random
import os
import time
from mistralai import Mistral
from datasets import load_dataset
from dotenv import load_dotenv

# 1. 初始化环境变量和客户端
load_dotenv() 
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env!")

client = Mistral(api_key=api_key)

# 2. 加载数据集
print("正在从 HuggingFace 加载 DailyDialog...")
# 建议先加载完整版，再采样
full_dataset = load_dataset("OpenRL/daily_dialog", split="train")

# 3. 配置参数
sample_size = 500 
AGE_GROUPS = ["CHILD", "YOUNG_ADULT", "ELDER"]
# 随机采样 500 条
selected_dataset = full_dataset.shuffle(seed=42).select(range(sample_size))

# --- 重构函数 ---
def reshape_text_with_llm(original_text, target_age):
    prompt = f"""
    Rewrite the following sentence for a {target_age}. 
    Speaker persona: Compassionate Companion (Warm, empathetic, and culturally appropriate).
    Original: "{original_text}"
    Output ONLY the rewritten text.
    """
    try:
        # 稍微增加一点等待，防止请求过快被 Rate Limit
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\nAPI Error on rewrite: {e}")
        return original_text

# 4. 循环处理
formatted_data = []
temp_file = "temp_formatted_data.jsonl"

print(f"🚀 开始重构 {sample_size} 条对话 (使用 Mistral-Large)...")
print("提示：已开启实时保存，如中断可从临时文件中恢复。")

for idx, item in enumerate(selected_dataset):
    dialogue = item['dialog']
    target_age = random.choice(AGE_GROUPS)
    
    # 打印详细进度
    print(f"[{idx+1}/{sample_size}] 正在处理对话 | 目标群体: {target_age}...", end="\r")
    
    messages = [{"role": "system", "content": f"Context: User is a {target_age}."}]
    
    for i, text in enumerate(dialogue):
        role = "user" if i % 2 == 0 else "assistant"
        if role == "assistant":
            content = reshape_text_with_llm(text, target_age)
        else:
            # User 的话增加标识，让微调后的模型更易识别场景
            content = f"[{target_age}] {text}"
        
        messages.append({"role": role, "content": content})
    
    entry = {"messages": messages}
    formatted_data.append(entry)
    
    # 实时备份到本地，防止崩溃
    with open(temp_file, "a", encoding="utf-8") as tf:
        tf.write(json.dumps(entry, ensure_ascii=False) + "\n")

# 5. 分割训练集和验证集
print("\n\n✅ 所有数据重构完成！正在进行数据分割...")
random.shuffle(formatted_data)

split_idx = int(len(formatted_data) * 0.9)  # 90% 训练, 10% 验证
train_data = formatted_data[:split_idx]
eval_data = formatted_data[split_idx:]

# 6. 保存最终结果
with open("train_kin.jsonl", "w", encoding="utf-8") as f:
    for entry in train_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with open("eval_kin.jsonl", "w", encoding="utf-8") as f:
    for entry in eval_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("-" * 30)
print(f"🏁 任务结束！")
print(f"📦 训练集: {len(train_data)} 条 (train_kin.jsonl)")
print(f"📦 验证集: {len(eval_data)} 条 (eval_kin.jsonl)")
print(f"💡 临时备份已保存至: {temp_file}")