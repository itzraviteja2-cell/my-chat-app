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

# 4. SIDEBAR
st.sidebar.title("🛠️ టూల్స్")

if st.sidebar.button("➕ కొత్త చాట్", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

audio_input = st.sidebar.audio_input("🎙️ మైక్")
uploaded_file = st.sidebar.file_uploader("📂 మీడియా (ఫోటో/వీడియో)", type=["mp4", "png", "jpg", "jpeg"])

# 5. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT & RESPONSE
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "ఈ ఫైల్ గురించి వివరించండి."
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            inputs = [user_text]
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as t:
                    t.write(audio_input.getvalue())
                    inputs.append(client.files.upload(path=t.name))
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as t:
                    t.write(uploaded_file.getvalue())
                    inputs.append(client.files.upload(path=t.name))
            
            # Interactions API సరిచేసిన పారామీటర్ల నిర్మాణం
            response = client.interactions.create(
                model="models/gemini-2.5-flash", 
                input=inputs[0] if len(inputs) == 1 else inputs
            )
            
            # అవుట్‌పుట్ పొందడం
            result_text = ""
            if hasattr(response, 'outputs') and response.outputs:
                result_text = response.outputs[-1].text
            elif hasattr(response, 'text'):
                result_text = response.text
            else:
                result_text = str(response)
            
            message_placeholder.markdown(result_text)
            st.session_state.messages.append({"role": "assistant", "content": result_text})
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
