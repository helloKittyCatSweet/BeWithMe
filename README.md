# 🎙️ BeWithMe - AI 情感陪伴与记忆永续系统

**基于 AI 的音色克隆、个性化对话与区块链存证系统**

在 [NVIDIA Mistral 全球黑客松 2026](https://worldwide-hackathon.mistral.ai/) 中脱颖而出，BeWithMe 致力于通过前沿 AI 技术，让您可以与思念的亲人进行富有情感的对话，并利用区块链技术确保这些珍贵记忆的永恒与权属。

---

## � 黑客松赛道支持

本项目全面覆盖并深度集成了以下赛道：

- ✅ **W&B Fine-Tuning 赛道** - 使用 Mistral 模型进行个性化微调，通过 W&B 追踪实验全过程。
- ✅ **Mistral Agents 赛道** - 构建具备特定人格特质与说话风格的对话智能体。
- ✅ **General 赛道** - 融合音色克隆、ASR 与 LLM 的端到端语音交互系统。
- 🚀 **Web3 扩展** - 创新性地引入区块链技术，解决情感资产的数字所有权与永生命题。

---

## ✨ 核心功能

### 🧠 核心能力
- 🎤 **即时音色克隆** - 仅需 30 秒音频样例，即可通过 ElevenLabs 实现高度还原的音色克隆。
- 🤖 **人格特质建模** - 深度刻画亲人的性格特征、口头禅及情感偏好，创建专属 AI 代理。
- 💬 **自然情感对话** - 由 **Mistral Large 2** 驱动，提供极具共情力且逻辑连贯的对话体验。
- 🎧 **语音交互 (ASR)** - 集成 OpenAI Whisper，支持流畅的语音输入识别。

### 📊 W&B 深度集成 (Fine-Tuning & Eval)
- **Weave 追踪**：全程监控每一条对话链路，优化 Prompt 与模型响应。
- **实验对比**：多版本模型性能直观对比，确保微调效果。
- **Artifacts 管理**：自动化管理数据集、LoRA 权重与评估报告。

![W&B 模型对比](docs/w&b_comparasion.png)

### ⛓️ 区块链存证 (MemoryLock)
- **去中心化存储**：利用 IPFS/Arweave 存储原始素材哈希，确保记忆不因服务商关闭而丢失。
- **数字所有权 (NFT/SFT)**：将模型权重封装为资产，只有特定私钥持有者（家属）可唤醒 AI。
- **智能合约触发**：实现“数字遗嘱”，在特定时刻或通过情感验证后释放遗产或信息。

---

## 🚀 快速开始

### 环境准备
```bash
# Python 3.10+
python --version

# 推荐使用 uv 包管理器
pip install uv
```

### 安装与配置
1. **克隆项目并安装依赖**
```bash
git clone https://github.com/your-repo/BeWithMe.git
cd BeWithMe
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

2. **配置环境变量**
复制 `.env.example` 为 `.env` 并填写您的 API 密钥：
```env
MISTRAL_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
WANDB_API_KEY=your_key
```

### 启动应用
**推荐方式：一键启动**
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```
启动后访问：
- 🎨 **前端 UI**: `http://localhost:8501`
- 🔧 **API 文档**: `http://localhost:8000/docs`

---

## 🎯 W&B 微调工作流

我们提供了一套完整的微调 pipeline，帮助您训练出更具“灵魂”的模型。

```bash
# 1. 准备训练数据
python -m src.training.data_preparation

# 2. 启动 Mistral 微调 (W&B 实时监控)
python -m src.training.mistral_finetuner

# 3. 运行评估并查看 Weave 追踪
./scripts/evaluate_model.sh
```

**为什么选择微调？**
通过微调，模型能够从底层学习到特定人物的语序、语气与情感反馈逻辑，相比单纯的 System Prompt，响应更真实、更具代入感。

---

## 🏗️ 项目架构

```
BeWithMe/
├── src/
│   ├── core/           # 核心逻辑 (ASR, Voice Cloning, Conversation)
│   ├── api/            # FastAPI 后端路由与模型
│   ├── frontend/       # Streamlit 前端应用
│   └── training/       # W&B 微调与数据处理脚本
├── blockchain/         # 智能合约与部署脚本 (Solidity)
├── scripts/            # 自动化运行脚本
├── docs/               # 详细文档与静态资源
└── tests/              # 自动化测试用例
```

---

## 📜 许可说明
本项目基于 MIT 协议开源。请遵循相关伦理规范，在合法合规的前提下使用声音克隆技术。

---

## 🙏 致谢
- **Mistral AI** 提供强大的 LLM 支持
- **Weights & Biases** 提供卓越的实验追踪与评估工具
- **NVIDIA** 组织本次全球黑客松

---
🏆 **Hackathon Judges**: 详细评审路径请参考 [DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
