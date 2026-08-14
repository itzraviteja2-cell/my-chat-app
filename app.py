import streamlit as st
from google import genai
import os
import tempfile

# 1. పేజీ సెట్టింగ్స్
st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide"
)

# 2. లోగో & హెడర్
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
    <svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="auroraGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#7928CA;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#FF0080;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#00DFD8;stop-opacity:1" />
            </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="45" fill="url(#auroraGrad)" />
        <path d="M50 18 L58 40 L82 42 L63 57 L70 80 L50 66 L30 80 L37 57 L18 42 L42 40 Z" fill="#FFFFFF" />
    </svg>
    <span style="font-size: 36px; font-weight: 800; background: linear-gradient(45deg, #7928CA, #FF0080, #00DFD8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Aurora AI
    </span>
</div>
""", unsafe_allow_html=True)

# 3. API క్లయింట్ సెటప్
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Streamlit Secrets లో GEMINI_API_KEY సెట్ చేయలేదు.")
    st.stop()

# 'google-genai' లైబ్రరీ కోసం సరైన క్లయింట్ ఇనిషియలైజేషన్
client = genai.Client(api_key=api_key)

# 4. సైడ్‌బార్ ఫీచర్స్
st.sidebar.header("🎬 మీడియా & వాయిస్")
audio_input = st.sidebar.audio_input("వాయిస్ రికార్డ్ చేయండి")
uploaded_file = st.sidebar.file_uploader("ఫైల్ అప్‌లోడ్", type=["mp4", "png", "jpg", "jpeg"])

# 5. చాట్ హిస్టరీ
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. ఇన్పుట్ & రెస్పాన్స్
prompt = st.chat_input("ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = [prompt]
            
            # ఫైల్స్ ఉంటే యాడ్ చేయడం
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                file_ref = client.files.upload(file=tmp_path)
                contents_list.append(file_ref)

            # రెస్పాన్స్ - మోడల్ పేరును మార్చకుండా ఉంచండి, ఇది లేటెస్ట్ మోడల్
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents_list,
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"ఎర్రర్: {e}")
