# 🎯 Be With Me - 完整的前后端集成指南

## 📋 系统架构

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                  │
│  🎤 Clone Voice | 🤖 Create Agent | 💬 Chat | 📊 History │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP REST API
┌────────────────────────┴─────────────────────────────────┐
│                      Backend (FastAPI)                    │
│  /voice/clone | /agent/create | /chat/text | /simulate-call │
└────────────────────────┬─────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌─────▼─────┐ ┌───────▼───────┐
│  ElevenLabs   │ │  Mistral  │ │    Whisper    │
│ Voice Cloning │ │    LLM    │ │      ASR      │
└───────────────┘ └───────────┘ └───────────────┘
```

---

## ✅ 完整功能清单

### 1. 音色克隆 (Voice Cloning)
- ✅ 上传音频文件 (30-60秒, MP3/WAV)
- ✅ ElevenLabs Instant Voice Cloning
- ✅ 生成 Voice ID
- ✅ 自动保存到系统状态

### 2. 对话代理 (Conversation Agent)
- ✅ 自定义角色 (姓名、关系、性格)
- ✅ 设置说话习惯和口头禅
- ✅ Mistral Large 2 生成对话
- ✅ 保持对话历史记忆

### 3. 文本对话 (Text Chat)
- ✅ 实时文本对话
- ✅ 对话历史显示
- ✅ 可选语音合成 (TTS)
- ✅ 清空历史记录

### 4. 语音通话 (Voice Call) ⭐
- ✅ 上传录音
- ✅ ASR 语音识别 (Whisper)
- ✅ LLM 生成回复 (Mistral)
- ✅ TTS 语音合成 (克隆音色)
- ✅ 播放 AI 语音回复
- ✅ 完整流程 5-10 秒

---

## 🚀 快速启动

### 1. 启动后端
```bash
cd /home/kitty/BeWithMe

# 激活环境
source .venv/bin/activate

# 启动服务
sh start_all.sh

# 或手动启动
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在: `http://localhost:8000`

### 2. 启动前端
```bash
# 新终端窗口
cd /home/kitty/BeWithMe
source .venv/bin/activate

# 启动 Streamlit
streamlit run src/frontend/app.py --server.port 8501
```

前端将运行在: `http://localhost:8501`

### 3. 验证连接
```bash
# 测试后端
curl http://localhost:8000/

# 测试前端
curl http://localhost:8501/
```

---

## 🔧 集成测试

### 运行完整测试
```bash
# 基础测试 (不包含音频)
python test_integration.py

# 完整测试 (包含音色克隆和通话)
python test_integration.py /path/to/your/audio.mp3
```

### 测试覆盖
1. ✅ 后端连接测试
2. ✅ 系统状态测试
3. ✅ 创建对话代理
4. ✅ 文本对话测试
5. ✅ 音色克隆测试 (需音频)
6. ✅ 语音合成测试 (需音频)
7. ✅ 完整通话测试 (需音频)

---

## 📖 使用流程

### Step 1: 克隆音色 (Clone Voice)
1. 打开前端 Tab "🎤 Clone Voice"
2. 输入音色名称 (例如: "奶奶的声音")
3. 上传 30-60 秒清晰录音
4. 点击 "🚀 Clone Voice"
5. 等待 5-10 秒
6. 获得 Voice ID (自动保存)

**要求:**
- 音频格式: MP3 或 WAV
- 时长: 30-60 秒
- 质量: 清晰、无背景噪音
- 内容: 自然说话，包含情感

### Step 2: 创建对话代理 (Create Agent)
1. 打开 Tab "🤖 Create Agent"
2. 填写信息:
   - 名称: "李奶奶"
   - 关系: "奶奶"
   - 性格: "慈祥温柔，总是关心健康"
   - 口头禅: ["孩子", "多吃饭", "注意身体"]
3. 点击 "🎯 Create Agent"
4. 等待 1-2 秒

### Step 3: 开始对话

#### 方式 A: 文本对话
1. 打开 Tab "💬 Chat"
2. 选择 "💬 Text Chat"
3. 输入消息: "奶奶，我今天考试考得很好！"
4. 点击 "📤 Send" (纯文本)
5. 或点击 "🔊 TTS" (生成语音)

#### 方式 B: 语音通话 ⭐
1. 打开 Tab "💬 Chat"
2. 选择 "🎙️ Voice Chat"
3. 上传你的录音 (说 "奶奶，我想你了")
4. 点击 "🚀 Send Voice Message"
5. 等待 10-15 秒
6. 查看识别结果 + AI 回复文本
7. 播放 AI 语音 (用克隆的音色)

---

## 🔌 API 端点

### 系统端点
```bash
GET  /              # 健康检查
GET  /status        # 系统状态
GET  /docs          # API 文档 (Swagger UI)
```

### 音色克隆
```bash
POST /voice/clone              # 克隆音色
GET  /voice/list               # 列出所有音色
DELETE /voice/{voice_id}       # 删除音色
POST /voice/quick-tts          # 快速 TTS
POST /voice/simulate-call      # 模拟通话 ⭐
```

### 对话代理
```bash
POST /agent/create    # 创建代理
GET  /agent/current   # 获取当前代理
POST /agent/reset     # 重置代理
```

