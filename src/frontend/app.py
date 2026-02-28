"""
Echoes of Kin - Streamlit Frontend Demo Application
AI-Powered Voice Cloning & Conversation System
"""
import streamlit as st
import requests
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Be With Me",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL from environment variable
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS Styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2.5rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.main-header h1 {
    margin-bottom: 0.5rem;
    font-size: 2.5rem;
}
.main-header h3 {
    margin-bottom: 0.3rem;
    font-weight: 400;
}
.chat-message {
    padding: 1rem 1.2rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.user-message {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-left: 4px solid #2196f3;
}
.agent-message {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border-left: 4px solid #9c27b0;
}
.info-box {
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 8px;
    border-left: 4px solid #76ff03;
}
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🎙️ Be With Me</h1>
    <h3>AI-Powered Voice Cloning & Conversation System</h3>
    <p>Experience meaningful conversations with AI that sounds like your loved ones</p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if 'agent_created' not in st.session_state:
    st.session_state.agent_created = False
if 'voice_cloned' not in st.session_state:
    st.session_state.voice_cloned = False
if 'voice_id' not in st.session_state:
    st.session_state.voice_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar - System Status
st.sidebar.title("⚙️ System Status")

try:
    status_resp = requests.get(f"{API_BASE_URL}/status", timeout=2)
    if status_resp.status_code == 200:
        status = status_resp.json()
        st.sidebar.success("✅ Backend Connected")
        
        if status['agent_ready']:
            st.sidebar.info(f"🤖 Agent: {status['agent_name']}")
            st.session_state.agent_created = True
        
        if status['voice_ready']:
            st.sidebar.info(f"🔊 Voice ID: {status['voice_id'][:20]}...")
            st.session_state.voice_cloned = True
            st.session_state.voice_id = status['voice_id']
    else:
        st.sidebar.error("❌ Backend Error")
except Exception as e:
    st.sidebar.error(f"❌ Connection Failed: {str(e)}")

st.sidebar.markdown("---")

# Setup Progress Tracker
st.sidebar.title("📋 Setup Progress")
step1 = "✅" if st.session_state.voice_cloned else "⏳"
step2 = "✅" if st.session_state.agent_created else "⏳"
step3 = "✅" if (st.session_state.voice_cloned and st.session_state.agent_created) else "⏳"

st.sidebar.markdown(f"""
{step1} **Step 1:** Clone Voice
{step2} **Step 2:** Create Agent  
{step3} **Step 3:** Start Conversation
""")

# Tech Stack Info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Powered By")
st.sidebar.markdown("""
- 🧠 **Mistral Large 2**
- 🎤 **ElevenLabs Voice AI**
- 🎧 **OpenAI Whisper**
- 📊 **W&B Weave Tracking**
""")

# Main Interface - Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👪 Family Verification", "🎤 Clone Voice", "🤖 Create Agent", "💬 Chat", "📊 History"])

with tab1:
    st.header("👪 Step 0: Family Relationship Verification")
    st.info("🛡️ 伦理保护：请声明您与要克隆声音的亲属关系，并上传验证文件")
    
    st.markdown("### 为什么需要验证？")
    st.markdown("""
    <div class="info-box">
    为防止技术滥用，我们要求用户：
    1. **声明亲属关系** - 说明您与被克隆声音者的关系
    2. **上传证明文件** - 提供户口本、死亡证明等官方文件
    3. **等待审核** - 管理员会在 24 小时内审核您的申请
    4. **通过后使用** - 只有审核通过的关系才能进行声音克隆
    
    这是一个负责任的 AI 系统，旨在保护个人隐私和尊重家庭关系。
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 用户 ID 输入（实际应用中从登录会话获取）
    user_id = st.number_input("User ID (Demo)", min_value=1, value=1, help="实际应用中从登录会话获取")
    
    # 创建两列布局
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📝 注册亲属关系")
        
        with st.form("relationship_form"):
            relative_name = st.text_input("亲属姓名 *", placeholder="例如：张明")
            
            relationship_type = st.selectbox(
                "关系类型 *",
                ["parent", "grandparent", "sibling", "child", "spouse", "other"],
                format_func=lambda x: {
                    "parent": "父母",
                    "grandparent": "祖父母/外祖父母",
                    "sibling": "兄弟姐妹",
                    "child": "子女",
                    "spouse": "配偶",
                    "other": "其他"
                }[x]
            )
            
            purpose = st.text_area(
                "使用目的 *", 
                placeholder="例如：怀念逝去的父亲，希望能听到他的声音",
                help="请说明为什么需要克隆这个声音"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                birth_date = st.date_input("出生日期（可选）")
            with col_b:
                is_deceased = st.checkbox("已故")
                death_date = st.date_input("去世日期（可选）", disabled=not is_deceased)
            
            additional_info = st.text_area(
                "其他信息（可选）",
                placeholder="任何您想补充的信息"
            )
            
            submit_btn = st.form_submit_button("🚀 提交关系申请", type="primary", use_container_width=True)
            
            if submit_btn:
                if not relative_name or not purpose:
                    st.error("❌ 请填写必填字段：亲属姓名和使用目的")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/relationships/register",
                            json={
                                "relative_name": relative_name,
                                "relationship_type": relationship_type,
                                "purpose": purpose,
                                "birth_date": birth_date.isoformat() if birth_date else None,
                                "death_date": death_date.isoformat() if is_deceased and death_date else None,
                                "additional_info": additional_info
                            },
                            params={"user_id": user_id}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ 关系申请提交成功！关系 ID: {result['id']}")
                            st.info("📝 请在下方上传验证文件")
                            st.session_state.last_relationship_id = result['id']
                            st.rerun()
                        else:
                            st.error(f"❌ 提交失败: {response.text}")
                    except Exception as e:
                        st.error(f"❌ 错误: {str(e)}")
        
        st.markdown("---")
        
        # 文件上传部分
        st.markdown("### 📄 上传验证文件")
        
        # 获取用户的关系列表用于选择
        try:
            rel_response = requests.get(
                f"{API_BASE_URL}/relationships/list",
                params={"user_id": user_id}
            )
            if rel_response.status_code == 200:
                relationships = rel_response.json()
                if relationships:
                    # 筛选状态为 pending 的关系
                    pending_rels = [r for r in relationships if r['verification_status'] == 'pending']
                    
                    if pending_rels:
                        selected_rel = st.selectbox(
                            "选择关系",
                            pending_rels,
                            format_func=lambda r: f"{r['relative_name']} ({r['relationship_type']}) - ID: {r['id']}"
                        )
                        
                        uploaded_doc = st.file_uploader(
                            "上传验证文件（户口本、死亡证明等）",
                            type=["pdf", "jpg", "jpeg", "png"],
                            help="PDF、JPG 或 PNG 格式"
                        )
                        
                        if st.button("📤 上传文件", type="primary"):
                            if uploaded_doc:
                                try:
                                    upload_response = requests.post(
                                        f"{API_BASE_URL}/relationships/{selected_rel['id']}/upload-document",
                                        files={"document": uploaded_doc},
                                        params={"user_id": user_id}
                                    )
                                    
                                    if upload_response.status_code == 200:
                                        st.success("✅ 文件上传成功！等待管理员审核")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ 上传失败: {upload_response.text}")
                                except Exception as e:
                                    st.error(f"❌ 错误: {str(e)}")
                            else:
                                st.warning("⚠️ 请选择文件")
                    else:
                        st.info("💡 没有待上传文件的关系。请先注册关系。")
        except Exception as e:
            st.error(f"❌ 获取关系列表失败: {str(e)}")
    
    with col2:
        st.markdown("### 📋 我的关系列表")
        
        if st.button("🔄 刷新列表"):
            st.rerun()
        
        try:
            rel_response = requests.get(
                f"{API_BASE_URL}/relationships/list",
                params={"user_id": user_id}
            )
            
            if rel_response.status_code == 200:
                relationships = rel_response.json()
                
                if relationships:
                    for rel in relationships:
                        status_emoji = {
                            'pending': '⏳',
                            'approved': '✅',
                            'rejected': '❌',
                            'expired': '⌛'
                        }.get(rel['verification_status'], '❓')
                        
                        status_color = {
                            'pending': '#FFA500',
                            'approved': '#4CAF50',
                            'rejected': '#F44336',
                            'expired': '#9E9E9E'
                        }.get(rel['verification_status'], '#999')
                        
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                border-left: 4px solid {status_color};
                                padding: 10px;
                                margin: 10px 0;
                                background: #f9f9f9;
                                border-radius: 5px;
                            ">
                                <h4 style="margin: 0;">{status_emoji} {rel['relative_name']}</h4>
                                <p style="margin: 5px 0; font-size: 0.9em;">
                                    <strong>关系:</strong> {rel['relationship_type']}<br>
                                    <strong>状态:</strong> {rel['verification_status']}<br>
                                    <strong>申请时间:</strong> {rel['created_at'][:10]}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if rel['verification_status'] == 'approved':
                                st.success(f"可用于声音克隆 - Relationship ID: {rel['id']}")
                            elif rel['verification_status'] == 'rejected' and rel.get('reviewer_notes'):
                                st.error(f"拒绝原因: {rel['reviewer_notes']}")
                else:
                    st.info("📭 还没有注册任何关系")
        except Exception as e:
            st.error(f"❌ 获取列表失败: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 🔒 管理员审核")
        st.markdown("""
        <div class="info-box">
        <p><strong>审核流程:</strong></p>
        <ol style="margin: 0; padding-left: 20px;">
        <li>用户提交关系申请</li>
        <li>用户上传验证文件</li>
        <li>管理员审核文件真实性</li>
        <li>审核通过后可进行声音克隆</li>
        </ol>
        <p style="margin-top: 10px;"><em>通常在 24 小时内完成审核</em></p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.header("🎤 Step 1: Clone Voice")
    st.info("📤 Upload a 30-second audio sample to clone the voice using ElevenLabs Instant Voice Cloning")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        voice_name = st.text_input("Voice Name", placeholder="e.g., Grandmother's Voice")
        voice_desc = st.text_area("Voice Description (Optional)", placeholder="e.g., Warm, gentle, and caring tone")
        
        # 添加关系选择
        st.markdown("### 🔐 关系验证（可选）")
        use_verification = st.checkbox("使用已验证的关系", value=False, help="勾选后只能为已验证的亲属克隆声音")
        
        relationship_id_for_clone = None
        if use_verification:
            user_id_clone = st.number_input("User ID", min_value=1, value=1, key="clone_user_id")
            try:
                approved_rels_resp = requests.get(
                    f"{API_BASE_URL}/relationships/list",
                    params={"user_id": user_id_clone, "status": "approved"}
                )
                if approved_rels_resp.status_code == 200:
                    approved_rels = approved_rels_resp.json()
                    if approved_rels:
                        selected_approved_rel = st.selectbox(
                            "选择已验证的关系",
                            approved_rels,
                            format_func=lambda r: f"{r['relative_name']} ({r['relationship_type']})"
                        )
                        relationship_id_for_clone = selected_approved_rel['id']
                        st.success(f"✅ 已选择关系: {selected_approved_rel['relative_name']}")
                    else:
                        st.warning("⚠️ 没有已审核通过的关系，请先在 Family Verification 标签页注册关系")
                        use_verification = False
            except Exception as e:
                st.error(f"获取关系失败: {str(e)}")
                use_verification = False
        
        uploaded_audio = st.file_uploader("Upload Audio File (.mp3 or .wav)", type=["mp3", "wav"])
        
        clone_disabled = not uploaded_audio or (use_verification and not relationship_id_for_clone)
        
        if st.button("🚀 Clone Voice", type="primary", disabled=clone_disabled):
            if uploaded_audio and voice_name:
                with st.spinner("🔄 Cloning voice... This may take a moment..."):
                    try:
                        # 准备表单数据
                        form_data = {
                            "voice_name": voice_name,
                            "description": voice_desc,
                            "user_id": user_id_clone if use_verification else 1
                        }
                        
                        if use_verification and relationship_id_for_clone:
                            form_data["relationship_id"] = relationship_id_for_clone
                        
                        response = requests.post(
                            f"{API_BASE_URL}/voice/clone",
                            files={"audio_file": uploaded_audio},
                            data=form_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.voice_cloned = True
                            st.session_state.voice_id = result['voice_id']
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                        else:
                            st.error(f"❌ Cloning failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please provide a voice name and upload an audio file")
    
    with col2:
        st.markdown("### 💡 Requirements")
        st.markdown("""
        <div class="info-box">
        
        **Audio Quality:**
        - Duration: 30-60 seconds
        - Quality: Clear, no noise
        - Content: Natural speech
        - Format: MP3 or WAV
        
        **Best Results:**
        - Single speaker
        - Normal speaking pace
        - Various emotions
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("🤖 Step 2: Create Conversation Agent")
    st.info("🎭 Define personality traits and conversational patterns using Mistral Large 2")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        agent_name = st.text_input("Name", placeholder="e.g., Grandma")
        relationship = st.text_input("Relationship", placeholder="e.g., Grandmother")
        personality = st.text_area(
            "Personality Traits",
            placeholder="e.g., Warm, caring, always concerned about health and well-being",
            height=100
        )
        
        st.markdown("**Speech Patterns & Catchphrases** *(Optional)*")
        col1a, col1b = st.columns(2)
        
        with col1a:
            pattern1 = st.text_input("Pattern 1", placeholder="e.g., Dear child")
            pattern2 = st.text_input("Pattern 2", placeholder="e.g., Take care")
        
        with col1b:
            pattern3 = st.text_input("Pattern 3", placeholder="e.g., Did you eat?")
            pattern4 = st.text_input("Pattern 4", placeholder="e.g., Stay safe")
        
        patterns = [p for p in [pattern1, pattern2, pattern3, pattern4] if p]
        
        if st.button("🎯 Create Agent", type="primary"):
            if agent_name and relationship and personality:
                with st.spinner("🔄 Creating conversation agent with AI personality..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/agent/create",
                            json={
                                "name": agent_name,
                                "relationship": relationship,
                                "personality_traits": personality,
                                "speech_patterns": patterns
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.agent_created = True
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                        else:
                            st.error(f"❌ Creation failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please fill in all required fields")
    
    with col2:
        st.markdown("### 🎭 Example Profile")
        st.markdown("""
        <div class="info-box">
        
        **Grandmother Character:**
        - Name: Grandma Linda
        - Relationship: Grandmother
        - Traits: Warm, nurturing, loves to tell stories
        - Patterns: "Dear child", "Take care", "Did you eat well?"
        
        **Father Character:**
        - Name: Dad
        - Relationship: Father  
        - Traits: Supportive, wise, gives life advice
        - Patterns: "Son/Daughter", "I'm proud of you", "Work hard"
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.header("💬 Step 3: Start Conversation")
    
    if not st.session_state.agent_created:
        st.warning("⚠️  Please create a conversation agent first (Step 2)")
    elif not st.session_state.voice_cloned:
        st.warning("⚠️  Please clone a voice first (Step 1)")
    else:
        st.success("✅ System ready! Start your conversation below.")
        
        mode = st.radio("Select Mode", ["💬 Text Chat", "🎙️ Voice Chat (Beta)"])
        
        if mode == "💬 Text Chat":
            st.markdown("#### 📝 Text Conversation")
            user_input = st.text_input("Your Message", placeholder="Type your message here...", key="text_input")
            
            col_send, col_clear, col_voice = st.columns([2, 1, 1])
            with col_send:
                send_btn = st.button("📤 Send", type="primary", use_container_width=True)
            with col_voice:
                voice_btn = st.button("🔊 TTS", use_container_width=True)
            with col_clear:
                clear_btn = st.button("🗑️ Clear", type="secondary", use_container_width=True)
            
            if send_btn and user_input:
                with st.spinner("🤔 Generating response with AI..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/chat/text",
                            json={"message": user_input, "use_voice": False}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.chat_history.append({
                                "user": user_input,
                                "agent": result['agent_response']
                            })
                            
                            st.markdown(f"<div class='chat-message user-message'><strong>You:</strong> {user_input}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='chat-message agent-message'><strong>AI Agent:</strong> {result['agent_response']}</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if voice_btn and user_input and st.session_state.voice_id:
                with st.spinner("🎙️ Generating voice response..."):
                    try:
                        # Get text response first
                        response = requests.post(
                            f"{API_BASE_URL}/chat/text",
                            json={"message": user_input, "use_voice": False}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            ai_text = result['agent_response']
                            
                            # Generate voice with cloned voice
                            voice_response = requests.post(
                                f"{API_BASE_URL}/voice/quick-tts",
                                data={
                                    "text": ai_text,
                                    "voice_id": st.session_state.voice_id
                                }
                            )
                            
                            if voice_response.status_code == 200:
                                # Save and play audio
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                                    tmp_file.write(voice_response.content)
                                    audio_path = tmp_file.name
                                
                                st.session_state.chat_history.append({
                                    "user": user_input,
                                    "agent": ai_text
                                })
                                
                                st.markdown(f"<div class='chat-message user-message'><strong>You:</strong> {user_input}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='chat-message agent-message'><strong>AI Agent:</strong> {ai_text}</div>", unsafe_allow_html=True)
                                
                                # Play audio
                                st.audio(audio_path, format="audio/mp3")
                                st.success("✅ Voice response generated!")
                            else:
                                st.error("❌ Voice generation failed")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if clear_btn:
                st.session_state.chat_history = []
                st.success("✅ Conversation cleared!")
                st.rerun()
        
        else:  # Voice Chat Mode
            st.markdown("#### 🎙️ Voice-to-Voice Conversation")
            st.info("🎯 **Complete Flow**: Record → ASR → LLM → TTS → Play AI response in cloned voice")
            
            st.markdown("---")
            
            # Method 1: Upload Recording
            st.markdown("##### 📤 Method 1: Upload Your Recording")
            uploaded_recording = st.file_uploader(
                "Upload your voice recording (MP3/WAV)", 
                type=["mp3", "wav", "m4a"],
                key="voice_upload"
            )
            
            if st.button("🚀 Send Voice Message", type="primary", disabled=not uploaded_recording):
                if uploaded_recording and st.session_state.voice_id:
                    with st.spinner("🔄 Processing: ASR → LLM → TTS... Please wait..."):
                        try:
                            # Call simulate-call endpoint
                            files = {"audio_file": uploaded_recording}
                            data = {
                                "voice_id": st.session_state.voice_id,
                                "agent_name": "AI Agent"
                            }
                            
                            response = requests.post(
                                f"{API_BASE_URL}/voice/simulate-call",
                                files=files,
                                data=data,
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                # Get transcription from headers
                                user_message = response.headers.get('X-User-Message', '(transcribing...)')
                                ai_response = response.headers.get('X-AI-Response', '(generating...)')
                                
                                # Save audio response
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                                    tmp_file.write(response.content)
                                    audio_path = tmp_file.name
                                
                                # Update history
                                st.session_state.chat_history.append({
                                    "user": user_message,
                                    "agent": ai_response
                                })
                                
                                # Display results
                                st.success("✅ Voice call completed!")
                                st.markdown("---")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**🎧 Your Message (ASR):**")
                                    st.info(user_message)
                                
                                with col2:
                                    st.markdown(f"**🤖 AI Response (LLM):**")
                                    st.info(ai_response)
                                
                                st.markdown("**🔊 AI Voice Response:**")
                                st.audio(audio_path, format="audio/mp3")
                                
                                st.balloons()
                            else:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"❌ Voice call failed: {error_detail}")
                        
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timeout. This usually happens with long audio files. Try a shorter recording.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                else:
                    st.warning("⚠️ Please upload a recording and ensure voice is cloned")
            
            st.markdown("---")
            
            # Method 2: Browser Recording (Future)
            st.markdown("##### 🎤 Method 2: Browser Recording")
            st.info("🔜 Coming soon: Record directly in browser using Web Audio API")
            st.markdown("""
            **Planned Features:**
            - Real-time recording visualization
            - One-click record & send
            - Waveform display
            - Recording quality check
            """)

with tab5:
    st.header("📊 Conversation History")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("🔄 Refresh History", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE_URL}/chat/history")
                if response.status_code == 200:
                    history = response.json().get('history', [])
                    st.session_state.chat_history = history
                    st.success("✅ History refreshed")
            except Exception as e:
                st.error(f"Failed to refresh: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            try:
                requests.post(f"{API_BASE_URL}/chat/clear")
                st.session_state.chat_history = []
                st.success("✅ History cleared")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col3:
        export_btn = st.button("💾 Export", use_container_width=True, disabled=not st.session_state.chat_history)
    
    st.markdown("---")
    
    if st.session_state.chat_history:
        st.markdown(f"**Total Messages:** {len(st.session_state.chat_history) * 2}")
        st.markdown("---")
        
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            if isinstance(chat, dict) and 'user' in chat:
                st.markdown(f"<div class='chat-message user-message'><strong>You:</strong> {chat['user']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-message agent-message'><strong>AI Agent:</strong> {chat['agent']}</div>", unsafe_allow_html=True)
                if idx < len(st.session_state.chat_history) - 1:
                    st.markdown("---")
    else:
        st.info("📭 No conversation history yet. Start chatting in the 'Chat' tab!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <h3 style="margin: 0;">🎙️ Be With Me</h3>
    <p style="margin: 0.5rem 0;">AI-Powered Voice Cloning & Conversation System</p>
    <p style="margin: 0.5rem 0; font-size: 0.9em;">
        <strong>Tech Stack:</strong> Mistral Large 2 | ElevenLabs Voice AI | OpenAI Whisper | W&B Weave
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.8em; color: #999;">
        Built for NVIDIA AI Hackathon Singapore &copy; 2026
    </p>
</div>
""", unsafe_allow_html=True)
