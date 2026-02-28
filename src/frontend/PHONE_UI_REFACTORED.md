# 📱 Be With Me - Phone UI (Refactored)

## 架构说明

这是一个完全重构的版本，采用了现代化的代码组织结构。

### 为什么重构？

**之前的问题**：
- ❌ CSS 嵌入在 Python 代码中（~400 行）
- ❌ 所有组件混在一个文件中（~700+ 行）
- ❌ 缺少代码复用
- ❌ z-index 层叠关系不正确（垂直排列而非堆叠）

**重构后的改进**：
- ✅ CSS 分离到外部文件（`styles/phone_ui.css`）
- ✅ 组件化架构（`components/phone_components.py`）
- ✅ 工具函数独立（`utils/helpers.py`）
- ✅ 正确的 z-axis 层叠（使用 `position: absolute` + `z-index`）

## 目录结构

```
src/frontend/
├── phone_app.py                    # 主应用（重构版，推荐）
├── phone_call_ui.py                # 基础版（保留）
├── phone_call_ai.py                # AI 版（保留，待重构）
├── components/
│   ├── __init__.py
│   └── phone_components.py         # UI 组件模块
├── utils/
│   ├── __init__.py
│   └── helpers.py                  # 工具函数模块
├── styles/
│   └── phone_ui.css               # 外部样式表
└── PHONE_UI_REFACTORED.md         # 本文档
```

## 文件说明

### 1. phone_app.py - **推荐使用**
**主应用文件**，组件化和模块化的实现。

**特点**：
- ✨ 清晰的代码结构
- ✨ 组件可复用
- ✨ CSS 与代码分离
- ✨ 易于维护和扩展

**启动方式**：
```bash
cd /home/kitty/BeWithMe
streamlit run src/frontend/phone_app.py
```

### 2. components/phone_components.py
**UI 组件模块**，包含所有界面组件。

**组件列表**：
- `PhoneShell`: 手机外壳和屏幕框架
- `StatusBar`: 顶部状态栏
- `ContactCard`: 联系人卡片
- `ContactList`: 联系人列表
- `IncomingCall`: 来电界面
- `ActiveCall`: 通话中界面
- `CallHistory`: 通话记录
- `TabBar`: 底部标签栏

**设计原则**：
- 每个组件都是独立的类
- 使用静态方法 `render()` 渲染
- 返回用户交互结果（点击、输入等）
- 无副作用，状态管理由主应用处理

### 3. utils/helpers.py
**工具函数模块**，包含辅助功能。

**主要函数**：
- `load_css()`: 加载外部 CSS 文件
- `init_session_state()`: 初始化 session state
- `get_sample_contacts()`: 获取示例联系人
- `start_call()`: 开始通话
- `end_call()`: 结束通话
- `add_message()`: 添加消息到对话
- `simulate_agent_response()`: 模拟 AI 响应
- `get_call_duration()`: 获取通话时长
- `save_call_record()`: 保存通话记录

### 4. styles/phone_ui.css
**外部样式表**，所有 CSS 样式集中管理。

**CSS 架构**：
```css
.phone-wrapper {           /* 最外层容器 */
  position: relative;
  width: 420px;
  height: 850px;
}

.phone-container {         /* 手机外壳 */
  position: absolute;
  z-index: 1;              /* 底层 */
}

.phone-screen {            /* 屏幕区域 */
  position: absolute;
  z-index: 2;              /* 中层 */
}

.screen-content {          /* 内容区域 */
  position: relative;
  z-index: 2;
}

.call-screen {             /* 通话遮罩 */
  position: absolute;
  z-index: 100;            /* 顶层 */
}
```

**关键改进**：
- ✅ 使用 `position: absolute` 实现真正的 z-axis 堆叠
- ✅ 不再是垂直排列（之前的错误方式）
- ✅ 所有层级清晰可控
- ✅ 过渡动画和响应式设计

## 使用指南

### 快速开始

1. **确保依赖已安装**：
```bash
cd /home/kitty/BeWithMe
uv sync
```

2. **运行应用**：
```bash
streamlit run src/frontend/phone_app.py
```

3. **浏览器访问**：
```
http://localhost:8501
```

### 功能说明

#### 联系人列表
- 显示预设联系人（妈妈、爸爸、奶奶、爷爷、哥哥）
- 点击"📞 拨打"按钮发起通话