### 对话
```bash
POST /chat/text      # 文本对话
POST /chat/voice     # 语音对话
GET  /chat/history   # 获取历史
POST /chat/clear     # 清空历史
```

---

## 🔍 调试技巧

### 1. 查看后端日志
```bash
# 查看实时日志
tail -f /tmp/backend.log  # 如果使用 start_all.sh

# 或直接运行查看输出
uvicorn src.api.main:app --reload
```

### 2. 测试单个端点
```bash
# 测试状态
curl http://localhost:8000/status | jq

# 测试创建代理
curl -X POST http://localhost:8000/agent/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试",
    "relationship": "奶奶",
    "personality_traits": "温柔",
    "speech_patterns": ["孩子"]
  }' | jq

# 测试文本对话
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "use_voice": false}' | jq
```

### 3. 前端调试
```bash
# 在浏览器开发者工具中查看网络请求
# F12 → Network → XHR/Fetch

# 查看 Streamlit 日志
streamlit run src/frontend/app.py --logger.level=debug
```

---

## ⚠️ 常见问题

### 问题 1: 后端连接失败
**症状**: 前端显示 "❌ Connection Failed"

**解决方案**:
```bash
# 检查后端是否运行
curl http://localhost:8000/

# 检查端口占用
lsof -i :8000

# 重启后端
sh start_all.sh
```

### 问题 2: 音色克隆失败
**症状**: "❌ 音色克隆失败"

**解决方案**:
1. 检查 ElevenLabs API Key:
```bash
grep ELEVENLABS_API_KEY .env
```
2. 确保音频格式正确 (MP3/WAV)
3. 音频质量清晰、无背景噪音
4. 检查 API 配额 (Free 版限 10 个音色)

### 问题 3: 对话没有回复
**症状**: 发送消息后无响应

**解决方案**:
1. 确保已创建 Agent:
```bash
curl http://localhost:8000/status
```
2. 检查 Mistral API Key:
```bash
grep MISTRAL_API_KEY .env
```
3. 查看后端日志

### 问题 4: 语音通话超时
**症状**: "⏱️ Request timeout"

**原因**: 音频太长或首次加载 Whisper 模型

**解决方案**:
1. 使用较短的录音 (5-10 秒)
2. 等待 Whisper 模型加载完成 (首次需要 1-2 分钟)
3. 增加 timeout 设置

### 问题 5: Whisper 模型加载失败
**症状**: ImportError 或 model loading error

**解决方案**:
```bash
# 重新安装依赖
source .venv/bin/activate
uv pip install openai-whisper torch

# 手动下载模型
python -c "import whisper; whisper.load_model('base')"
```

---

## 📊 性能优化

### 1. 加速 ASR
```python
# 在 .env 中设置更小的模型
WHISPER_MODEL=tiny  # 最快 (原来是 base)
```

### 2. 加速 TTS
```python
# 已使用 eleven_turbo_v2 (最快的模型)
# src/core/voice_cloning.py 中已配置
```

### 3. 减少延迟
- 使用本地 GPU (如果有)
- 预加载模型
- 使用流式响应 (WebSocket)

---

## 🎯 黑客松展示建议

### 演示脚本 (5 分钟)

1. **开场** (30 秒)
   - "想和已故的亲人再说说话吗？"
   - 展示界面

2. **克隆音色** (1 分钟)
   - 播放原始录音 10 秒
   - 上传 → 获得 Voice ID
   - 强调: "30 秒即可克隆"

3. **创建代理** (30 秒)
   - 输入奶奶的性格特征
   - 点击创建

4. **文本对话** (1 分钟)
   - 输入: "奶奶，我想你了"
   - AI 回复: "(奶奶的性格化回复)"
   - 点击 TTS 生成语音

5. **语音通话** (2 分钟) ⭐
   - 上传录音: "奶奶，我今天工作很累"
   - 等待 10 秒
   - 展示识别结果
   - 播放 AI 语音回复 (克隆的音色)

6. **总结** (1 分钟)
   - 技术栈: Mistral + ElevenLabs + Whisper
   - 社会价值: 情感陪伴、疗愈、怀旧
   - 未来规划: 视频通话、实时对话

---

## 📚 相关文档

- [完整功能指南](docs/SIMULATE_CALL_GUIDE.md)
- [Fine-tuning 指南](docs/FINETUNING_GUIDE.md)
- [API 文档](http://localhost:8000/docs)

---

## 🎉 总结

现在你拥有一个**完全打通的、专业的前后端系统**:

✅ **前端**: Streamlit 完整 UI (4 个 Tab)  
✅ **后端**: FastAPI 完整 API (9 个端点)  
✅ **核心功能**: 音色克隆 + 对话代理 + 文本/语音通话  
✅ **测试工具**: 自动化集成测试脚本  
✅ **文档**: 完整的使用指南

**立即开始使用:**
```bash
# 1. 启动后端
sh start_all.sh

# 2. 启动前端
streamlit run src/frontend/app.py

# 3. 打开浏览器
# http://localhost:8501

# 4. 运行测试
python test_integration.py
```

**祝黑客松顺利！🚀**
