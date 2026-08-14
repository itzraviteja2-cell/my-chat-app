import streamlit as st
from google import genai
import os
import tempfile

# 1. PAGE SETTINGS
st.set_page_config(
    page_title="Aurora AI",
    page_icon="🤖",
    layout="wide"
)

# 2. AURORA AI HEADER
st.title("🤖 Aurora AI")
st.caption("ప్రశ్నలు అడగండి AI/audio)
st.markdown("---")

# 3. GEMINI API SETUP
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY Streamlit Secrets లో లభించలేదు.")
    st.stop()

# సరికొత్త క్లయింట్ సెటప్
client = genai.Client(api_key=api_key)

# 4. SIDEBAR TOOLS (ఫైల్ & వాయిస్ అప్లోడ్)
st.sidebar.header("📁 మీడియా & ఆడియో టూల్స్")

# వాయిస్ ఇన్పుట్
audio_input = st.sidebar.audio_input("🎙️ వాయిస్ రికార్డ్ చేయండి")

# ఫైల్ అప్లోడర్
uploaded_file = st.sidebar.file_uploader(
    "📤 వీడియో లేదా ఇమేజ్ అప్లోడ్ చేయండి",
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

# వాయిస్ లేదా టెక్స్ట్ ఇన్పుట్ చెక్ చేయడం
if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "ఈ ఆడియో/ఫైల్ ని విశ్లేషించి సమాధానం ఇవ్వు"
    
    # యూజర్ మెసేజ్ చూపించడం
    if prompt or audio_input:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
            
    # AI రెస్పాన్స్
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = []
            
            # 1. టెక్స్ట్ ప్రాంప్ట్ యాడ్ చేయడం
            contents_list.append(user_text)
            
            # 2. అప్లోడ్ చేసిన ఫైల్ (ఇమేజ్/వీడియో) ప్రాసెస్ చేయడం
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                uploaded_media = client.files.upload(file=tmp_file_path)
                contents_list.append(uploaded_media)
                os.unlink(tmp_file_path)

            # 3. రికార్డ్ చేసిన ఆడియో ప్రాసెస్ చేయడం
            if audio_input is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                    tmp_audio.write(audio_input.getvalue())
                    tmp_audio_path = tmp_audio.name
                
                uploaded_audio = client.files.upload(file=tmp_audio_path)
                contents_list.append(uploaded_audio)
                os.unlink(tmp_audio_path)
            
            # జెమిని API కాల్ (రద్దీ తక్కువగా ఉండే gemini-2.0-flash మోడల్ తో)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=contents_list
            )
            
            # సమాధానాన్ని స్క్రీన్ పై చూపించడం
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # ヒస్టరీలో సేవ్ చేయడం
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ ఎర్రర్ వచ్చింది: {e}")
