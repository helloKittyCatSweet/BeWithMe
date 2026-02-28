"""
Be With Me - 手机通话模拟界面
Phone Call Simulation UI
模拟真实手机与亲人通话的体验
"""
import streamlit as st
import requests
import base64
import time
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# 页面配置
st.set_page_config(
    page_title="📱 Be With Me - 通话",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# 高级 CSS 样式 - 模拟 iPhone 界面
st.markdown("""
<style>
/* 全局样式 */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 手机外壳 */
.phone-container {
    max-width: 400px;
    margin: 20px auto;
    background: #000;
    border-radius: 45px;
    padding: 15px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    position: relative;
}

/* 刘海屏 */
.phone-notch {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 30px;
    background: #000;
    border-radius: 0 0 20px 20px;
    z-index: 10;
}

/* 手机屏幕 */
.phone-screen {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 35px;
    padding: 45px 20px 30px 20px;
    min-height: 700px;
    position: relative;
    overflow: hidden;
}

/* 状态栏 */
.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    font-size: 14px;
    margin-bottom: 20px;
    padding: 0 10px;
}

/* 来电界面 */
.call-screen {
    text-align: center;
    padding: 40px 20px;
    color: #fff;
}

.contact-avatar {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    margin: 30px auto;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 60px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.contact-name {
    font-size: 32px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    color: #fff;
}

.call-status {
    font-size: 18px;
    color: #aaa;
    margin-bottom: 40px;
}

/* 通话中界面 */
.in-call-screen {
    text-align: center;
    padding: 60px 20px;
}

.call-timer {
    font-size: 48px;
    font-weight: 300;
    color: #fff;
    margin: 30px 0;
    font-family: 'Monaco', monospace;
}

/* 音频波形动画 */
.audio-wave {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80px;
    gap: 8px;
    margin: 40px 0;
}

.wave-bar {
    width: 6px;
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 3px;
    animation: wave 1s ease-in-out infinite;
}

.wave-bar:nth-child(1) { height: 20px; animation-delay: 0s; }
.wave-bar:nth-child(2) { height: 40px; animation-delay: 0.1s; }
.wave-bar:nth-child(3) { height: 60px; animation-delay: 0.2s; }
.wave-bar:nth-child(4) { height: 50px; animation-delay: 0.3s; }
.wave-bar:nth-child(5) { height: 30px; animation-delay: 0.4s; }
.wave-bar:nth-child(6) { height: 50px; animation-delay: 0.5s; }
.wave-bar:nth-child(7) { height: 60px; animation-delay: 0.6s; }
.wave-bar:nth-child(8) { height: 40px; animation-delay: 0.7s; }
.wave-bar:nth-child(9) { height: 20px; animation-delay: 0.8s; }

@keyframes wave {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(1.5); }
}

/* 通话控制按钮 */
.call-controls {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 60px 0 40px 0;
    flex-wrap: wrap;
}

.control-btn {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.control-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
}

.btn-answer {
    background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
}

.btn-decline {
    background: linear-gradient(135deg, #d63031 0%, #e17055 100%);
}

.btn-mute {
    background: linear-gradient(135deg, #636e72 0%, #2d3436 100%);
}

.btn-speaker {
    background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
}

/* 拨号界面 */
.dial-pad {
    padding: 20px;
}

.dial-display {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 30px;
    min-height: 60px;
    text-align: center;
}

.dial-number {
    font-size: 36px;
    color: #fff;
    font-family: 'Monaco', monospace;
    letter-spacing: 5px;
}

.keypad {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 30px 0;
}

.key {
    aspect-ratio: 1;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.key:hover {
    background: rgba(255,255,255,0.2);
    transform: scale(1.05);
}

.key-number {
    font-size: 32px;
    font-weight: 500;
    color: #fff;
}

.key-letters {
    font-size: 10px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* 通话记录 */
.call-history {
    padding: 20px;
}

.history-item {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.history-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.history-info {
    flex: 1;
}

.history-name {
    color: #fff;
    font-size: 18px;
    font-weight: 500;
}

.history-time {
    color: #aaa;
    font-size: 14px;
}

.history-duration {
    color: #667eea;
    font-size: 14px;
}

/* 联系人列表 */
.contact-list {
    padding: 20px;
}

.contact-item {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 15px;
    cursor: pointer;
    transition: all 0.2s;
}

.contact-item:hover {
    background: rgba(255,255,255,0.1);
    transform: translateX(5px);
}

/* 底部导航 */
.bottom-nav {
    position: absolute;
    bottom: 10px;
    left: 20px;
    right: 20px;
    display: flex;
    justify-content: space-around;
    background: rgba(0,0,0,0.5);
    border-radius: 25px;
    padding: 15px 10px;
    backdrop-filter: blur(10px);
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    cursor: pointer;
    transition: all 0.2s;
    padding: 5px 15px;
    border-radius: 15px;
}

.nav-item:hover {
    background: rgba(255,255,255,0.1);
}

.nav-item.active {
    background: rgba(102, 126, 234, 0.3);
}

.nav-icon {
    font-size: 24px;
}

.nav-label {
    font-size: 10px;
    color: #aaa;
}

.nav-item.active .nav-label {
    color: #667eea;
}

/* 消息提示 */
.toast {
    background: rgba(0,0,0,0.9);
    color: #fff;
    padding: 15px 25px;
    border-radius: 25px;
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    animation: slideUp 0.3s;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if 'call_state' not in st.session_state:
    st.session_state.call_state = 'idle'  # idle, incoming, dialing, in_call, ended
if 'call_start_time' not in st.session_state:
    st.session_state.call_start_time = None
if 'dialed_number' not in st.session_state:
    st.session_state.dialed_number = ''
if 'current_contact' not in st.session_state:
    st.session_state.current_contact = {
        'name': '亲爱的妈妈',
        'avatar': '👩',
        'phone': '',
        'relationship': 'parent'
    }
if 'call_history' not in st.session_state:
    st.session_state.call_history = []
if 'contacts' not in st.session_state:
    st.session_state.contacts = [
        {'name': '妈妈', 'avatar': '👩', 'relationship': 'parent', 'phone': ''},
        {'name': '爸爸', 'avatar': '👨', 'relationship': 'parent', 'phone': ''},
        {'name': '奶奶', 'avatar': '👵', 'relationship': 'grandparent', 'phone': ''},
        {'name': '爷爷', 'avatar': '👴', 'relationship': 'grandparent', 'phone': ''},
    ]
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'contacts'  # contacts, dial, history
if 'is_muted' not in st.session_state:
    st.session_state.is_muted = False
if 'is_speaker' not in st.session_state:
    st.session_state.is_speaker = False

def format_time(seconds):
    """格式化通话时间"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def render_phone_container():
    """渲染手机外壳"""
    return """
    <div class="phone-container">
        <div class="phone-notch"></div>
        <div class="phone-screen">
    """

def render_status_bar():
    """渲染状态栏"""
    current_time = datetime.now().strftime("%H:%M")
    return f"""
    <div class="status-bar">
        <span>{current_time}</span>
        <span>📶 🔋</span>
    </div>
    """

def render_incoming_call():
    """渲染来电界面"""
    contact = st.session_state.current_contact
    
    html = f"""
    <div class="call-screen">
        <div class="contact-avatar">{contact['avatar']}</div>
        <div class="contact-name">{contact['name']}</div>
        <div class="call-status">来电...</div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # 接听和挂断按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("❌", key="decline", help="拒绝"):
            st.session_state.call_state = 'idle'
            st.session_state.current_tab = 'contacts'
            st.rerun()
    
    with col3:
        if st.button("✅", key="answer", help="接听"):
            st.session_state.call_state = 'in_call'
            st.session_state.call_start_time = time.time()
            st.rerun()

def render_in_call():
    """渲染通话中界面"""
    contact = st.session_state.current_contact
    
    # 计算通话时长
    if st.session_state.call_start_time:
        elapsed = int(time.time() - st.session_state.call_start_time)
        timer_text = format_time(elapsed)
    else:
        timer_text = "00:00"
    
    html = f"""
    <div class="in-call-screen">
        <div class="contact-avatar" style="width: 100px; height: 100px; font-size: 48px;">
            {contact['avatar']}
        </div>
        <div class="contact-name" style="font-size: 28px;">{contact['name']}</div>
        <div class="call-timer">{timer_text}</div>
        
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
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # 通话控制按钮
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        mute_icon = "🔇" if st.session_state.is_muted else "🔊"
        if st.button(mute_icon, key="mute", help="静音"):
            st.session_state.is_muted = not st.session_state.is_muted
            st.rerun()
    
    with col2:
        if st.button("⏸️", key="hold", help="保持"):
            st.toast("通话已保持")
    
    with col3:
        speaker_icon = "📢" if st.session_state.is_speaker else "📱"
        if st.button(speaker_icon, key="speaker", help="扬声器"):
            st.session_state.is_speaker = not st.session_state.is_speaker
            st.rerun()
    
    with col4:
        if st.button("➕", key="add_call", help="添加通话"):
            st.toast("多方通话功能开发中")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 挂断按钮（居中）
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📞 挂断", type="primary", use_container_width=True):
            # 记录通话历史
            if st.session_state.call_start_time:
                duration = int(time.time() - st.session_state.call_start_time)
                st.session_state.call_history.insert(0, {
                    'contact': st.session_state.current_contact.copy(),
                    'time': datetime.now(),
                    'duration': duration,
                    'type': 'outgoing'
                })
            
            st.session_state.call_state = 'idle'
            st.session_state.call_start_time = None
            st.session_state.current_tab = 'history'
            st.rerun()
    
    # 自动刷新以更新计时器
    time.sleep(1)
    st.rerun()

def render_dial_pad():
    """渲染拨号界面"""
    st.markdown(f"""
    <div class="dial-pad">
        <div class="dial-display">
            <div class="dial-number">{st.session_state.dialed_number or '输入号码'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 数字键盘
    keypad_layout = [
        [('1', ''), ('2', 'ABC'), ('3', 'DEF')],
        [('4', 'GHI'), ('5', 'JKL'), ('6', 'MNO')],
        [('7', 'PQRS'), ('8', 'TUV'), ('9', 'WXYZ')],
        [('*', ''), ('0', '+'), ('#', '')]
    ]
    
    for row in keypad_layout:
        cols = st.columns(3)
        for col, (num, letters) in zip(cols, row):
            with col:
                if st.button(f"{num}\n{letters}", key=f"key_{num}", use_container_width=True):
                    st.session_state.dialed_number += num
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 控制按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ 删除", use_container_width=True):
            if st.session_state.dialed_number:
                st.session_state.dialed_number = st.session_state.dialed_number[:-1]
                st.rerun()
    
    with col2:
        if st.button("📞 呼叫", type="primary", use_container_width=True, 
                     disabled=not st.session_state.dialed_number):
            # 模拟拨打电话
            st.session_state.call_state = 'incoming'
            st.session_state.current_contact = {
                'name': f'联系人 ({st.session_state.dialed_number})',
                'avatar': '👤',
                'phone': st.session_state.dialed_number,
                'relationship': 'other'
            }
            st.session_state.dialed_number = ''
            st.rerun()
    
    with col3:
        if st.button("❌ 清空", use_container_width=True):
            st.session_state.dialed_number = ''
            st.rerun()

def render_contacts():
    """渲染联系人列表"""
    st.markdown('<div class="contact-list">', unsafe_allow_html=True)
    
    for contact in st.session_state.contacts:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="contact-item">
                <div class="history-avatar">{contact['avatar']}</div>
                <div class="history-info">
                    <div class="history-name">{contact['name']}</div>
                    <div class="history-time">{contact['relationship']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📞", key=f"call_{contact['name']}", help=f"呼叫{contact['name']}"):
                st.session_state.call_state = 'incoming'
                st.session_state.current_contact = contact
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_call_history():
    """渲染通话记录"""
    st.markdown('<div class="call-history">', unsafe_allow_html=True)
    
    if not st.session_state.call_history:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: #aaa;">
            <div style="font-size: 48px; margin-bottom: 20px;">📱</div>
            <div style="font-size: 18px;">暂无通话记录</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, call in enumerate(st.session_state.call_history):
            contact = call['contact']
            call_time = call['time'].strftime("%m月%d日 %H:%M")
            duration = format_time(call['duration'])
            
            type_icon = "📞" if call['type'] == 'outgoing' else "📲"
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-avatar">{contact['avatar']}</div>
                    <div class="history-info">
                        <div class="history-name">{type_icon} {contact['name']}</div>
                        <div class="history-time">{call_time}</div>
                        <div class="history-duration">通话时长: {duration}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🔄", key=f"recall_{idx}", help="回拨"):
                    st.session_state.call_state = 'incoming'
                    st.session_state.current_contact = contact
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_bottom_nav():
    """渲染底部导航"""
    tabs = [
        ('contacts', '👥', '联系人'),
        ('dial', '🔢', '拨号'),
        ('history', '🕐', '记录')
    ]
    
    cols = st.columns(len(tabs))
    
    for col, (tab_id, icon, label) in zip(cols, tabs):
        with col:
            if st.button(f"{icon}\n{label}", key=f"tab_{tab_id}", 
                        use_container_width=True,
                        type="primary" if st.session_state.current_tab == tab_id else "secondary"):
                st.session_state.current_tab = tab_id
                st.rerun()

# 主界面渲染
st.markdown(render_phone_container(), unsafe_allow_html=True)
st.markdown(render_status_bar(), unsafe_allow_html=True)

# 根据通话状态渲染不同界面
if st.session_state.call_state == 'incoming':
    render_incoming_call()
elif st.session_state.call_state == 'in_call':
    render_in_call()
else:
    # 空闲状态 - 显示主界面
    if st.session_state.current_tab == 'contacts':
        render_contacts()
    elif st.session_state.current_tab == 'dial':
        render_dial_pad()
    elif st.session_state.current_tab == 'history':
        render_call_history()
    
    # 底部导航
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    render_bottom_nav()

# 关闭手机屏幕和外壳的 div
st.markdown("</div></div>", unsafe_allow_html=True)

# 添加实时刷新（在通话中时）
if st.session_state.call_state == 'in_call':
    st.markdown("""
    <script>
    setTimeout(function() {
        window.location.reload();
    }, 1000);
    </script>
    """, unsafe_allow_html=True)
