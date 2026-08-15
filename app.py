import streamlit as st
from google import genai
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
    st.error("API Key దొరకలేదు! Secrets సరిచూసుకోండి.")
    st.stop()

client = genai.Client(api_key=api_key)

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
            contents = [user_text]
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as t:
                    t.write(audio_input.getvalue())
                    contents.append(client.files.upload(path=t.name))
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as t:
                    t.write(uploaded_file.getvalue())
                    contents.append(client.files.upload(path=t.name))

            # అందుబాటులో ఉన్న మోడల్స్ వరుసగా ట్రై చేస్తుంది
            working_model = None
            available_models = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"]
            
            for m in available_models:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=contents
                    )
                    working_model = m
                    break
                except Exception:
                    continue

            if working_model and response:
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                message_placeholder.markdown("మోడల్ అందుబాటులో లేదు. దయచేసి API Key సరిచూసుకోండి.")

        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
