import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="✨")

# 2. API Setup - ఇక్కడ జాగ్రత్తగా చూడండి
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు! సెట్టింగ్స్‌లో చెక్ చేయండి.")
    st.stop()

genai.configure(api_key=api_key)

# మోడల్ పేరు మార్చాను (gemini-1.5-pro ఎక్కువ స్థిరంగా ఉంటుంది)
model = genai.GenerativeModel('gemini-1.5-pro')

# 3. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. SIDEBAR (అన్ని కంట్రోల్స్ ఇక్కడే ఉంటాయి - ఇది క్రాష్ అవ్వదు)
with st.sidebar:
    st.title("✨ ఆప్షన్లు")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    uploaded_file = st.file_uploader("➕ ఫోటో అప్‌లోడ్", type=["png", "jpg"])
    
    st.markdown("---")
    st.write("🎙️ వాయిస్ ఇన్‌పుట్:")
    audio_value = st.audio_input("వాయిస్ రికార్డ్ చేయండి")

# 5. Main Chat Area
st.title("✨ Aurora AI")

# డిస్‌ప్లే మెసేజెస్
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Logic (ఫోటో అప్‌లోడ్ అయితే)
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("🔍 ఫోటో విశ్లేషించు"):
        with st.chat_message("assistant"):
            response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరించండి.", image])
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# 7. Main Chat Input
if prompt := st.chat_input("మీ సందేశాన్ని టైప్ చేయండి..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("ఆలోచిస్తోంది..."):
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")
