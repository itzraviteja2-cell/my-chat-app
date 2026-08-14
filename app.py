import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(
    page_title="Aurora AI",
    page_icon="✨",
    layout="centered"
)

# 2. Responsive Layout CSS
st.markdown("""
<style>
    .stChatMessage, .stMarkdown, p {
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        white-space: pre-wrap !important;
    }
    div[data-testid="stFileUploader"] {
        margin-top: 0px;
    }
</style>
""", unsafe_allow_html=True)

# 3. API Setup & Model Initialization
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API Key దొరకలేదు! Streamlit Secrets లో GEMINI_API_KEY ని తనిఖీ చేయండి.")
    st.stop()

# Configure API Key
genai.configure(api_key=api_key)

# Initialize Model (పక్కాగా పనిచేసే మోడల్ పేరు)
try:
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
except Exception as e:
    st.error(f"మోడల్ లోడ్ చేయడంలో లోపం జరిగింది: {e}")
    st.stop()

# 4. App Title
st.title("✨ Aurora AI")

# 5. Chat History Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 7. Bottom Controls
st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("🖼️ ఫోటో ఎంచుకోండి", type=["png", "jpg", "jpeg"])

with col2:
    audio_value = st.audio_input("🎙️ మైక్ (వాయిస్)")

# 8. Main Chat Input Box
user_input = st.chat_input("మీ సందేశాన్ని టైప్ చేయండి...")

# 9. Image Processing Logic
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("ఈ ఫోటో గురించి విశ్లేషించు"):
        with st.chat_message("assistant"):
            with st.spinner("ఫోటోని చూస్తున్నాను..."):
                try:
                    response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరంగా వివరించండి.", image])
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"ఎర్రర్ వచ్చింది: {e}")

# 10. Voice Logic
if audio_value:
    with st.chat_message("assistant"):
        st.write("వాయిస్ రికార్డ్ అయ్యింది, ప్రాసెస్ చేస్తున్నాను...")

# 11. Text Chat Logic
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("ఆలోచిస్తోంది..."):
            try:
                response = model.generate_content(user_input)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"సందేశం పంపడంలో ఎర్రర్ వచ్చింది: {e}")
