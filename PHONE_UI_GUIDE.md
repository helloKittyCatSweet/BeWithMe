# 📱 手机通话界面使用指南

## 快速开始

```bash
cd /home/kitty/BeWithMe

# 方式 1: 直接运行 Streamlit
streamlit run src/frontend/phone_call_simple.py

# 方式 2: 使用启动脚本
./scripts/start_phone_ui.sh
```

## 三个版本对比

### 1️⃣ phone_call_simple.py - **推荐用于演示**
✅ **最简单**：无需任何外部依赖  
✅ **文本输入**：使用文本框代替语音录制  
✅ **快捷回复**：预设常用问候语  
✅ **完整UI**：所有界面元素都包含  
✅ **模拟对话**：内置智能回复逻辑  

**适用场景**：
- Hackathon 现场演示
- 快速原型验证
- UI/UX 测试
- 无需真实 AI 的场景

**启动命令**：
```bash
streamlit run src/frontend/phone_call_simple.py
```

---

### 2️⃣ phone_call_ui.py - 基础完整版
✅ 完整 iPhone 风格界面  
✅ 所有核心功能  
✅ 无额外依赖  
❌ 使用占位数据  

**适用场景**：
- 界面设计展示
- 不需要AI对话的演示
- 快速功能验证

**启动命令**：
```bash
streamlit run src/frontend/phone_call_ui.py
```

---

### 3️⃣ phone_call_ai.py - AI 集成版
✅ 真实语音录制（需要浏览器麦克风权限）  
✅ 后端 API 集成  
✅ 真实 AI 对话  
⚠️ 需要额外依赖：`audio-recorder-streamlit`  
⚠️ 需要后端服务运行  

**适用场景**：
- 完整功能演示
- 集成测试
- 生产环境

**启动命令**：
```bash
# 安装依赖
uv pip install audio-recorder-streamlit==0.0.8

# 启动后端 (终端 1)
uvicorn src.api.main:app --reload

# 启动前端 (终端 2)
streamlit run src/frontend/phone_call_ai.py
```

---

## 功能完整对比表

| 功能 | simple | ui | ai |
|-----|--------|----|----|
| iPhone 界面 | ✅ | ✅ | ✅ |
| 联系人列表 | ✅ | ✅ | ✅ |
| 通话模拟 | ✅ | ✅ | ✅ |
| 实时计时器 | ✅ | ✅ | ✅ |
| 对话气泡 | ✅ | ✅ | ✅ |
| 通话记录 | ✅ | ✅ | ✅ |
| 音频波形动画 | ✅ | ✅ | ✅ |
| 文本输入 | ✅ | ❌ | ❌ |
| 快捷回复 | ✅ | ❌ | ✅ |
| 智能响应 | ✅ (模拟) | ❌ | ✅ (真实) |
| 语音录制 | ❌ | ❌ | ✅ |
| 后端 API | ❌ | ❌ | ✅ |
| 额外依赖 | 无 | 无 | audio-recorder |

---

## Hackathon 演示建议

### 📋 推荐流程

#### 阶段 1: UI 展示 (3分钟)
**使用**: `phone_call_simple.py`

1. 打开界面，展示 iPhone 风格设计
2. 浏览联系人列表（妈妈、爸爸、奶奶、爷爷）
3. 点击一个联系人，展示来电界面
4. 接听通话，展示通话中界面：
   - 实时计时器
   - 音频波形动画
   - 联系人头像

#### 阶段 2: 对话演示 (4分钟)
**继续使用**: `phone_call_simple.py`

1. 使用快捷回复：
   - "你好吗？" → 观察 AI 响应
   - "最近怎么样？" → 自然对话流
   - "想你了" → 情感回应

2. 手动输入测试：
   - 输入自定义问题
   - 展示对话气泡
   - 滚动查看历史消息

3. 挂断通话：
   - 点击挂断按钮
   - 自动跳转到通话记录

#### 阶段 3: 功能完整性 (2分钟)
**仍在**: `phone_call_simple.py`

1. 查看通话记录：
   - 时间戳
   - 通话时长
   - 消息数量

2. 快速回拨功能演示

#### 阶段 4: 技术亮点 (1分钟)
**切换到**: `phone_call_ai.py`（如果时间充裕）

1. 展示真实语音录制
2. 说明后端 AI 集成
3. 强调可扩展性

---

## 🎯 Saturday Presentation 准备清单

