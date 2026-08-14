import streamlit as st
from google import genai
import os
import tempfile

# 1. PAGE SETTINGS
st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide"
)

# 2. AURORA AI HEADER
st.title("🌌 Aurora AI")
st.caption("మీ వ్యక్తిగత AI & వీడియో/ఆడియో అసిస్టెంట్")
st.markdown("---")

# 3. GEMINI API SETUP
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY Streamlit Secrets లో లభించలేదు.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. SIDEBAR TOOLS (మైక్ + ఫైల్ అప్‌లోడ్)
st.sidebar.header("🛠️ మీడియా & ఆడియో టూల్స్")

# మైక్ ఆప్షన్
audio_input = st.sidebar.audio_input("🎙️ వాయిస్ రికార్డ్ చేయండి")

# ఫైల్ అప్‌లోడర్
uploaded_file = st.sidebar.file_uploader(
    "📂 వీడియో లేదా ఇమేజ్ అప్‌లోడ్ చేయండి", 
    type=["mp4", "mov", "avi", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    if uploaded_file.type.startswith("video"):
        st.sidebar.video(uploaded_file)
    elif uploaded_file.type.startswith("image"):
        st.sidebar.image(uploaded_file)

# 5. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT & RESPONSE PROCESSING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

# వాయిస్ లేదా టెక్స్ట్ ఇన్పుట్ ఉంటే ప్రాసెస్ చేస్తుంది
if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "ఈ ఆడియో/ఫైల్ ని విశ్లేషించి సమాధానం ఇవ్వండి."
    
    # యూజర్ మెసేజ్ చూపించడం
    if prompt:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

    # AI రెస్పాన్స్
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = [user_text]
            
            # ఆడియో ఫైల్ ఉంటే
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_input.getvalue())
                    audio_ref = client.files.upload(file=tmp_audio.name)
                    contents_list.append(audio_ref)

            # వీడియో లేదా ఫోటో ఉంటే
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    file_ref = client.files.upload(file=tmp_file.name)
                    contents_list.append(file_ref)

            # API Call (gemini-1.5-flash మోడల్ సరిగ్గా పనిచేస్తుంది)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents_list,
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
