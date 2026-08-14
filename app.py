import streamlit as st
from google import genai
import os
import tempfile

# 1. పేజీ సెట్టింగ్స్ మరియు ఐకాన్
st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide"
)

# 2. అరోరా AI హెడర్ & SVG లోగో
logo_svg = """
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
"""
st.markdown(logo_svg, unsafe_allow_html=True)
st.caption("మీ వ్యక్తిగత AI & వీడియో అసిస్టెంట్ (తెలుగు సపోర్ట్‌తో)")

# 3. Gemini API సెటప్
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("దయచేసి మీ Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయండి.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. సైడ్‌బార్ - వీడియో/ఫోటో అప్‌లోడర్ & ఆడియో వాయిస్ ఇన్‌పుట్
st.sidebar.header("🎬 మీడియా & వాయిస్ ఇన్పుట్")

# ఆడియో / వాయిస్ మైక్ ఆప్షన్
st.sidebar.subheader("🎙️ మైక్ / వాయిస్ మెసేజ్")
audio_input = st.sidebar.audio_input("వాయిస్ రికార్డ్ చేయండి")

st.sidebar.markdown("---")
st.sidebar.subheader("📁 వీడియో/ఇమేజ్ ఫైల్")
uploaded_file = st.sidebar.file_uploader(
    "అప్‌లోడ్ చేయండి", 
    type=["mp4", "mov", "avi", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    if uploaded_file.type.startswith("video"):
        st.sidebar.video(uploaded_file)
    elif uploaded_file.type.startswith("image"):
        st.sidebar.image(uploaded_file)

# 5. చాట్ హిస్టరీ
if "messages" not in st.session_state:
    st.session_state.messages = []

# పాత మెసేజ్‌లు చూపించడం
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. ప్రొసెస్ చేయడానికి ఇన్పుట్ తీసుకోవడం
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

# వాయిస్ ఇన్పుట్ వస్తే దాన్ని ప్రాసెస్ చేయడానికి సపోర్ట్
if audio_input and not prompt:
    prompt = "ఈ వాయిస్ రికార్డింగ్ విని తెలుగులో స్పష్టంగా జవాబు ఇవ్వండి."

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = [prompt]
            
            # వాయిస్ ఆడియో ఫైల్ ఉంటే
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_input.getvalue())
                    audio_path = tmp_audio.name
                audio_ref = client.files.upload(file=audio_path)
                contents_list.append(audio_ref)

            # వీడియో/ఫోటో ఫైల్ ఉంటే
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                uploaded_file_ref = client.files.upload(file=tmp_file_path)
                contents_list.append(uploaded_file_ref)

            # సరిచేసిన మోడల్ నేమ్‌తో API కాల్ (gemini-1.5-flash)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents_list,
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
