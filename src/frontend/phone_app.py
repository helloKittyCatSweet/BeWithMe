"""
Be With Me - Phone Call UI (Refactored)
重构后的手机通话界面

这是一个组件化的版本，代码结构更清晰，CSS 分离到外部文件。
"""
import streamlit as st
import sys
from pathlib import Path

# 添加 frontend 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from components.phone_components import (
    PhoneShell,
    StatusBar,
    ContactList,
    IncomingCall,
    ActiveCall,
    CallHistory,
    TabBar
)
from utils.helpers import (
    load_css,
    init_session_state,
    get_sample_contacts,
    start_call,
    end_call,
    add_message,
    simulate_agent_response,
    get_call_duration
)


def main():
    """主应用"""
    # 页面配置
    st.set_page_config(
        page_title="Be With Me - 智能通话",
        page_icon="📱",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    # 加载 CSS
    load_css()
    
    # 初始化状态
    init_session_state()
    
    # ========== 侧边栏控制 ==========
    with st.sidebar:
        st.title("📱 界面预览")
        st.markdown("---")
        
        # 界面模式选择
        view_mode = st.radio(
            "选择界面",
            ["联系人列表", "来电界面", "通话中", "通话记录"],
            key="view_mode"
        )
        
        st.markdown("---")
        
        # 如果是通话界面，可以选择联系人
        if view_mode in ["来电界面", "通话中"]:
            st.subheader("选择联系人")
            contacts = get_sample_contacts()
            contact_names = [c['name'] for c in contacts]
            selected_name = st.selectbox("联系人", contact_names)
            selected_contact = contacts[contact_names.index(selected_name)]
        else:
            selected_contact = None
        
        st.markdown("---")
        st.markdown("""
        **架构说明**
        - ✅ 组件化架构
        - ✅ 外部 CSS
        - ✅ z-index 层叠
        - ✅ 工具函数分离
        """)
    
    # ========== 主界面渲染 ==========
    # 获取联系人列表
    contacts = get_sample_contacts()
    
    # 渲染手机外壳（开始）
    PhoneShell.render()
    
    # 渲染状态栏
    StatusBar.render()
    
    # 根据侧边栏选择渲染不同界面
    if view_mode == "联系人列表":
        render_contacts_view(contacts)
    elif view_mode == "来电界面":
        render_incoming_view(selected_contact)
    elif view_mode == "通话中":
        render_calling_view(selected_contact)
    elif view_mode == "通话记录":
        render_records_view()
    
    # 关闭内容区域
    PhoneShell.close_content()
    
    # 渲染底部标签栏（仅在联系人和记录界面）
    if view_mode in ["联系人列表", "通话记录"]:
        # 确定当前标签
        current_tab = 'contacts' if view_mode == "联系人列表" else 'records'
        TabBar.render(current_tab)
    
    # 关闭手机外壳
    PhoneShell.close()
    
    # 标题和说明
    st.markdown("---")
    st.markdown("""
    ### 📱 Be With Me - 智能陪伴通话
    
    这是一个重构后的手机界面，采用了：
    - ✅ 组件化架构（components/）
    - ✅ 外部 CSS 文件（styles/）
    - ✅ 工具函数分离（utils/）
    - ✅ 正确的 z-index 层叠关系
    
    **使用侧边栏切换不同界面进行预览**
    """)


def render_contacts_view(contacts):
    """渲染联系人列表视图"""
    selected_contact = ContactList.render(contacts)
    
    if selected_contact:
        st.success(f"已选择：{selected_contact['name']}")


def render_incoming_view(contact):
    """渲染来电界面视图"""
    if not contact:
        st.warning("请在侧边栏选择联系人")
        return
    
    # 渲染来电界面（纯展示，不处理交互）
    st.markdown(f"""
    <div class="call-screen">
        <div class="incoming-call">
            <div class="caller-info">
                <div class="caller-avatar">{contact['avatar']}</div>
                <div class="caller-name">{contact['name']}</div>
                <div class="call-status">来电中...</div>
            </div>
            <div style="display: flex; justify-content: space-around; margin-top: 40px;">
                <div style="width: 70px; height: 70px; background: #ff3b30; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px;">❌</div>
                <div style="width: 70px; height: 70px; background: #34c759; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px;">✅</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_calling_view(contact):
    """渲染通话中界面视图"""
    if not contact:
        st.warning("请在侧边栏选择联系人")
        return
    
    # 模拟对话
    conversation = [
        ("user", "妈妈，你在干嘛呢？"),
        ("agent", "刚在家里收拾东西，想着给你打个电话。"),
        ("user", "今天吃饭了吗？"),
        ("agent", "吃过了，你呢？有没有好好吃饭？")
    ]
    
    # 渲染通话界面
    st.markdown(f"""
    <div class="call-screen">
        <div class="in-call">
            <div class="call-header">
                <div class="call-avatar">{contact['avatar']}</div>
                <div class="call-name">{contact['name']}</div>
                <div class="call-duration">02:35</div>
            </div>
            
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
            
            <div class="conversation-area">
    """, unsafe_allow_html=True)
    
    for role, message in conversation:
        bubble_class = "bubble-user" if role == "user" else "bubble-agent"
        st.markdown(
            f'<div class="bubble {bubble_class}">{message}</div>', 
            unsafe_allow_html=True
        )
    
    st.markdown("""
            </div>
            
            <div class="call-controls">
                <div style="text-align: center;">
                    <button style="width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.2); border: none; font-size: 24px; margin: 0 10px;">🔇</button>
                    <button style="width: 60px; height: 60px; border-radius: 50%; background: #ff3b30; border: none; font-size: 24px; margin: 0 10px;">📞</button>
                    <button style="width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.2); border: none; font-size: 24px; margin: 0 10px;">🔊</button>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_records_view():
    """渲染通话记录视图"""
    # 模拟记录
    from datetime import datetime, timedelta
    
    records = []
    contacts = get_sample_contacts()
    
    for i, contact in enumerate(contacts[:3]):
        record = {
            'contact': contact,
            'time': (datetime.now() - timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M"),
            'duration': f"{i+1}分{20+i*5}秒",
            'messages_count': (i+1) * 3,
            'timestamp': datetime.now().timestamp()
        }
        records.append(record)
    
    selected = CallHistory.render(records)
    
    if selected:
        st.success(f"已选择回拨：{selected['name']}")




if __name__ == "__main__":
    main()
