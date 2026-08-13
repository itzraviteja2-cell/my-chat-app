import streamlit as st
import google.generativeai as genai
from PIL import Image

# Page Config
st.set_page_config(page_title="Smart AI", page_icon="logo.png", layout="centered")

# API Setup
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Gemini Flash మోడల్ మల్టీ మోడల్ (Text/Image/Audio) కి సపోర్ట్ చేస్తుంది
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
        st.error(f"API Key సెటప్ లోపం: {e}")
    st.stop()

st.title("✨ Smart AI")

# --- కొత్త ఫీచర్లు: ఫోటో & మైక్ కంట్రోల్స్ ---
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్ చేయండి", type=["png", "jpg", "jpeg"])

with col2:
    audio_value = st.audio_input("🎙️ మైక్ (వాయిస్)")

# చాట్ హిస్టరీ
if "messages" not in st.session_state:
    st.session_state.messages = []

# హిస్టరీని చూపించడం
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# చాట్ ఇన్‌పుట్
user_input = st.chat_input("మీ సందేశాన్ని టైప్ చేయండి...")

# --- లాజిక్ ---
# 1. ఒకవేళ యూజర్ ఫోటో పంపిస్తే
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("ఫోటో గురించి అడగండి"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరించండి", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# 2. ఒకవేళ యూజర్ ఆడియో పంపిస్తే
if audio_value:
    with st.chat_message("assistant"):
        st.write("వాయిస్ వింటున్నాను...")
        # ఆడియోను AI కి పంపుతున్నాం
        response = model.generate_content(["ఈ వాయిస్‌లో ఉన్న విషయాన్ని అర్థం చేసుకోండి", audio_value])
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 3. టెక్స్ట్ ఇన్‌పుట్
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response = model.generate_content(user_input)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
