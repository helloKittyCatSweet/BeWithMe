"""
Be With Me - Utility Functions
工具函数模块
"""
import json
from pathlib import Path
from typing import Dict, List
import streamlit as st


def load_css() -> None:
    """加载外部 CSS 文件"""
    css_path = Path(__file__).parent.parent / "styles" / "phone_ui.css"
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        st.markdown(
            f'<style>{css_content}</style>', 
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error(f"CSS 文件未找到: {css_path}")
    except Exception as e:
        st.error(f"加载 CSS 时出错: {e}")


def init_session_state() -> None:
    """初始化 session state"""
    default_states = {
        'call_active': False,
        'call_incoming': False,
        'current_contact': None,
        'call_start_time': None,
        'conversation': [],
        'call_records': [],
        'active_tab': 'contacts'
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_sample_contacts() -> List[Dict]:
    """获取示例联系人列表"""
    return [
        {
            'id': 'mom',
            'name': '妈妈',
            'avatar': '👩',
            'relationship': '母亲',
            'phone': '+86 138 0000 0001'
        },
        {
            'id': 'dad',
            'name': '爸爸',
            'avatar': '👨',
            'relationship': '父亲',
            'phone': '+86 138 0000 0002'
        },
        {
            'id': 'grandma',
            'name': '奶奶',
            'avatar': '👵',
            'relationship': '祖母',
            'phone': '+86 138 0000 0003'
        },
        {
            'id': 'grandpa',
            'name': '爷爷',
            'avatar': '👴',
            'relationship': '祖父',
            'phone': '+86 138 0000 0004'
        },
        {
            'id': 'brother',
            'name': '哥哥',
            'avatar': '👦',
            'relationship': '兄弟',
            'phone': '+86 138 0000 0005'
        }
    ]


def format_duration(seconds: int) -> str:
    """
    格式化时长
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时长字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分"


def save_call_record(contact: Dict, duration: int, messages_count: int) -> None:
    """
    保存通话记录
    
    Args:
        contact: 联系人信息
        duration: 通话时长（秒）
        messages_count: 消息数量
    """
    from datetime import datetime
    
    record = {
        'contact': contact,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'duration': format_duration(duration),
        'messages_count': messages_count,
        'timestamp': datetime.now().timestamp()
    }
    
    # 添加到记录列表（最新的在前）
    if 'call_records' not in st.session_state:
        st.session_state.call_records = []
    
    st.session_state.call_records.insert(0, record)
    
    # 保留最近 20 条记录
    st.session_state.call_records = st.session_state.call_records[:20]


def start_call(contact: Dict) -> None:
    """
    开始通话
    
    Args:
        contact: 联系人信息
    """
    from datetime import datetime
    
    st.session_state.call_active = True
    st.session_state.call_incoming = False
    st.session_state.current_contact = contact
    st.session_state.call_start_time = datetime.now()
    st.session_state.conversation = []


def end_call() -> None:
    """结束通话"""
    from datetime import datetime
    
    if st.session_state.call_active and st.session_state.call_start_time:
        # 计算通话时长
        duration = int((datetime.now() - st.session_state.call_start_time).total_seconds())
        
        # 保存记录
        save_call_record(
            st.session_state.current_contact,
            duration,
            len(st.session_state.conversation)
        )
    
    # 重置状态
    st.session_state.call_active = False
    st.session_state.call_incoming = False
    st.session_state.current_contact = None
    st.session_state.call_start_time = None
    st.session_state.conversation = []


def add_message(role: str, message: str) -> None:
    """
    添加消息到对话
    
    Args:
        role: 角色 ('user' 或 'agent')
        message: 消息内容
    """
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    st.session_state.conversation.append((role, message))


def simulate_agent_response(user_message: str) -> str:
    """
    模拟智能体回复（简化版）
    
    Args:
        user_message: 用户消息
        
    Returns:
        str: 智能体回复
    """
    # 简单的模拟响应
    responses = {
        '你好': '你好！很高兴听到你的声音。',
        '最近怎么样': '我很好，谢谢关心！你呢？',
        '在干嘛': '刚在家里休息，想着给你打个电话。',
        '吃饭了吗': '吃过了，你吃了吗？',
        '再见': '好的，再见！有空常联系。'
    }
    
    # 检查是否有匹配的响应
    for key in responses:
        if key in user_message:
            return responses[key]
    
    # 默认响应
    return '嗯嗯，我明白了。'


def get_call_duration() -> int:
    """
    获取当前通话时长
    
    Returns:
        int: 通话时长（秒）
    """
    from datetime import datetime
    
    if not st.session_state.call_start_time:
        return 0
    
    return int((datetime.now() - st.session_state.call_start_time).total_seconds())


def export_records_json() -> str:
    """
    导出通话记录为 JSON
    
    Returns:
        str: JSON 字符串
    """
    records = st.session_state.get('call_records', [])
    return json.dumps(records, ensure_ascii=False, indent=2)


def import_records_json(json_str: str) -> bool:
    """
    从 JSON 导入通话记录
    
    Args:
        json_str: JSON 字符串
        
    Returns:
        bool: 是否成功
    """
    try:
        records = json.loads(json_str)
        st.session_state.call_records = records
        return True
    except Exception:
        return False
