"""
Be With Me - 完整功能的手机通话界面
Full-featured Phone Call UI with AI Integration
"""
import streamlit as st
import requests
import base64
import time
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import io

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="📱 Be With Me - AI 语音通话",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# CSS 样式（复用之前的样式）
st.markdown("""
<style>
/* 全局样式 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 手机外壳 */
.phone-container {
    max-width: 420px;
    margin: 20px auto;
    background: #1a1a1a;
    border-radius: 50px;
    padding: 18px;
    box-shadow: 
        0 20px 60px rgba(0,0,0,0.6),
        inset 0 0 0 2px rgba(255,255,255,0.1);
    position: relative;
}

/* 刘海屏 */
.phone-notch {
    position: absolute;
    top: 15px;
    left: 50%;
    transform: translateX(-50%);
    width: 180px;
    height: 28px;
    background: #0a0a0a;
    border-radius: 0 0 18px 18px;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
}

.speaker {
    width: 60px;
    height: 4px;
    background: #333;
    border-radius: 2px;
    margin-top: -10px;
}

/* 手机屏幕 */
.phone-screen {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
    border-radius: 38px;
    padding: 50px 20px 30px 20px;
    min-height: 750px;
    position: relative;
    overflow: hidden;
}

/* 状态栏 */
.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    font-size: 13px;
    margin-bottom: 25px;
    padding: 0 15px;
    font-weight: 500;
}

.status-left, .status-right {
    display: flex;
    gap: 8px;
    align-items: center;
}

/* 来电界面 */
.call-screen {
    text-align: center;
    padding: 50px 20px;
    color: #fff;
}

.contact-avatar {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    margin: 40px auto;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 70px;
    box-shadow: 
        0 15px 40px rgba(102, 126, 234, 0.5),
        0 0 0 10px rgba(102, 126, 234, 0.1);
    animation: pulse 2s infinite ease-in-out;
    position: relative;
}

.contact-avatar::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 3px solid rgba(102, 126, 234, 0.6);
    animation: ripple 2s infinite ease-out;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

@keyframes ripple {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    100% {
        transform: scale(1.5);
        opacity: 0;
    }
}

.contact-name {
    font-size: 36px;
    font-weight: 600;
    margin: 25px 0 15px 0;
    color: #fff;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.contact-subtitle {
    font-size: 16px;
    color: #999;
    margin-bottom: 10px;
}

.call-status {
    font-size: 20px;
    color: #667eea;
    margin-bottom: 50px;
    animation: blink 1.5s infinite;
}

@keyframes blink {
    0%, 50%, 100% { opacity: 1; }
    25%, 75% { opacity: 0.5; }
}

/* 通话中界面 */
.in-call-screen {
    text-align: center;
    padding: 40px 20px;
}

.call-timer {
    font-size: 52px;
    font-weight: 200;
    color: #fff;
    margin: 35px 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    letter-spacing: 2px;
}

/* 音频波形动画 */
.audio-wave {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    gap: 10px;
    margin: 50px 0;
}

.wave-bar {
    width: 8px;
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    animation: wave 1.2s ease-in-out infinite;
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

.wave-bar:nth-child(1) { height: 25px; animation-delay: 0s; }
.wave-bar:nth-child(2) { height: 45px; animation-delay: 0.1s; }
.wave-bar:nth-child(3) { height: 70px; animation-delay: 0.2s; }
.wave-bar:nth-child(4) { height: 60px; animation-delay: 0.3s; }
.wave-bar:nth-child(5) { height: 35px; animation-delay: 0.4s; }
.wave-bar:nth-child(6) { height: 60px; animation-delay: 0.5s; }
.wave-bar:nth-child(7) { height: 70px; animation-delay: 0.6s; }
.wave-bar:nth-child(8) { height: 45px; animation-delay: 0.7s; }
.wave-bar:nth-child(9) { height: 25px; animation-delay: 0.8s; }

@keyframes wave {
    0%, 100% { transform: scaleY(0.8); opacity: 0.7; }
    50% { transform: scaleY(1.6); opacity: 1; }
}

/* 对话气泡 */
.conversation-bubbles {
    max-height: 300px;
    overflow-y: auto;
    padding: 20px 15px;
    margin: 20px 0;
}

.bubble {
    margin: 12px 0;
    padding: 12px 18px;
    border-radius: 18px;
    max-width: 80%;
    word-wrap: break-word;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.bubble-user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    margin-left: auto;
    text-align: right;
    border-bottom-right-radius: 4px;
}

.bubble-agent {
    background: rgba(255,255,255,0.1);
    color: #fff;
    margin-right: auto;
    text-align: left;
    border-bottom-left-radius: 4px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* 控制按钮面板 */
.controls-panel {
    padding: 25px 15px;
    margin-top: 30px;
}

.control-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
    margin-bottom: 30px;
}

.control-item {
    text-align: center;
}

.control-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px auto;
    font-size: 24px;
    transition: all 0.3s;
    cursor: pointer;
}

.control-circle:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.1);
}

.control-circle.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
}

.control-label {
    font-size: 12px;
    color: #999;
}

.btn-end-call {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff4757 0%, #d63031 100%);
    border: none;
    color: #fff;
    font-size: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    cursor: pointer;
    box-shadow: 
        0 8px 20px rgba(255, 71, 87, 0.4),
        inset 0 -2px 5px rgba(0,0,0,0.2);
    transition: all 0.3s;
}

.btn-end-call:hover {
    transform: scale(1.1);
    box-shadow: 0 10px 25px rgba(255, 71, 87, 0.6);
}

/* 联系人卡片 */
.contact-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 18px;
    transition: all 0.3s;
    cursor: pointer;
}

.contact-card:hover {
    background: rgba(255,255,255,0.1);
    transform: translateX(5px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
}

.contact-card-avatar {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}

.contact-card-info {
    flex: 1;
}

.contact-card-name {
    color: #fff;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 4px;
}

.contact-card-detail {
    color: #999;
    font-size: 14px;
}

/* 加载动画 */
.loading-dots {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin: 20px 0;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #667eea;
    animation: bounce 1.4s infinite ease-in-out;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* 隐藏 Streamlit 元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# 初始化 session state
def init_session_state():
    defaults = {
        'call_state': 'idle',  # idle, ringing, connecting, talking, ending
        'call_start_time': None,
        'current_contact': None,
        'conversation': [],
        'call_history': [],
        'contacts': [
            {'name': '妈妈', 'avatar': '👩', 'relationship': 'parent', 'agent_id': 1},
            {'name': '爸爸', 'avatar': '👨', 'relationship': 'parent', 'agent_id': 2},
            {'name': '奶奶', 'avatar': '👵', 'relationship': 'grandparent', 'agent_id': 3},
            {'name': '爷爷', 'avatar': '👴', 'relationship': 'grandparent', 'agent_id': 4},
        ],
        'current_tab': 'contacts',
        'is_muted': False,
        'is_speaker': True,
        'is_recording': False,
        'last_audio': None,
        'ai_speaking': False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def format_time(seconds):
    """格式化通话时间"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def get_call_duration():
    """获取通话时长"""
    if st.session_state.call_start_time:
        return int(time.time() - st.session_state.call_start_time)
    return 0

def simulate_ai_response(user_message):
    """模拟 AI 响应（实际应调用后端 API）"""
    try:
        # 调用后端 API
        response = requests.post(
            f"{API_BASE_URL}/voice/simulate-call",
            json={
                "user_message": user_message,
                "agent_name": st.session_state.current_contact['name'],
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '抱歉，我没听清楚。')
        else:
            return "抱歉，我现在有点不舒服，稍后再聊好吗？"
    except Exception as e:
        print(f"API调用失败: {e}")
        return "网络不太好，我没听清楚，你能再说一遍吗？"

def render_status_bar():
    """渲染状态栏"""
    current_time = datetime.now().strftime("%H:%M")
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-left">
            <span>📶</span>
            <span>5G</span>
        </div>
        <div>{current_time}</div>
        <div class="status-right">
            <span>{"🔋" if datetime.now().minute % 2 == 0 else "🔌"}</span>
            <span>85%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ringing_screen():
    """来电/正在呼叫界面"""
    contact = st.session_state.current_contact
    
    st.markdown(f"""
    <div class="call-screen">
        <div class="contact-avatar">{contact['avatar']}</div>
        <div class="contact-name">{contact['name']}</div>
        <div class="contact-subtitle">{contact['relationship']}</div>
        <div class="call-status">{"来电中..." if st.session_state.call_state == 'ringing' else "正在连接..."}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.call_state == 'ringing':
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("❌ 拒绝", use_container_width=True, type="secondary"):
                st.session_state.call_state = 'idle'
                st.session_state.current_tab = 'contacts'
                st.rerun()
        
        with col3:
            if st.button("✅ 接听", use_container_width=True, type="primary"):
                st.session_state.call_state = 'talking'
                st.session_state.call_start_time = time.time()
                st.session_state.conversation = []
                # AI 主动问候
                greeting = f"喂？是我，{contact['name']}，想你了。"
                st.session_state.conversation.append(('agent', greeting))
                st.rerun()
    
    else:  # connecting
        # 3秒后自动转为通话中
        time.sleep(1)
        st.session_state.call_state = 'talking'
        st.session_state.call_start_time = time.time()
        st.rerun()

def render_talking_screen():
    """通话中界面"""
    contact = st.session_state.current_contact
    duration_text = format_time(get_call_duration())
    
    st.markdown(f"""
    <div class="in-call-screen">
        <div class="contact-avatar" style="width: 100px; height: 100px; font-size: 50px; margin: 20px auto;">
            {contact['avatar']}
        </div>
        <div class="contact-name" style="font-size: 26px; margin: 15px 0;">
            {contact['name']}
        </div>
        <div class="call-timer">{duration_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 音频波形
    if st.session_state.ai_speaking or st.session_state.is_recording:
        st.markdown("""
        <div class="audio-wave">
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
            <div class="wave-bar"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # 对话记录
    if st.session_state.conversation:
        st.markdown('<div class="conversation-bubbles">', unsafe_allow_html=True)
        for role, message in st.session_state.conversation[-6:]:  # 只显示最近6条
            bubble_class = "bubble-user" if role == "user" else "bubble-agent"
            st.markdown(f'<div class="bubble {bubble_class}">{message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 控制面板
    st.markdown('<div class="controls-panel">', unsafe_allow_html=True)
    
    # 输入方式选择
    input_method = st.radio("输入方式", ["💬 文本输入", "🎤 上传音频文件"], horizontal=True, label_visibility="collapsed")
    
    if input_method == "💬 文本输入":
        # 文本输入
        user_input = st.text_input("说点什么...", key="text_input", placeholder="输入消息...")
        
        if st.button("发送 📤", key="send_text") and user_input:
            st.session_state.conversation.append(('user', user_input))
            
            # 调用 AI API
            with st.spinner("对方正在输入..."):
                ai_response = call_ai_api(user_input, contact['name'])
            
            st.session_state.conversation.append(('agent', ai_response))
            st.rerun()
    
    else:
        # 音频文件上传
        audio_file = st.file_uploader("上传音频文件", type=['wav', 'mp3', 'ogg', 'm4a'], label_visibility="collapsed")
        
        if audio_file is not None:
            st.audio(audio_file, format='audio/wav')
            
            if st.button("发送音频 🎤", key="send_audio"):
                with st.spinner("正在识别语音..."):
                    # 这里应该调用 Whisper API 进行语音识别
                    # 暂时使用占位文本
                    user_message = "[语音消息]"
                    st.session_state.conversation.append(('user', user_message))
                    
                    # 调用 AI API
                    ai_response = call_ai_api(user_message, contact['name'])
                    st.session_state.conversation.append(('agent', ai_response))
                    st.rerun()
        
        # 模拟 AI 响应
        st.session_state.ai_speaking = True
        ai_response = simulate_ai_response(user_message)
        st.session_state.conversation.append(('agent', ai_response))
        st.session_state.ai_speaking = False
        
        st.rerun()
    
    # 快捷回复按钮
    st.markdown("### 💬 快捷回复")
    quick_replies = ["你好吗？", "最近怎么样？", "想你了", "保重身体"]
    
    cols = st.columns(2)
    for idx, reply in enumerate(quick_replies):
        with cols[idx % 2]:
            if st.button(reply, key=f"quick_{idx}", use_container_width=True):
                st.session_state.conversation.append(('user', reply))
                st.session_state.ai_speaking = True
                ai_response = simulate_ai_response(reply)
                st.session_state.conversation.append(('agent', ai_response))
                st.session_state.ai_speaking = False
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 控制按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mute_icon = "🔇" if st.session_state.is_muted else "🔊"
        mute_label = "取消静音" if st.session_state.is_muted else "静音"
        if st.button(f"{mute_icon} {mute_label}", use_container_width=True):
            st.session_state.is_muted = not st.session_state.is_muted
            st.rerun()
    
    with col2:
        if st.button("📞 挂断", use_container_width=True, type="primary"):
            # 保存通话记录
            st.session_state.call_history.insert(0, {
                'contact': st.session_state.current_contact,
                'time': datetime.now(),
                'duration': get_call_duration(),
                'messages': len(st.session_state.conversation)
            })
            
            st.session_state.call_state = 'idle'
            st.session_state.call_start_time = None
            st.session_state.conversation = []
            st.session_state.current_tab = 'history'
            st.rerun()
    
    with col3:
        speaker_icon = "📢" if st.session_state.is_speaker else "📱"
        speaker_label = "听筒" if st.session_state.is_speaker else "扬声器"
        if st.button(f"{speaker_icon} {speaker_label}", use_container_width=True):
            st.session_state.is_speaker = not st.session_state.is_speaker
            st.rerun()
    
    # 自动刷新计时器
    time.sleep(1)
    st.rerun()

def render_contacts_tab():
    """联系人列表"""
    st.markdown("## 👥 联系人")
    
    for contact in st.session_state.contacts:
        cols = st.columns([4, 1])
        
        with cols[0]:
            st.markdown(f"""
            <div class="contact-card">
                <div class="contact-card-avatar">{contact['avatar']}</div>
                <div class="contact-card-info">
                    <div class="contact-card-name">{contact['name']}</div>
                    <div class="contact-card-detail">{contact['relationship']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            if st.button("📞", key=f"call_{contact['name']}", help=f"呼叫{contact['name']}"):
                st.session_state.call_state = 'ringing'
                st.session_state.current_contact = contact
                st.rerun()

def render_history_tab():
    """通话记录"""
    st.markdown("## 🕐 通话记录")
    
    if not st.session_state.call_history:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px; color: #666;">
            <div style="font-size: 60px; margin-bottom: 20px;">📱</div>
            <div style="font-size: 20px;">暂无通话记录</div>
            <div style="font-size: 14px; margin-top: 10px; color: #999;">
                开始你的第一次通话吧
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, call in enumerate(st.session_state.call_history):
            contact = call['contact']
            call_time = call['time'].strftime("%m月%d日 %H:%M")
            duration = format_time(call['duration'])
            messages = call.get('messages', 0)
            
            cols = st.columns([4, 1])
            
            with cols[0]:
                st.markdown(f"""
                <div class="contact-card">
                    <div class="contact-card-avatar">{contact['avatar']}</div>
                    <div class="contact-card-info">
                        <div class="contact-card-name">📞 {contact['name']}</div>
                        <div class="contact-card-detail">
                            {call_time} · {duration} · {messages} 条消息
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                if st.button("🔄", key=f"recall_{idx}", help="回拨"):
                    st.session_state.call_state = 'connecting'
                    st.session_state.current_contact = contact
                    st.rerun()

# ========== 主界面 ==========

st.markdown('<div class="phone-container">', unsafe_allow_html=True)
st.markdown('<div class="phone-notch"><div class="speaker"></div></div>', unsafe_allow_html=True)
st.markdown('<div class="phone-screen">', unsafe_allow_html=True)

# 状态栏
render_status_bar()

# 根据通话状态渲染界面
if st.session_state.call_state in ['ringing', 'connecting']:
    render_ringing_screen()
elif st.session_state.call_state == 'talking':
    render_talking_screen()
else:
    # 主界面 - 标签页
    if st.session_state.current_tab == 'contacts':
        render_contacts_tab()
    elif st.session_state.current_tab == 'history':
        render_history_tab()
    
    # 底部导航
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👥 联系人", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == 'contacts' else "secondary"):
            st.session_state.current_tab = 'contacts'
            st.rerun()
    
    with col2:
        if st.button("🕐 记录", use_container_width=True,
                    type="primary" if st.session_state.current_tab == 'history' else "secondary"):
            st.session_state.current_tab = 'history'
            st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)
