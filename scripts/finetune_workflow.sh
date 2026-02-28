#!/bin/bash
# Complete fine-tuning workflow for Be With Me project

set -e  # Exit on error

echo "🎯 Be With Me - Fine-Tuning Workflow"
echo "===================================="

# Activate virtual environment
source .venv/bin/activate

# Step 1: Prepare training data
echo ""
echo "📝 Step 1: Preparing training data..."
python -m src.training.data_preparation

# Step 2: Start fine-tuning
echo ""
echo "🚀 Step 2: Starting fine-tuning job..."
python -m src.training.mistral_finetuner

# Step 3: Evaluate model (after training completes)
echo ""
echo "🧪 Step 3: Evaluation will be tracked in W&B"
echo "   View results at: https://wandb.ai/[your-entity]/be-with-me-finetuning"

echo ""
echo "✅ Fine-tuning workflow completed!"
echo "   Check W&B dashboard for training curves and model artifacts"
