#!/bin/bash

# Quick Fine-Tuning Guide for BeWithMe
# Choose your method and get started in minutes!

set -e

echo "🎯 Be With Me - Quick Fine-Tuning Setup"
echo "========================================"
echo ""
echo "Choose your fine-tuning method:"
echo ""
echo "1) 🚀 Mistral API (Recommended for Hackathon)"
echo "   - No GPU needed"
echo "   - Mistral handles everything"
echo "   - Time: 30 min - 2 hours"
echo "   - Cost: Free (Hackathon)"
echo ""
echo "2) 💻 Local with Unsloth (For quick experiments)"
echo "   - Requires A100/H100 GPU"
echo "   - Downloads ~7GB model"
echo "   - Time: 10-30 min (with GPU)"
echo "   - Cost: CoreWeave credits ($500 available!)"
echo ""
echo "3) 📖 View complete guide"
echo ""
echo "4) ❌ Exit"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "✅ Using Mistral API method"
        echo ""
        
        # Check for training file
        if [ ! -f "training_data/grandma_training.jsonl" ]; then
            echo "⚠️  Training file not found!"
            echo "   First, run: python -m src.training.data_preparation"
            exit 1
        fi
        
        echo "📝 Starting Mistral API fine-tuning..."
        echo ""
        
        source .venv/bin/activate
        python -c "
from src.training.mistral_api_finetuner import quick_finetune
import os

training_file = 'training_data/grandma_training.jsonl'
model_id = quick_finetune(
    training_file=training_file,
    model='mistral-small-latest',
    name='be-with-me-personality'
)

print(f'\n🎉 Success! Model ID: {model_id}')
print(f'\n📊 Monitor progress in W&B:')
print(f'   https://wandb.ai/[your-username]/be-with-me-finetuning')
"
        ;;
    
    2)
        echo ""
        echo "⚠️  Using Local Unsloth method"
        echo ""
        echo "Prerequisites:"
        echo "  - GPU with 40GB+ VRAM (A100/H100)"
        echo "  - ~7GB disk space for model"
        echo ""
        read -p "Do you have a compatible GPU? (y/n): " has_gpu
        
        if [ "$has_gpu" != "y" ]; then
            echo "❌ Local fine-tuning requires GPU"
            echo "   Use method 1 (Mistral API) instead"
            exit 1
        fi
        
        # Check for training file
        if [ ! -f "training_data/grandma_training.jsonl" ]; then
            echo "⚠️  Training file not found!"
            echo "   First, run: python -m src.training.data_preparation"
            exit 1
        fi
        
        echo ""
        echo "📥 Installing Unsloth..."
        source .venv/bin/activate
        pip install unsloth torch transformers peft trl huggingface-hub
        
        echo ""
        echo "🚀 Starting local fine-tuning..."
        python -m src.training.unsloth_finetuner training_data/grandma_training.jsonl
        
        echo ""
        echo "✅ Fine-tuning complete!"
        echo ""
        echo "Next: Upload to HuggingFace"
        echo "  python -c \"from src.training.unsloth_finetuner import UnslothFineTuner; t = UnslothFineTuner(); t.export_to_huggingface('./models/lora_adapter', 'unsloth/mistral-7b-bnb-4bit', 'be-with-me-lora')\""
        ;;
    
    3)
        echo ""
        less docs/FINETUNING_GUIDE.md
        ;;
    
    4)
        echo "Goodbye!"
        exit 0
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "  1. Monitor in W&B dashboard"
echo "  2. Evaluate model in Weave"
echo "  3. Create report with MCP"
echo "  4. Test in your demo"
echo ""
