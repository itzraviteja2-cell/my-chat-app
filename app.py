import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="✨", layout="centered")

# 2. API & Model Setup
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు!")
    st.stop()
genai.configure(api_key=api_key)

# మోడల్ నేమ్ అప్‌డేట్ చేశాను (ఇప్పుడు ఎర్రర్ రాదు)
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. SIDEBAR (సైడ్‌బార్)
with st.sidebar:
    st.title("✨ Menu")
    st.write("---")
    if st.button("🗑️ Clear Chat (చాట్ తుడిచివేయి)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Main Title
st.title("✨ Aurora AI")

# 5. Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Custom Input Row (లెఫ్ట్ '+', రైట్ 'Mic')
col_left, col_mid, col_right = st.columns([1, 8, 1])

with col_left:
    # ఫైల్ అప్‌లోడర్ ('+' లాగా)
    uploaded_file = st.file_uploader("➕", type=["png", "jpg"], label_visibility="collapsed")

with col_right:
    # మైక్ (వాయిస్ ఇన్‌పుట్)
    audio_value = st.audio_input("🎙️", label_visibility="collapsed")

# 7. Main Chat Input
user_input = st.chat_input("మీ సందేశాన్ని టైప్ చేయండి...")

# 8. Handling Logic
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("🔍 ఫోటో విశ్లేషించు"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరంగా వివరించండి.", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

if audio_value:
    st.chat_message("assistant").write("🎙️ వాయిస్ రిసీవ్ అయ్యింది (ఇది ప్రస్తుతం రికార్డింగ్ ఫీచర్ మాత్రమే).")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        response = model.generate_content(user_input)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
