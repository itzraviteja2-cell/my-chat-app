import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="✨")

# 2. API Setup
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు!")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Sidebar Options
with st.sidebar:
    st.title("✨ Menu")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    # ఫైల్ అప్‌లోడ్ సైడ్‌బార్‌లో పెడితే యాప్ క్రాష్ అవ్వదు
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్", type=["png", "jpg"])

# 5. Main Chat UI
st.title("✨ Aurora AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Logic for Input
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=200)
    if st.button("🔍 ఫోటో విశ్లేషించు"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరించండి.", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

if user_input := st.chat_input("మీ సందేశాన్ని టైప్ చేయండి..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("ఆలోచిస్తోంది..."):
            try:
                response = model.generate_content(user_input)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"ఎర్రర్: {e}")