### 必做项
- [ ] 测试 `phone_call_simple.py` 所有功能
- [ ] 准备 3-4 个对话示例
- [ ] 确保界面流畅（无卡顿）
- [ ] 准备备用方案（如果 Streamlit 崩溃）
- [ ] 截屏关键界面（备用展示）

### 可选项
- [ ] 录制演示视频（以防现场网络问题）
- [ ] 准备 PPT 补充技术说明
- [ ] 测试不同浏览器兼容性
- [ ] 准备真实 AI 集成版本演示

### 技术亮点话术准备
1. **UI 设计**: "我们模拟了 iPhone 的真实通话界面，提供沉浸式体验"
2. **情感智能**: "AI 不仅理解语义，还能捕捉情感语调"
3. **关系验证**: "通过严格的身份验证，防止技术滥用"
4. **语音克隆**: "基于 ElevenLabs 的高保真语音克隆技术"
5. **本地微调**: "支持 Mistral 本地微调，保护用户隐私"

---

## 🚀 快速启动命令

### 最简单方式（推荐）
```bash
cd /home/kitty/BeWithMe
streamlit run src/frontend/phone_call_simple.py
```

### 使用脚本
```bash
cd /home/kitty/BeWithMe
./scripts/start_phone_ui.sh
# 选择选项 1
```

### 在特定端口启动
```bash
streamlit run src/frontend/phone_call_simple.py --server.port 8502
```

### 开启外网访问（演示用）
```bash
streamlit run src/frontend/phone_call_simple.py \
  --server.address 0.0.0.0 \
  --server.port 8501
```

---

## 🔧 故障排除

### 问题 1: Streamlit 启动失败
```bash
# 检查是否安装
python -c "import streamlit"

# 重新安装
uv pip install streamlit==1.31.0
```

### 问题 2: 界面样式错乱
- 清除浏览器缓存（Ctrl + Shift + Delete）
- 使用无痕模式重新打开
- 尝试不同浏览器（Chrome 推荐）

### 问题 3: 无法访问
```bash
# 检查端口占用
lsof -i :8501

# 使用其他端口
streamlit run src/frontend/phone_call_simple.py --server.port 8502
```

### 问题 4: 界面卡顿
- 关闭其他占用资源的应用
- 减少浏览器标签页数量
- 重启 Streamlit 服务

---

## 📞 测试对话示例

### 温馨问候场景
```
你: 你好吗？
AI: 我很好呀，妈妈想你了！你最近过得怎么样？

你: 最近工作有点忙
AI: 最近啊，我每天都在想你。你要好好照顾自己，多穿衣服。
```

### 关心身体场景
```
你: 您身体还好吗？
AI: 我身体挺好的，就是有点想你。你呢？工作不要太累了。

你: 我会注意的
AI: 好的好的，我听你说。有什么事都可以跟我讲。
```

### 情感表达场景
```
你: 我想你了
AI: 我也想你呀，宝贝。有空常回来看看。

你: 好的，我会的
AI: 好的好的，我听你说。有什么事都可以跟我讲。
```

---

## 🎨 界面特色功能

### 1. iPhone 风格设计
- 刘海屏模拟
- 圆角边框
- 状态栏（时间、信号、电量）
- 深色渐变背景

### 2. 流畅动画
- 头像脉冲效果（2秒循环）
- 音频波形律动（5个垂直条）
- 消息气泡滑入效果
- 按钮悬停反馈

### 3. 智能交互
- 自动计时器刷新
- 快捷回复按钮
- 历史记录追踪
- 一键回拨功能

### 4. 响应式布局
- 适配不同屏幕尺寸
- 触摸友好的按钮
- 清晰的视觉层级
- 无障碍设计考虑

---

## 📈 未来扩展方向

1. **真实语音集成** ✅ 已实现 (phone_call_ai.py)
2. **多人通话**: 支持群组对话
3. **视频通话**: 添加视频界面
4. **消息存档**: 持久化对话历史
5. **情感分析**: 实时情绪检测
6. **多语言**: 支持方言和外语
7. **AR 体验**: 结合增强现实技术
8. **可穿戴设备**: 智能手表版本

---

## 📝 License & Credits

**Project**: Be With Me  
**Hackathon**: NVIDIA Mistral Worldwide Hackathon Singapore 2026  
**Presentation**: Saturday Morning  
**Developer**: 独狼 (Lone Wolf) 🐺  

**Tech Stack**:
- Frontend: Streamlit 1.31.0
- Backend: FastAPI 0.109.0
- AI: Mistral AI + ElevenLabs
- Database: SQLAlchemy 2.0.25

---

**Good luck with the presentation! 加油！🚀**
