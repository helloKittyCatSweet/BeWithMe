import os
import asyncio
import json
from pathlib import Path
import weave
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# 确保安装了最新版: uv pip install mistralai weave transformers peft torch
from mistralai import Mistral

# --- 1. 环境与路径配置 ---
load_dotenv()
DATA_PATH = Path(__file__).parent / "data"
MODELS_PATH = Path(__file__).parent / "models"
PROJECT_NAME = "be-with-me-kin"

weave.init(PROJECT_NAME)

# 初始化 Mistral 异步客户端
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    print("错误：请在 .env 文件中设置 MISTRAL_API_KEY")
    exit(1)

client = Mistral(api_key=api_key)
print(client)

# --- 2. 数据加载函数 ---
def read_jsonl(path: Path):
    if not path.exists():
        print(f"错误：数据文件不存在: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

# 加载验证集 (CPU 推理慢，建议先取前 3-5 条测试)
val_ds = read_jsonl(DATA_PATH / "formatted_val.jsonl")

# --- 3. Weave 模型定义 ---
from pydantic import PrivateAttr

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import weave
from pydantic import PrivateAttr # 必须导入这个来保护本地模型对象

# --- 3. Weave 模型定义 ---
# --- 3. Weave 模型定义 ---
from pydantic import PrivateAttr
import torch
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

class KinModel(weave.Model):
    model_id: str
    model_type: str  # 'api' 或 'local'
    base_model_name: str = "ministral/Ministral-3b-instruct" 
    system_prompt: str = "You are a compassionate companion, acting as a deceased relative."
    temperature: float = 0.7
    
    # 私有属性，防止 Weave 扫描导致 Pydantic 报错
    _model: any = PrivateAttr(default=None)
    _tokenizer: any = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.model_type == 'local':
            self._load_local_model()

    def _load_local_model(self):
        """整合 Transformers 官方推荐的 CPU 加载方式"""
        print(f"🚀 [CPU 优化模式] 正在加载本地模型: {self.model_id}")
        gc.collect() # 强制垃圾回收
        
        # 1. 加载分词器
        self._tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)

        # 2. 加载基础模型 - 关键：使用 float16 并在 CPU 上进行 low_cpu 优化
        # 虽然是 3b，但 float32 需要 12GB+，float16 只需要 6GB+
        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float16,  # 必须改用 float16 避开 Killed
            low_cpu_mem_usage=True,    # 官方推荐的低 CPU 内存模式
            device_map={"": "cpu"},    # 显式指定 CPU
            trust_remote_code=True
        )

        try:
            # 3. 加载 LoRA 权重
            lora_path = MODELS_PATH / self.model_id
            print(f"  - 正在加载 LoRA 适配器: {lora_path}...")
            # 注意：在内存极度紧张的情况下，不建议执行 merge_and_unload()
            # 因为合并过程会瞬时消耗双倍内存导致 Killed
            self._model = PeftModel.from_pretrained(base_model, str(lora_path))
            print(f"✅ 本地模型已就绪 (非合并模式以保护内存)")
        except Exception as e:
            print(f"⚠️ LoRA 加载失败: {e}，将使用原版模型。")
            self._model = base_model

    @weave.op()
    async def predict(self, messages: list) -> str:
        """
        核心修复：针对 train/val 数据格式进行截断
        """
        # 1. 深度拷贝一份消息，防止修改原始数据
        import copy
        inference_messages = copy.deepcopy(messages)

        # 2. 截断逻辑：如果最后一条是 assistant 的回复（即答案），将其移除
        # 这样模型才能接收到以 User 结尾的 Prompt
        while inference_messages and inference_messages[-1]["role"].lower() == "assistant":
            inference_messages.pop()

        # 3. 健壮性检查：如果没有消息了或者最后一条不是 user，手动提取
        if not inference_messages or inference_messages[-1]["role"].lower() != "user":
            # 尝试从原始列表中找最后一条 user 消息
            last_user = next((m for m in reversed(messages) if m["role"] == "user"), None)
            if last_user:
                # 重新构造：System + 最后一条 User
                inference_messages = [
                    {"role": "system", "content": self.system_prompt},
                    last_user
                ]
            else:
                return "Error: No user message found in conversation."

        # 4. 执行推理
        if self.model_type == 'api':
            return await self._predict_api(inference_messages)
        else:
            return self._predict_local(inference_messages)

    async def _predict_api(self, messages: list) -> str:
        """API 调用现在接收到的已经是截断好的 messages 了"""
        try:
            # 适配 Ministral 在 API 端的命名习惯
            api_model = "ministral-3b-latest" if "ministral" in self.model_id.lower() else self.model_id
            
            response = await client.chat.complete_async(
                model=api_model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            # 如果报 400 错误，打印出消息结构方便调试
            print(f"DEBUG: Error messages structure: {messages}")
            return f"API Error: {e}"

    def _predict_local(self, messages: list) -> str:
        """按照 Transformers 官方文档重写的推理逻辑"""
        try:
            # 1. 构造 Prompt
            # 注入 System Prompt 到对话开头
            full_messages = [{"role": "system", "content": self.system_prompt}] + messages
            
            # 2. 使用官方模板处理输入
            inputs = self._tokenizer.apply_chat_template(
                full_messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to("cpu")

            # 3. 生成输出
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs, 
                    max_new_tokens=80,      # CPU 建议设短一点，否则极慢
                    temperature=self.temperature,
                    do_sample=True
                )

            # 4. 解码 (跳过 input 部分)
            input_length = inputs["input_ids"].shape[-1]
            response = self._tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            return response.strip()
            
        except Exception as e:
            print(f"本地推理出错: {e}")
            return f"Local Error: {e}"

# --- 4. 评分裁判定义 ---
# 关键：暂时不继承 weave.Scorer，直接使用普通类
# 或者确保类中只有基础类型属性
class KinshipScorer(weave.Scorer):
    model_name: str = "mistral-large-latest"

    # 不要在这里定义复杂的 client 对象作为类属性
    # 如果需要 client，直接使用全局定义的那个 client

    @weave.op()
    async def score(self, messages: list, model_output: str) -> dict:
        """
        评分逻辑保持不变，但通过 @weave.op() 确保它被追踪
        """
        user_query = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "N/A")

        eval_prompt = f"""
        Evaluate the following AI response for a companionship application.
        User said: "{user_query}"
        AI Response: "{model_output}"

        Score 1-5 for:
        1. Empathy (Genuine care)
        2. Style (Appropriate tone)
        3. Human-likeness (Natural sounding)

        Return ONLY a JSON object: {{"empathy": int, "style": int, "human_likeness": int, "reason": "short explanation"}}
        """

        try:
            # 直接使用全局初始化好的 client
            response = await client.chat.complete_async(
                model=self.model_name,
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            # 计算综合得分
            avg_score = (result.get('empathy', 0) + result.get('style', 0) + result.get('human_likeness', 0)) / 3.0
            
            return {
                "overall_score": round(avg_score, 2),
                **result
            }
        except Exception as e:
            print(f"评分系统出错: {e}")
            return {"overall_score": 0, "error": str(e)}

# --- 5. 执行主逻辑 ---
async def main():
    models_to_test = [
        {"id": "ministral/Ministral-3b-instruct", "type": "api"}, 
        {"id": "be-with-me-kin-test-1", "type": "local"},
        {"id": "lora_weight_kin_test_2", "type": "local"},
    ]

    dataset = val_ds[:20] # CPU 环境下，数据量一定要小

    for m_info in models_to_test:
        print(f"\n开始评估模型: {m_info['id']}")
        model_instance = KinModel(model_id=m_info["id"], model_type=m_info["type"])
        evaluation = weave.Evaluation(dataset=dataset, scorers=[KinshipScorer()])
        await evaluation.evaluate(model_instance)

if __name__ == "__main__":
    asyncio.run(main())