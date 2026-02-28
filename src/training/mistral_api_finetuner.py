import os, asyncio, json, random
from pathlib import Path
import weave
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
# 1. 路径与环境配置
# 假设你的数据在当前脚本目录的 ../data 下
DATA_PATH = Path(__file__).parent / "data"
PROJECT_NAME = "be-with-me-kin"
weave.init(PROJECT_NAME)

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# 2. 加载你刚才分割好的本地数据
def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

# 加载数据
train_path = DATA_PATH / "formatted_train.jsonl"
val_path = DATA_PATH / "formatted_val.jsonl"
train_ds = read_jsonl(train_path)
val_ds = read_jsonl(val_path)

# 3. 定义评估模型类 (Weave 风格)
class KinModel(weave.Model):
    model: str
    system_prompt: str = "You are a compassionate companion."
    temperature: float = 0.7

    @weave.op()
    async def predict(self, messages: list):
        """
        这里的输入 messages 已经是训练集里的格式
        我们需要提取 user 的输入来做预测
        """
        # 提取最后一条 user 消息作为输入
        user_content = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

        # 构造推理用的 Prompt
        inference_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        chat_response = client.chat.complete(
            model=self.model,
            messages=inference_messages,
            temperature=self.temperature
        )
        return chat_response.choices[0].message.content

# 4. 定义评分标准 (Scorer)
class KinshipScorer(weave.Scorer):
    model_name: str = "mistral-large-latest"

    @weave.op()
    async def score(self, messages: list, model_output: str) -> dict:
        # 1. 提取上下文信息
        # 假设 messages[0] 是 system prompt，包含了 Context: User is a [AGE]
        context = messages[0]["content"]
        user_query = messages[-1]["content"] # 最后一条 user 的话

        # 2. 构造裁判 Prompt
        eval_prompt = f"""
        Evaluate the following AI response for a companionship application.
        The user is: {context}
        User said: "{user_query}"
        AI Response: "{model_output}"

        Score the response from 1-5 on:
        1. Empathy: Does it show genuine care?
        2. Style: Is the tone appropriate for the specific age group?
        3. Human-likeness: Does it sound like a person, not a bot?

        Return ONLY a JSON object with keys: 'empathy', 'style', 'human_likeness' and a brief 'reason'.
        """

        try:
            # 调用 Mistral Large 作为裁判
            response = client.chat.complete(
                model=self.model_name,
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            # 计算一个综合得分
            avg_score = (result['empathy'] + result['style'] + result['human_likeness']) / 3
            return {
                "overall_score": avg_score,
                "metadata": result
            }
        except Exception as e:
            return {"error": str(e)}

# 初始化新的评分器
kin_scorer = KinshipScorer()

# 5. 准备微调格式
# Mistral FT 需要 messages 列表，里面包含 role 和 content
def save_jsonl(ds, path):
    with open(path, "w", encoding='utf-8') as f:
        for row in ds:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

# 已经处理好的数据已经是正确的 FT 格式，直接保存备份即可
save_jsonl(train_ds, DATA_PATH / "formatted_train.jsonl")
save_jsonl(val_ds, DATA_PATH / "formatted_val.jsonl")

def clean_and_format_data(dataset):
    """
    确保每一条数据都以 assistant 结尾，且格式正确
    """
    clean_ds = []
    for entry in dataset:
        messages = entry.get("messages", [])
        if not messages:
            continue
        
        # 规则 1：如果最后一条不是 assistant，就把它删掉（或者你可以补充，但删除最快）
        if messages[-1]["role"].lower() != "assistant":
            # 尝试往前找，直到找到最后一个 assistant 结尾的地方
            while messages and messages[-1]["role"].lower() != "assistant":
                messages.pop()
        
        # 规则 2：对话至少要有 2 条（User + Assistant）
        if len(messages) >= 2:
            clean_ds.append({"messages": messages})
            
    return clean_ds

# 在 main 函数或 run_finetune 之前执行清洗
train_ds_cleaned = clean_and_format_data(train_ds)
val_ds_cleaned = clean_and_format_data(val_ds)

# 覆盖保存
save_jsonl(train_ds_cleaned, DATA_PATH / "formatted_train.jsonl")
save_jsonl(val_ds_cleaned, DATA_PATH / "formatted_val.jsonl")

# 6. 上传并创建微调任务
async def run_finetune():
    print("📤 正在上传训练文件...")
    # 核心修改：将文件流包装在符合要求的字典中，键名必须是 'file'
    with open(DATA_PATH / "formatted_train.jsonl", "rb") as f:
        ds_train = client.files.upload(
            file = {
                "file_name": "train_kin.jsonl",
                "content": open(train_path, "rb"),
            }
        )
    
    print("📤 正在上传验证文件...")
    with open(DATA_PATH / "formatted_val.jsonl", "rb") as f:
        ds_val = client.files.upload(
            file = {
                "file_name": "val_kin.jsonl",
                "content": open(val_path, "rb"),
            }
        )

    print(f"🚀 创建微调任务: {PROJECT_NAME}")
    created_job = client.fine_tuning.jobs.create(
        model="open-mistral-7b",
        training_files=[{"file_id": ds_train.id, "weight": 1}],
        validation_files=[ds_val.id],
        hyperparameters={
            "training_steps": 120,
            "learning_rate": 0.0001,
        },
        auto_start=True,
        # integrations=[
        #     {
        #         "type": "wandb",
        #         "project": os.getenv("WANDB_PROJECT", "be-with-me-kin"),
        #         "api_key": os.environ.get("WANDB_API_KEY"),
        #     }
        # ],
    )

# 7. 评估流程
async def main():
    # A. 评估基础模型 (作为 Baseline)
    # base_model = KinModel(model="open-mistral-7b")
    # evaluation = weave.Evaluation(dataset=val_ds[:20], scorers=[kin_scorer])
    # print("📊 正在评估基础模型...")
    # await evaluation.evaluate(base_model)

    # B. 执行微调 (这步会持续一段时间)
    await run_finetune()
    print(f"任务已发起。请在 W&B 监控曲线。")

if __name__ == "__main__":
    asyncio.run(main())