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
        <circle cx="50" cy="50" r="45" fill="url(#auroraGrad)" />
        <defs>
            <linearGradient id="auroraGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#7928CA" />
                <stop offset="100%" style="stop-color:#00DFD8" />
            </linearGradient>
        </defs>
        <path d="M50 18 L58 40 L82 42 L63 57 L70 80 L50 66 L30 80 L37 57 L18 42 L42 40 Z" fill="#FFFFFF" />
    </svg>
    <h1 style="margin: 0; background: linear-gradient(45deg, #7928CA, #00DFD8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Aurora AI
    </h1>
</div>
""", unsafe_allow_html=True)

# 3. API క్లయింట్
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Streamlit Secrets లో GEMINI_API_KEY సెట్ చేయలేదు.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. సైడ్‌బార్ ఫీచర్స్ (మైక్ + ఫైల్ అప్‌లోడ్)
st.sidebar.header("🛠️ కంట్రోల్ ప్యానెల్")
audio_input = st.sidebar.audio_input("🎙️ మైక్: వాయిస్ మెసేజ్")
uploaded_file = st.sidebar.file_uploader("📂 మీడియా: వీడియో/ఇమేజ్ అప్‌లోడ్", type=["mp4", "png", "jpg", "jpeg"])

# 5. చాట్ హిస్టరీ
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. ఇన్పుట్ తీసుకోవడం
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "ఈ ఆడియో/ఫైల్ ని విశ్లేషించి తెలుగులో చెప్పు."
    
    # యూజర్ మెసేజ్ సేవ్ చేయడం
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # AI స్పందన
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = [user_text]
            
            # ఆడియో ప్రాసెసింగ్
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_input.getvalue())
                    audio_ref = client.files.upload(file=tmp_audio.name)
                    contents_list.append(audio_ref)
            
            # వీడియో/ఫోటో ప్రాసెసింగ్
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    file_ref = client.files.upload(file=tmp_file.name)
                    contents_list.append(file_ref)

            # API కాల్ - మోడల్ పేరును తప్పు లేకుండా గుర్తించేలా సెట్ చేశాను
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents_list,
                )
            except Exception:
                # ఒకవేళ ఏమైనా ఇబ్బంది ఉంటే బ్యాకప్ మోడల్
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents_list,
                )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
