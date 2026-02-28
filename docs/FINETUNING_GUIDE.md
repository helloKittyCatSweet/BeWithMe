# 🎯 Fine-Tuning Guide for Be With Me

This guide explains how to fine-tune Mistral models to create personalized conversation agents using W&B.

## 📋 Overview

Fine-tuning allows you to create models that **inherently understand** a specific personality, rather than relying on system prompts. This improves:
- Response consistency
- Personality authenticity
- Computational efficiency
- Model specialization

## 🏆 W&B Fine-Tuning Track Requirements

According to the [W&B Hackathon Guide](https://www.notion.so/wandbai/W-B-at-Mistral-Worldwide-Hackathon-2026):

### Judging Criteria

| Criteria | Weight | Requirements |
|----------|--------|--------------|
| **Technical Quality** | ⭐⭐⭐⭐ | Task-fit, quality, workflow completeness |
| **E2E Points** | ⭐⭐ | Use W&B Models + Weave together |
| **Experiment Tracking** | ⭐ | Log training runs to W&B Models |
| **Tracing & Evaluation** | ⭐ | Evaluate model in Weave |
| **W&B Report** | ⭐⭐ | Create summary report |

### Our Approach

✅ **Task-Fit**: Fine-tuning is ideal for personality modeling  
✅ **E2E Integration**: Already using Weave for tracing  
✅ **Complete Workflow**: Data prep → Training → Evaluation  
✅ **W&B Models**: Track all training metrics  
✅ **Weave Evaluation**: Test fine-tuned model in agent pipeline

## 🚀 Quick Start

### 1. Collect Training Data

```python
from src.training.data_preparation import prepare_data_for_finetuning

# Define personality
personality_config = {
    "name": "Grandma",
    "relationship": "Grandmother",
    "personality_traits": "Warm, caring, always concerned about health",
    "speech_patterns": ["Dear child", "Did you eat well?", "Take care"]
}

# Prepare dataset
dataset_path = prepare_data_for_finetuning(
    personality_config=personality_config,
    conversation_history=[]  # Add real conversations if available
)
```

### 2. Start Fine-Tuning

```python
from src.training.mistral_finetuner import run_finetuning_pipeline

# Run complete pipeline
model_id = run_finetuning_pipeline(
    training_file=dataset_path,
    hyperparameters={
        "n_epochs": 3,
        "learning_rate": 1e-5,
        "batch_size": 4
    }
)
```

### 3. Monitor Progress

Go to [W&B Dashboard](https://wandb.ai) to see:
- Training loss curves
- Validation metrics
- Model artifacts

### 4. Evaluate with Weave

The fine-tuned model is automatically evaluated and traced in Weave.

## 📊 Data Format

Training data follows Mistral's conversation format:

```json
{
  "messages": [
    {"role": "user", "content": "How are you?"},
    {"role": "assistant", "content": "Dear child, I'm doing well! Did you eat well today?"}
  ]
}
```

## 🛠️ Alternative: Local Fine-Tuning with Unsloth

For faster local fine-tuning, you can use [Unsloth](https://github.com/unslothai/unsloth):

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/mistral-7b-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True
)

# Apply LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj"]
)

# Train with W&B logging
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    report_to="wandb"
)

trainer.train()
```

## 📈 Expected Results

After fine-tuning, you should see:
- ✅ Consistent use of speech patterns
- ✅ Personality-aligned responses
- ✅ Reduced prompting overhead
- ✅ Better response quality

## 🎓 Key Resources

- [Mistral Fine-Tuning API Docs](https://docs.mistral.ai/capabilities/finetuning/)
- [Mistral + W&B Cookbook](https://docs.mistral.ai/cookbooks/third_party-wandb-02_finetune_and_eval)
- [W&B Models Documentation](https://docs.wandb.ai/models)
- [W&B Weave Evaluation](https://docs.wandb.ai/weave/guides/evaluation)
- [Unsloth GitHub](https://github.com/unslothai/unsloth)

## 💡 Tips for Success

1. **Data Quality > Quantity**: 50-100 high-quality examples beat 1000 mediocre ones
2. **Track Everything**: Log all experiments in W&B Models
3. **Evaluate Rigorously**: Use Weave to test real conversation flows
4. **Create Reports**: Use W&B MCP to auto-generate comparison reports
5. **Show Your Work**: Document your workflow for judges

## 🎯 Next Steps

1. Collect real conversation data from your demo
2. Run the fine-tuning pipeline
3. Compare base model vs fine-tuned model in Weave
4. Create a W&B Report showing improvements
5. Submit to the Fine-Tuning Track!

---

**Questions?** Check the [W&B Hackathon Discord](https://discord.gg/wandb) or find W&B team members on-site.
