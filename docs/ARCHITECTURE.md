# 📂 项目结构说明

## 新的项目组织结构

```
BeWithMe/
├── src/                            # ⭐ 源代码目录
│   ├── __init__.py
│   ├── config.py                  # 配置中心（所有配置的统一管理）
│   │
│   ├── core/                       # 核心业务模块
│   │   ├── __init__.py
│   │   ├── voice_cloning.py       # ElevenLabs 音色克隆
│   │   ├── conversation.py        # Mistral 对话生成
│   │   └── asr.py                 # Whisper 语音识别
│   │
│   ├── api/                        # FastAPI 后端应用
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 主应用
│   │   ├── models.py              # Pydantic 数据模型
│   │   │
│   │   └── routes/                # API 路由（模块化）
│   │       ├── __init__.py
│   │       ├── voice.py           # 音色克隆路由
│   │       ├── conversation.py    # 对话代理路由
│   │       └── chat.py            # 聊天路由
│   │
│   └── frontend/                   # Streamlit 前端应用
│       ├── __init__.py
│       └── app.py                 # 前端应用
│
├── tests/                          # 测试目录（可扩展）
│   ├── __init__.py
│   ├── test_core.py               # 核心模块测试
│   ├── test_api.py                # API 测试
│   └── test_integration.py        # 集成测试
│
├── docs/                           # 文档目录
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DEMO_GUIDE.md
│   └── ARCHITECTURE.md            # 架构文档
│
├── scripts/                        # 辅助脚本
│   ├── run_backend.sh            # 启动后端
│   ├── run_frontend.sh           # 启动前端
│   └── run_all.sh                # 启动全部
│
├── config/                         # 配置文件目录
│   ├── .env.example              # 环境变量模板
│   └── logging.yaml              # 日志配置（预留）
│
├── sample_audio/                   # 音频样本目录
│   ├── README.md
│   ├── voice_samples/            # 音色克隆样本
│   └── test_inputs/              # 测试输入
│
├── .venv/                          # Python 虚拟环境
├── pyproject.toml                  # 项目配置（uv）
├── requirements.txt                # 依赖列表
├── .gitignore                      # Git 忽略规则
└── 其他文档...
```

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────┐
│   Frontend Layer            │  📱 Streamlit Web UI
│   (src/frontend/app.py)     │
└────────────┬────────────────┘
             │
        HTTP │ REST API
             │
┌────────────▼────────────────┐
│   API Layer                 │  🔌 FastAPI Routes
│   (src/api/)                │     - routes/voice.py
│                             │     - routes/conversation.py
│                             │     - routes/chat.py
│                             │     - models.py
└────────────┬────────────────┘
             │
    Imports  │ Python
             │
┌────────────▼────────────────┐
│   Business Layer            │  🧠 核心逻辑
│   (src/core/)               │     - voice_cloning.py
│                             │     - conversation.py
│                             │     - asr.py
└────────────┬────────────────┘
             │
   Imports   │ Python
             │
┌────────────▼────────────────┐
│   Configuration             │  ⚙️ src/config.py
│                             │     - API 密钥
│                             │     - 模型参数
│                             │     - 应用设置
└─────────────────────────────┘
```

### 依赖关系

```
frontend/app.py
    ↓ (requests HTTP)
api/main.py
    ├── api/routes/voice.py
    │   └── core/voice_cloning.py ← config.py
    ├── api/routes/conversation.py
    │   └── core/conversation.py ← config.py
    └── api/routes/chat.py
        ├── core/conversation.py ← config.py
        ├── core/asr.py ← config.py
        └── core/voice_cloning.py ← config.py
```

## 🎯 主要改进

### ✅ 已完成

1. **清晰的目录结构**
   - 核心逻辑与 API 分离
   - 前后端完全解耦
   - 便于维护和扩展

2. **模块化路由设计**
   - API 路由分开到 `routes/` 目录
   - 每个功能独立的 `.py` 文件
   - 易于添加新端点

3. **统一的配置管理**
   - 所有配置在 `src/config.py`
   - 环境变量统一读取
   - 易于管理多环境配置

4. **数据模型标准化**
   - 单独的 `src/api/models.py`
   - 所有请求/响应用 Pydantic 定义
   - 自动生成 API 文档

5. **独立的启动脚本**
   - `scripts/run_backend.sh` - 启动后端
   - `scripts/run_frontend.sh` - 启动前端
   - `scripts/run_all.sh` - 一键启动全部

## 🚀 后续扩展点

### 前端扩展
```
src/frontend/
├── app.py              # 主应用
├── pages/              # 多页面应用
│   ├── home.py
│   ├── settings.py
│   └── history.py
└── components/         # 可重用组件
    ├── chat_widget.py
    ├── voice_recorder.py
    └── status_panel.py
```

### 后端扩展
```
src/api/routes/
├── voice.py           # ✅ 已有
├── conversation.py    # ✅ 已有
├── chat.py            # ✅ 已有
├── user.py            # 🚧 用户管理
├── history.py         # 🚧 对话历史存储
├── analytics.py       # 🚧 数据分析
└── admin.py           # 🚧 后台管理
```

### 数据库集成
```
src/
├── database/
│   ├── models.py      # SQLAlchemy 模型
│   ├── crud.py        # 数据库操作
│   └── schemas.py     # SQLAlchemy Schemas
└── migrations/        # 数据库迁移（Alembic）
```

### 测试覆盖
```
tests/
├── test_core/
│   ├── test_voice_cloning.py
│   ├── test_conversation.py
│   └── test_asr.py
├── test_api/
│   ├── test_voice_routes.py
│   ├── test_conversation_routes.py
│   └── test_chat_routes.py
└── conftest.py        # pytest 配置
```

## 📦 使用新结构

### 启动应用

**方式 1: 后端 + 前端分开启动**
```bash
# 终端 1 - 后端
chmod +x scripts/run_backend.sh
./scripts/run_backend.sh

# 终端 2 - 前端
chmod +x scripts/run_frontend.sh
./scripts/run_frontend.sh
```

**方式 2: 一键启动**
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

**方式 3: 手动启动**
```bash
source .venv/bin/activate

# 后端
python -m uvicorn src.api.main:app --reload

# 前端（新终端）
streamlit run src/frontend/app.py
```

### 导入模块

```python
# 旧方式
from voice_cloning import VoiceCloner
from conversation import ConversationAgent
from asr import WhisperASR

# 新方式
from src.core.voice_cloning import VoiceCloner
from src.core.conversation import ConversationAgent
from src.core.asr import WhisperASR

# 或者（相对导入）
from ..core.voice_cloning import VoiceCloner
```

## 📊 文件大小对比

| 项 | 旧结构 | 新结构 | 改进 |
|----|--------|--------|------|
| 根目录文件数 | 15+ | 5 | 清晰 70% |
| 代码组织 | 扁平 | 分层 | ✅ |
| 路由模块化 | 否 | 是 | ✅ |
| 配置管理 | 分散 | 统一 | ✅ |
| 扩展难度 | 高 | 低 | ✅ |

## 🎓 学习资源

- FastAPI 进阶：模块化路由 → `src/api/routes/`
- Streamlit 组件化 → 预留 `src/frontend/pages/`
- Python 包管理：从 `requirements.txt` → `pyproject.toml`

---

**现在项目更清晰了，可以专注于功能开发！🚀**