#### 通话界面
- 显示通话时长
- 音频波形动画
- 对话气泡显示
- 支持文本输入和音频上传（占位）
- 挂断按钮结束通话

#### 通话记录
- 显示最近 20 条通话记录
- 记录包含：联系人、时间、时长、消息数
- 支持回拨功能

### 自定义开发

#### 添加新组件

1. 在 `components/phone_components.py` 中添加类：
```python
class MyComponent:
    @staticmethod
    def render(data):
        st.markdown('<div class="my-component">', unsafe_allow_html=True)
        # 渲染逻辑
        st.markdown('</div>', unsafe_allow_html=True)
        return user_action
```

2. 在 `styles/phone_ui.css` 中添加样式：
```css
.my-component {
    /* 样式 */
}
```

3. 在主应用中使用：
```python
from components.phone_components import MyComponent

result = MyComponent.render(data)
```

#### 修改样式

直接编辑 `styles/phone_ui.css` 文件，无需修改 Python 代码。

#### 集成后端 API

修改 `utils/helpers.py` 中的 `simulate_agent_response()` 函数：

```python
def simulate_agent_response(user_message: str) -> str:
    import requests
    
    response = requests.post(
        "http://localhost:8000/voice/simulate-call",
        json={"text": user_message}
    )
    
    return response.json()["response"]
```

## 技术架构

### 前端框架
- **Streamlit**: Web 应用框架
- **HTML/CSS**: 界面渲染
- **Session State**: 状态管理

### z-index 层次结构

```
100: .call-screen (通话遮罩)
 50: .tab-bar (底部标签栏)
 10: .status-bar, .phone-notch (状态栏和刘海)
  2: .phone-screen, .screen-content (屏幕和内容)
  1: .phone-container (手机外壳)
```

### 组件通信
- 组件通过返回值向主应用报告用户交互
- 主应用管理全局状态（`st.session_state`）
- 工具函数处理状态变更逻辑

## 与旧版本对比

### phone_call_ui.py (基础版)
- ✅ 适合快速演示
- ❌ CSS 嵌入代码
- ❌ 组件耦合
- ❌ z-axis 层叠错误

### phone_call_ai.py (AI 版)
- ✅ 有 API 集成
- ✅ 支持音频上传
- ❌ CSS 嵌入代码
- ❌ 组件耦合
- ❌ z-axis 层叠错误

### phone_app.py (重构版) ⭐
- ✅ 代码组织清晰
- ✅ CSS 外部化
- ✅ 组件可复用
- ✅ 正确的 z-axis 层叠
- ✅ 易于维护
- ✅ 易于扩展

## 下一步计划

### 短期 (本周末前)
- [ ] 将 phone_call_ai.py 的 API 集成迁移到新架构
- [ ] 添加音频播放组件
- [ ] 完善错误处理

### 中期 (下周)
- [ ] 集成真实的 Mistral 模型
- [ ] 实现语音克隆功能
- [ ] 添加更多联系人管理功能

### 长期
- [ ] 持久化存储（数据库）
- [ ] 用户认证系统
- [ ] 多用户支持

## 常见问题

### Q: 为什么我看不到手机界面？
A: 检查 CSS 是否正确加载。确保 `styles/phone_ui.css` 文件存在。

### Q: 组件没有正确堆叠怎么办？
A: 检查 CSS 中的 `position` 和 `z-index` 属性。确保父容器使用 `position: relative`，子元素使用 `position: absolute`。

### Q: 如何调试组件？
A: 在组件的 `render()` 方法中添加 `st.write()` 输出调试信息。

### Q: 旧版本还能用吗？
A: 可以，`phone_call_ui.py` 和 `phone_call_ai.py` 仍然可用，但建议迁移到新架构。

## 贡献指南

### 代码规范
- 类名使用 PascalCase
- 函数名使用 snake_case
- 组件使用静态方法
- 添加类型提示
- 编写文档字符串

### 提交规范
- 一次提交只做一件事
- 提交信息清晰明了
- 大的改动提前讨论

## License

MIT License - 自由使用和修改

## 联系方式

项目：Be With Me - NVIDIA Mistral Hackathon Singapore
日期：2026 年 2 月 28 日 - 3 月 1 日
开发者：独狼（Solo Dev）

---

**注意**：这是一个重构版本，专注于代码质量和可维护性。如果你需要快速原型，可以使用旧版本；如果你想要专业的代码结构，请使用这个版本。
