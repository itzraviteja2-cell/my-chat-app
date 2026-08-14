import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="✨")

# 2. API Setup
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు! Secrets సరిగ్గా ఉన్నాయో లేదో చూడండి.")
    st.stop()

genai.configure(api_key=api_key)

# మోడల్ పేరును అత్యంత కొత్త మరియు స్థిరమైన 'gemini-2.5-flash' కి మారాము
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. SIDEBAR
with st.sidebar:
    st.title("✨ Aurora AI Menu")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్", type=["png", "jpg"])
    st.write("🎙️ వాయిస్ ఇన్‌పుట్:")
    audio_value = st.audio_input("వాయిస్ రికార్డ్")

# 5. Main Chat Area
st.title("✨ Aurora AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Logic (Image Handling)
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=200)
    if st.button("🔍 ఫోటో విశ్లేషించు"):
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరించండి.", image])
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")

# 7. Main Chat Input
if prompt := st.chat_input("మీ సందేశాన్ని టైప్ చేయండి..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"ఎర్రర్ వివరాలు: {e}")
