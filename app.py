import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Aurora AI", page_icon="🌌", layout="centered")

# ChatGPT Style UI (Dark Theme + White Text Visibility)
st.markdown("""
<style>
    .stApp { background-color: #212121; color: #ffffff !important; }
    div[data-testid="stChatMessage"] { color: #ffffff !important; }
    div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
    header, footer { visibility: hidden; }
    
    .main-title { 
        text-align: center; 
        font-size: 2.2rem; 
        font-weight: 600; 
        color: #ffffff; 
        margin-bottom: 20px; 
    }
    
    .stChatInputContainer { border-radius: 20px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌌 Aurora AI</div>', unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Buttons Row directly above Chat Input ---
col_file, col_mic = st.columns([1, 1])

with col_file:
    uploaded_file = st.file_uploader("➕ Upload Photo/File", type=["png", "jpg", "jpeg", "pdf", "txt"], label_visibility="collapsed")

with col_mic:
    st.components.v1.html("""
        <button onclick="startDictation()" style="width:100%; background:#2f2f2f; color:white; border:1px solid #444; border-radius:12px; padding:6px; cursor:pointer;">
            🎤 Voice Input
        </button>
        <script>
            function startDictation() {
                if ('webkitSpeechRecognition' in window) {
                    var rec = new webkitSpeechRecognition();
                    rec.lang = 'en-US';
                    rec.start();
                    rec.onresult = function(e) {
                        window.parent.postMessage({type: 'streamlit:setComponentValue', value: e.results[0][0].transcript}, '*');
                    };
                }
            }
        </script>
    """, height=40)

# Main Chat Box
prompt = st.chat_input("Ask Aurora AI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... ⏳")
        
        try:
            # 100% 404 ఎర్రర్ రాకుండా అందుబాటులో ఉన్న మోడల్‌ను మాత్రమే ఎంచుకుంటుంది
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
