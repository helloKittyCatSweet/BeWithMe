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
tab1, tab2, tab3, tab4 = st.tabs(["🎤 Clone Voice", "🤖 Create Agent", "💬 Chat", "📊 History"])

with tab1:
    st.header("🎤 Step 1: Clone Voice")
    st.info("📤 Upload a 30-second audio sample to clone the voice using ElevenLabs Instant Voice Cloning")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        voice_name = st.text_input("Voice Name", placeholder="e.g., Grandmother's Voice")
        voice_desc = st.text_area("Voice Description (Optional)", placeholder="e.g., Warm, gentle, and caring tone")
        uploaded_audio = st.file_uploader("Upload Audio File (.mp3 or .wav)", type=["mp3", "wav"])
        
        if st.button("🚀 Clone Voice", type="primary", disabled=not uploaded_audio):
            if uploaded_audio and voice_name:
                with st.spinner("🔄 Cloning voice... This may take a moment..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/voice/clone",
                            files={"audio_file": uploaded_audio},
                            data={
                                "voice_name": voice_name,
                                "description": voice_desc
                            }
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

with tab2:
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

with tab3:
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
            
            col_send, col_clear = st.columns([3, 1])
            with col_send:
                send_btn = st.button("📤 Send Message", type="primary", use_container_width=True)
            with col_clear:
                clear_btn = st.button("🗑️ Clear", type="secondary", use_container_width=True)
            
            if send_btn and user_input:
                with st.spinner("🤔 Generating response with AI..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/chat/text",
                            json={"message": user_input}
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
            
            if clear_btn:
                st.session_state.chat_history = []
                st.success("✅ Conversation cleared!")
                st.rerun()
        
        else:
            st.info("🎙️ Voice chat mode coming soon! This will enable full speech-to-speech conversation.")

with tab4:
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
