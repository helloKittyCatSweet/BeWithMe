# 🎙️ Be With Me - AI Voice Companion

**AI-Powered Voice Cloning & Conversation System**

Create meaningful conversations with AI that sounds and talks like your loved ones. Built for [NVIDIA Mistral Worldwide Hackathon 2026](https://worldwide-hackathon.mistral.ai/).

## 🏆 Hackathon Tracks

This project supports **multiple tracks**:

- ✅ **W&B Fine-Tuning Track** - Fine-tune Mistral models for personality adaptation
- ✅ **Mistral Agents Track** - Conversational AI with personality injection  
- ✅ **General Track** - Voice cloning + LLM conversation system

## ✨ Features

### Core Capabilities
- 🎤 **Voice Cloning** - 30-second instant voice cloning via ElevenLabs
- 🤖 **Personality Modeling** - Create AI agents with specific traits and speech patterns
- 💬 **Natural Conversations** - Powered by Mistral Large 2
- 🎧 **Speech Recognition** - OpenAI Whisper for voice input

### Advanced Features
- 📊 **W&B Weave Integration** - Trace every conversation for debugging
- 🔧 **Fine-Tuning Support** - Train models to inherently learn personalities
- 🛡️ **Safety Check Interface** - Ready for NeMo Guardrails integration
- 📈 **Experiment Tracking** - Full W&B Models integration

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.10+
python --version

# uv package manager (recommended)
pip install uv
```

### Installation

```bash
# Clone repository
cd BeWithMe

# Create virtual environment
uv venv

# Install dependencies
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Add your API keys
MISTRAL_API_KEY=your_mistral_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
WANDB_API_KEY=your_wandb_api_key  # Optional but recommended
```

### Run the Application

**Option 1: One-command launch** (Recommended)
```bash
./scripts/run_all.sh
```

**Option 2: Separate terminals**
```bash
# Terminal 1: Backend
./scripts/run_backend.sh

# Terminal 2: Frontend
./scripts/run_frontend.sh
```

Then visit:
- 🎨 **Frontend**: http://localhost:8501
- 🔧 **API Docs**: http://localhost:8000/docs

## 📖 Documentation

- [🏗️ Architecture Guide](docs/ARCHITECTURE.md)
- [⚡ Quick Start Guide](QUICKSTART.md)
- [🎯 Fine-Tuning Guide](docs/FINETUNING_GUIDE.md) - **New!**
- [🎭 Demo Guide](docs/DEMO_GUIDE.md)
- [📁 Project Structure](docs/PROJECT_STRUCTURE.md)

## 🎯 W&B Fine-Tuning Track

Want to compete in the Fine-Tuning track? We've got you covered!

### Why Fine-Tune?

Instead of using system prompts, fine-tune Mistral to **inherently understand** personalities:
- Better consistency
- More authentic responses  
- Computational efficiency
- Task specialization

### Fine-Tuning Workflow

```bash
# 1. Prepare training data from conversations
python -m src.training.data_preparation

# 2. Start fine-tuning job (tracked in W&B)
python -m src.training.mistral_finetuner

# 3. Monitor progress in W&B dashboard
# 4. Evaluate with Weave

# Or run the complete pipeline:
./scripts/finetune_workflow.sh
```

**Key Features:**
- ✅ Automatic W&B Models tracking
- ✅ Weave evaluation integration
- ✅ Artifact logging (LoRA adapters)
- ✅ Training curves visualization
- ✅ E2E pipeline (Data → Train → Eval)

See [Fine-Tuning Guide](docs/FINETUNING_GUIDE.md) for details.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Mistral Large 2 (via Mistral AI API) |
| **Voice Cloning** | ElevenLabs Instant Voice Cloning |
| **Speech Recognition** | OpenAI Whisper (base model) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Tracking** | W&B Weave + W&B Models |
| **Package Manager** | uv |

## 📁 Project Structure

```
BeWithMe/
├── src/
│   ├── config.py              # Centralized configuration
│   ├── core/                  # Business logic
│   │   ├── voice_cloning.py  # ElevenLabs integration
│   │   ├── conversation.py   # Mistral + personality
│   │   └── asr.py            # Whisper ASR
│   ├── api/                   # FastAPI backend
│   │   ├── main.py           # App entry point
│   │   ├── models.py         # Pydantic models
│   │   └── routes/           # Modular routes
│   ├── frontend/              # Streamlit UI
│   │   └── app.py
│   └── training/              # Fine-tuning (NEW!)
│       ├── data_preparation.py
│       └── mistral_finetuner.py
├── scripts/                   # Launch scripts
├── docs/                      # Documentation
└── tests/                     # Test suite
```

## 🎨 Screenshots

### Main Interface
- **Step 1**: Clone voice from audio sample
- **Step 2**: Create personality profile
- **Step 3**: Start conversation
- **Step 4**: View history & analytics

## 📊 W&B Integration

### Weave Tracing
Every conversation is traced:
```python
import weave
weave.init("be-with-me")

# All Mistral calls automatically traced!
response = agent.generate_response(user_message)
```

### Models Tracking
Fine-tuning experiments logged:
```python
import wandb
wandb.init(project="be-with-me-finetuning")

# Training curves, metrics, artifacts
wandb.log({"loss": 0.42, "accuracy": 0.87})
```

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- **Mistral AI** for the amazing LLMs
- **ElevenLabs** for voice cloning technology
- **Weights & Biases** for ML tooling and hackathon support
- **NVIDIA** for hackathon organization

## 📞 Contact

Built for **NVIDIA Mistral Worldwide Hackathon Singapore** (Feb 28 - March 1, 2026)

---

⭐ **Star this repo** if you find it helpful!

🏆 **Hackathon Judges**: See [DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for evaluation walkthrough
