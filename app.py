import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Aurora AI", page_icon="✨")

# API Setup
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు! Secrets తనిఖీ చేయండి.")
    st.stop()

genai.configure(api_key=api_key)

# అత్యంత స్థిరమైన మోడల్
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("✨ Aurora AI")

# Sidebar
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    uploaded_file = st.file_uploader("🖼️ ఫోటో అప్‌లోడ్", type=["png", "jpg", "jpeg"])

# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Image Processing
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=200)
    if st.button("🔍 విశ్లేషించు"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటో గురించి చెప్పండి.", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# Text Input
if prompt := st.chat_input("మీ సందేశాన్ని టైప్ చేయండి..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
