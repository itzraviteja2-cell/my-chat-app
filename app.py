import streamlit as st
from google import genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="✨")

# 2. API Setup (New Google GenAI SDK)
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు! Streamlit Secrets లో చూడండి.")
    st.stop()

client = genai.Client(api_key=api_key)

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
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్", type=["png", "jpg", "jpeg"])

# 5. Main Chat Area
st.title("✨ Aurora AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Image Input Logic
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=200)
    if st.button("🔍 ఫోటో విశ్లేషించు"):
        with st.chat_message("assistant"):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=["ఈ ఫోటోలో ఏముందో వివరించండి.", image]
                )
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")

# 7. Main Chat Text Input
if prompt := st.chat_input("మీ సందేశాన్ని టైప్ చేయండి..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"ఎర్రర్ వివరాలు: {e}")
