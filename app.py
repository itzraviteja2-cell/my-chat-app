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
    .stChatInputContainer {
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. API Setup & Model Initialization
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API Key దొరకలేదు! Streamlit Secrets లో GEMINI_API_KEY ని తనిఖీ చేయండి.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

# Initialize Model
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"మోడల్ లోడ్ చేయడంలో లోపం జరిగింది: {e}")
    st.stop()

# 4. App Title
st.title("✨ Aurora AI")

# 5. Media Controls
col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్ చేయండి", type=["png", "jpg", "jpeg"])

with col2:
    audio_value = st.audio_input("🎙️ మైక్ (వాయిస్)")

# 6. Chat History Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 7. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 8. Chat Input Box
user_input = st.chat_input("మీ సందేశాన్ని టైప్ చేయండి...")

# 9. Logic for Image Processing
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("ఫోటో గురించి అడగండి"):
        with st.chat_message("assistant"):
            with st.spinner("విశ్లేషిస్తోంది..."):
                try:
                    response = model.generate_content(["ఈ ఫోటోలో ఏమిందో వివరంగా వివరించండి.", image])
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"ఎర్రర్: {e}")

# 10. Logic for Voice Input
if audio_value:
    with st.chat_message("assistant"):
        st.write("వాయిస్ వింటున్నాను...")
        # Note: Audio processing logic can be extended here

# 11. Logic for Text Chat Input
if user_input:
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("ఆలోచిస్తోంది..."):
            try:
                response = model.generate_content(user_input)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"సందేశం పంపడంలో ఎర్రర్ వచ్చింది: {e}")
