import streamlit as st
from google import genai
import os

# 1. ChatGPT UI Page Setup
st.set_page_config(page_title="Aurora AI", page_icon="🌌", layout="centered")

# Custom ChatGPT Style CSS
st.markdown("""
<style>
    /* Dark Theme ChatGPT look */
    .stApp {
        background-color: #212121;
        color: #ececec;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input box styling */
    .stChatInputContainer {
        border-radius: 24px !important;
        background-color: #2f2f2f !important;
        border: 1px solid #424242 !important;
    }
    
    /* Title Styling */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌌 Aurora AI</div>', unsafe_allow_html=True)

# 2. API Key Check
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Session State setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Input Controls (+ Symbol & Voice Mic Setup)
col_file, col_voice = st.columns([1, 1])

with col_file:
    uploaded_file = st.file_uploader("➕ Upload Image/File", type=["png", "jpg", "jpeg", "pdf", "txt"], label_visibility="collapsed")

with col_voice:
    # Web Speech API Voice Input HTML Button
    st.components.v1.html("""
        <button onclick="startDictation()" style="background-color: #2f2f2f; color: white; border: 1px solid #424242; border-radius: 20px; padding: 6px 14px; cursor: pointer; font-size: 14px;">
            🎤 Tap to Speak
        </button>
        <script>
            function startDictation() {
                if (window.hasOwnProperty('webkitSpeechRecognition')) {
                    var recognition = new webkitSpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.lang = "en-US";
                    recognition.start();
                    recognition.onresult = function(e) {
                        var text = e.results[0][0].transcript;
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
                        recognition.stop();
                    };
                    recognition.onerror = function(e) { recognition.stop(); }
                }
            }
        </script>
    """, height=40)

# 5. Main Chat Input Box
prompt = st.chat_input("Ask Aurora AI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... ⏳")
        
        try:
            # Automatic active model detection (Prevents 404 errors)
            active_models = [m.name for m in client.models.list() if "generateContent" in m.supported_actions]
            selected_model = active_models[0] if active_models else "gemini-1.5-flash"
            
            response = client.models.generate_content(
                model=selected_model,
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error: {e}")
