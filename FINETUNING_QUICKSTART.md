# 🎯 Fine-Tuning Quick Start

This is a condensed guide to get you started with fine-tuning **right now**.

## ⚡ 5-Minute Setup

### 1. Install Dependencies (Already Done ✅)
```bash
# You already have wandb and weave installed!
# If not: uv pip install wandb weave
```

### 2. Prepare Training Data

Create a simple training dataset:

```python
# Quick example
from src.training.data_preparation import prepare_data_for_finetuning

personality = {
    "name": "Grandma",
    "relationship": "Grandmother",
    "personality_traits": "Warm, caring, loves to tell stories",
    "speech_patterns": ["Dear child", "Did you eat?", "Take care"]
}

# Generate training data
dataset_path = prepare_data_for_finetuning(
    personality_config=personality,
    conversation_history=[]  # Add real conversations if you have them
)

print(f"✅ Training data ready: {dataset_path}")
```

### 3. Start Fine-Tuning

```python
from src.training.mistral_finetuner import run_finetuning_pipeline

# This will:
# - Upload data to Mistral
# - Start training job  
# - Monitor progress
# - Log everything to W&B

model_id = run_finetuning_pipeline(
    training_file="./training_data/grandma_training.jsonl",
    hyperparameters={
        "n_epochs": 3,
        "learning_rate": 1e-5
    }
)

print(f"🎉 Model ready: {model_id}")
```

### 4. Monitor in W&B

Go to: https://wandb.ai/[your-username]/be-with-me-finetuning

You'll see:
- 📈 Training loss curves
- 📊 Validation metrics
- 💾 Model artifacts
- 🔍 Weave traces

## 🎯 For the Hackathon

### Judging Criteria Checklist

- [ ] **Technical Quality** (⭐⭐⭐⭐)
  - [ ] Show why fine-tuning is better than prompts
  - [ ] Complete workflow: data → train → eval
  - [ ] Benchmark improvements

- [ ] **E2E Points** (⭐⭐)
  - [x] Use W&B Models ✅  
  - [x] Use Weave ✅
  - [ ] Show them working together

- [ ] **Experiment Tracking** (⭐)
  - [ ] Loss plots in W&B Models
  - [ ] Model saved as artifact

- [ ] **Tracing & Evaluation** (⭐)
  - [ ] Traces in Weave
  - [ ] Evaluation results

- [ ] **W&B Report** (⭐⭐)
  - [ ] Create summary report
  - [ ] Show training curves
  - [ ] Compare base vs fine-tuned

### Quick Win Strategy

1. **Collect Data** (15 min)
   - Use your demo conversations
   - Generate 50-100 examples

2. **Fine-Tune** (30-60 min)
   - Run the pipeline
   - Monitor in W&B

3. **Evaluate** (15 min)
   - Test in Weave
   - Compare responses

4. **Create Report** (20 min)
   - Use W&B MCP: "Generate report comparing my fine-tuning runs"
   - Add screenshots

Total time: ~2 hours for complete submission!

## 💡 Pro Tips

### Use W&B MCP for Reports
```bash
# In Cursor/Claude, ask:
"Generate a W&B report comparing my base model vs fine-tuned model runs"
```

### Track Everything
```python
import wandb

wandb.log({
    "training_loss": loss,
    "eval_accuracy": acc,
    "personality_match_score": score
})
```

### Evaluate with Weave
```python
@weave.op()
def personality_score(response: str) -> float:
    """Custom metric: how well does response match personality?"""
    # Your evaluation logic
    return score
```

## 🚨 Common Issues

### Issue: "Mistral API key invalid"
**Fix**: Check your `.env` file has `MISTRAL_API_KEY=...`

### Issue: "Training data format error"
**Fix**: Ensure JSONL format with `messages` field:
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### Issue: "W&B not logging"
**Fix**: Run `wandb login` and paste your API key

## 📚 Resources

- **Mistral Fine-Tuning**: https://docs.mistral.ai/capabilities/finetuning/
- **W&B Models**: https://docs.wandb.ai/models
- **Weave Evaluation**: https://docs.wandb.ai/weave/guides/evaluation
- **Hackathon Guide**: [Full documentation](FINETUNING_GUIDE.md)

## 🎯 Next Steps

1. Run data preparation script
2. Start fine-tuning job
3. Monitor in W&B dashboard
4. Create evaluation in Weave
5. Generate report with MCP
6. Submit to judges!

---

**Need help?** Find W&B team members at the hackathon venue 💛
