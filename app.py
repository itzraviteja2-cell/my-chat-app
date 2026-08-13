import streamlit as st
import google.generativeai as genai
from PIL import Image

# Page Config - లోగో, టైటిల్ అమరిక
st.set_page_config(
    page_title="Aurora AI", 
    page_icon="logo.png", 
    layout="centered"
)

# టెక్స్ట్ బాక్స్ నుండి బయటకు రాకుండా డిజైన్ స్టైలింగ్
st.markdown("""
    <style>
    .stChatMessage, .stMarkdown, p {
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        white-space: pre-wrap !important;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# API Setup
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Key సెటప్ లోపం: {e}")
    st.stop()

st.title("✨ Aurora AI")

# --- ఫోటో & మైక్ కంట్రోల్స్ ---
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
# 1. ఫోటో పంపినప్పుడు
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("ఫోటో గురించి అడగండి"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరించండి", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# 2. వాయిస్ పంపినప్పుడు
if audio_value:
    with st.chat_message("assistant"):
        st.write("వాయిస్ వింటున్నాను...")
        response = model.generate_content(["ఈ వాయిస్‌లో ఉన్న విషయాన్ని అర్థం చేసుకోండి", audio_value])
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 3. టెక్స్ట్ పంపినప్పుడు
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response = model.generate_content(user_input)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
