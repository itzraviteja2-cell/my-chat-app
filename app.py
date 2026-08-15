import streamlit as st
import google.generativeai as genai
import os
import tempfile

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide", initial_sidebar_state="expanded")

# 2. HIDE STREAMLIT MENU & FOOTER
hide_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌌 Aurora AI")

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు! Streamlit Secrets సరిచూసుకోండి.")
    st.stop()

genai.configure(api_key=api_key)

# 4. SIDEBAR (➕ కొత్త చాట్, 🎙️ మైక్, 📂 ఫైల్స్)
st.sidebar.title("🛠️ టూల్స్")

if st.sidebar.button("➕ కొత్త చాట్", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

audio_input = st.sidebar.audio_input("🎙️ మైక్ ద్వారా మాట్లాడండి")
uploaded_file = st.sidebar.file_uploader("📂 ఫోటో / వీడియో అప్‌లోడ్ చేయండి", type=["mp4", "png", "jpg", "jpeg", "mp3", "wav"])

# 5. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT & RESPONSE HANDLING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "అప్‌లోడ్ చేసిన ఫైల్ వివరాలను తెలపండి."
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            # అందుబాటులో ఉన్న మోడల్‌ను ఆటోమేటిక్‌గా కనుగొనడం
            valid_model_name = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_model_name = m.name
                    break

            if not valid_model_name:
                st.error("మీ API Key కి సరిపడే మోడల్ అందుబాటులో లేదు.")
                st.stop()

            model = genai.GenerativeModel(valid_model_name)
            
            contents = [user_text]
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as t:
                    t.write(audio_input.getvalue())
                    uploaded_audio = genai.upload_file(t.name)
                    contents.append(uploaded_audio)
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as t:
                    t.write(uploaded_file.getvalue())
                    uploaded_media = genai.upload_file(t.name)
                    contents.append(uploaded_media)

            response = model.generate_content(contents)
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
