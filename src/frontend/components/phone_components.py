"""
Be With Me - UI Components
组件模块
"""
import streamlit as st
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class PhoneShell:
    """手机外壳组件"""
    
    @staticmethod
    def render():
        """渲染手机外壳和屏幕开始"""
        st.markdown("""
        <div class="phone-wrapper">
            <div class="phone-container">
                <div class="phone-notch">
                    <div class="notch-camera"></div>
                    <div class="notch-speaker"></div>
                </div>
            </div>
            <div class="phone-screen">
                <div id="screen-content" class="screen-content">
        """, unsafe_allow_html=True)
    
    @staticmethod
    def close_content():
        """关闭内容区域"""
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def close():
        """关闭手机外壳"""
        st.markdown("""
                <div class="home-indicator"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


class StatusBar:
    """状态栏组件"""
    
    @staticmethod
    def render():
        """渲染状态栏"""
        current_time = datetime.now().strftime("%H:%M")
        st.markdown(f"""
        <div class="status-bar">
            <div class="status-time">{current_time}</div>
            <div class="status-icons">
                📶 📡 🔋
            </div>
        </div>
        """, unsafe_allow_html=True)


class ContactCard:
    """联系人卡片组件"""
    
    @staticmethod
    def render(contact: Dict, index: int) -> bool:
        """
        渲染联系人卡片
        
        Args:
            contact: 联系人信息字典
            index: 卡片索引
            
        Returns:
            bool: 是否被点击
        """
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div class="contact-avatar">
                {contact['avatar']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="contact-info">
                <div class="contact-name">{contact['name']}</div>
                <div class="contact-relation">{contact.get('relationship', '家人')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 使用按钮检测点击
        if st.button(f"📞 拨打", key=f"call_{index}", use_container_width=True):
            return True
        
        return False


class ContactList:
    """联系人列表组件"""
    
    @staticmethod
    def render(contacts: List[Dict]) -> Optional[Dict]:
        """
        渲染联系人列表
        
        Args:
            contacts: 联系人列表
            
        Returns:
            Optional[Dict]: 被选中的联系人，如果没有则返回 None
        """
        st.markdown('<div class="contacts-container">', unsafe_allow_html=True)
        st.markdown('<div class="contacts-header">联系人</div>', unsafe_allow_html=True)
        
        selected_contact = None
        
        for idx, contact in enumerate(contacts):
            with st.container():
                st.markdown('<div class="contact-card">', unsafe_allow_html=True)
                
                if ContactCard.render(contact, idx):
                    selected_contact = contact
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return selected_contact


class IncomingCall:
    """来电界面组件"""
    
    @staticmethod
    def render(contact: Dict) -> Tuple[bool, bool]:
        """
        渲染来电界面
        
        Args:
            contact: 来电联系人信息
            
        Returns:
            Tuple[bool, bool]: (是否接听, 是否拒绝)
        """
        st.markdown("""
        <div class="call-screen">
            <div class="incoming-call">
                <div class="caller-info">
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
                    <div class="caller-avatar">{contact['avatar']}</div>
                    <div class="caller-name">{contact['name']}</div>
                    <div class="call-status">来电中...</div>
                </div>
        """, unsafe_allow_html=True)
        
        # 接听和拒绝按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        
        decline = False
        accept = False
        
        with col1:
            if st.button("❌", key="btn_decline", help="拒绝", 
                        use_container_width=True):
                decline = True
        
        with col3:
            if st.button("✅", key="btn_accept", help="接听", 
                        use_container_width=True):
                accept = True
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return accept, decline


class ActiveCall:
    """通话中界面组件"""
    
    @staticmethod
    def render_audio_waves():
        """渲染音频波形动画"""
        st.markdown("""
        <div class="audio-waves">
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
    
    @staticmethod
    def render_conversation(messages: List[Tuple[str, str]]):
        """
        渲染对话气泡
        
        Args:
            messages: 消息列表 [(角色, 消息内容)]
        """
        st.markdown('<div class="conversation-area">', unsafe_allow_html=True)
        
        for role, message in messages:
            bubble_class = "bubble-user" if role == "user" else "bubble-agent"
            st.markdown(
                f'<div class="bubble {bubble_class}">{message}</div>', 
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render(contact: Dict, duration: int, conversation: List[Tuple[str, str]]) -> Tuple[bool, str]:
        """
        渲染通话中界面
        
        Args:
            contact: 联系人信息
            duration: 通话时长（秒）
            conversation: 对话列表
            
        Returns:
            Tuple[bool, str]: (是否挂断, 用户输入的消息)
        """
        st.markdown('<div class="call-screen"><div class="in-call">', unsafe_allow_html=True)
        
        # 通话头部
        st.markdown(f"""
        <div class="call-header">
            <div class="call-avatar">{contact['avatar']}</div>
            <div class="call-name">{contact['name']}</div>
            <div class="call-duration">{duration // 60:02d}:{duration % 60:02d}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 音频波形
        ActiveCall.render_audio_waves()
        
        # 对话区域
        if conversation:
            ActiveCall.render_conversation(conversation)
        
        # 输入区域
        st.markdown('<div class="controls-panel">', unsafe_allow_html=True)
        
        input_method = st.radio(
            "输入方式", 
            ["💬 文本", "🎤 音频"], 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        user_message = ""
        
        if input_method == "💬 文本":
            user_message = st.text_input(
                "消息", 
                key="msg_input",
                placeholder="说点什么...",
                label_visibility="collapsed"
            )
            
            if st.button("发送", key="send_msg", use_container_width=True):
                pass  # 消息已经在 user_message 中
        else:
            audio_file = st.file_uploader(
                "上传音频", 
                type=['wav', 'mp3', 'ogg', 'm4a'],
                label_visibility="collapsed"
            )
            
            if audio_file:
                st.audio(audio_file)
                if st.button("发送音频", key="send_audio", use_container_width=True):
                    user_message = "[语音消息]"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 控制按钮
        st.markdown('<div class="call-controls">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        hangup = False
        
        with col1:
            if st.button("🔇", key="mute", help="静音"):
                pass
        
        with col2:
            if st.button("📞 挂断", key="hangup", help="挂断"):
                hangup = True
        
        with col3:
            if st.button("🔊", key="speaker", help="扬声器"):
                pass
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        return hangup, user_message


class CallHistory:
    """通话记录组件"""
    
    @staticmethod
    def render(records: List[Dict]) -> Optional[Dict]:
        """
        渲染通话记录
        
        Args:
            records: 通话记录列表
            
        Returns:
            Optional[Dict]: 被选中回拨的联系人
        """
        st.markdown('<div class="records-container">', unsafe_allow_html=True)
        st.markdown('<div class="records-header">最近通话</div>', unsafe_allow_html=True)
        
        selected = None
        
        if not records:
            st.markdown(
                '<div class="text-center" style="color: rgba(255,255,255,0.5); padding: 40px;">暂无通话记录</div>',
                unsafe_allow_html=True
            )
        else:
            for idx, record in enumerate(records):
                st.markdown('<div class="record-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="record-header">
                        <div class="record-name">{record['contact']['avatar']} {record['contact']['name']}</div>
                        <div class="record-time">{record['time']}</div>
                    </div>
                    <div class="record-details">
                        时长: {record['duration']} | 消息: {record['messages_count']} 条
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("回拨", key=f"recall_{idx}"):
                        selected = record['contact']
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return selected


class TabBar:
    """底部标签栏组件"""
    
    @staticmethod
    def render(active_tab: str) -> str:
        """
        渲染标签栏（纯展示版）
        
        Args:
            active_tab: 当前激活的标签
            
        Returns:
            str: 当前标签
        """
        contact_class = "active" if active_tab == 'contacts' else ""
        record_class = "active" if active_tab == 'records' else ""
        
        st.markdown(f"""
        <div class="tab-bar">
            <div class="tab-item {contact_class}">
                👥
            </div>
            <div class="tab-item {record_class}">
                📋
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return active_tab
