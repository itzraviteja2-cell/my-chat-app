import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Config
st.set_page_config(
    page_title="Aurora AI",
    page_icon="✨",
    layout="centered"
)

# 2. Responsive & Clean UI CSS
st.markdown("""
<style>
    .stChatMessage, .stMarkdown, p {
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        white-space: pre-wrap !important;
    }
    /* బటన్లు, విజెట్ల మార్జిన్ కుదించడం */
    .stFileUploader, .stAudioInput {
        margin-bottom: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. API Setup
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API Key దొరకలేదు! Streamlit Secrets లో GEMINI_API_KEY ని తనిఖీ చేయండి.")
    st.stop()

genai.configure(api_key=api_key)

# 4. Session State Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. SIDEBAR (సైడ్‌బార్: మెనూ, సెట్టింగ్స్, క్లియర్ చాట్)
with st.sidebar:
    st.title("✨ Aurora AI Menu")
    st.divider()
    
    # Clear Chat Button
    st.subheader("🧹 చాట్ నిలిపివేత")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    creativity = st.slider("క్రియేటివిటీ (Creativity)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    st.divider()
    
    # Stats
    st.subheader("📊 Chat Stats")
    st.write(f"మొత్తం సందేశాలు: **{len(st.session_state.messages)}**")

# 6. Model Setup
try:
    generation_config = genai.GenerationConfig(temperature=creativity)
    model = genai.GenerativeModel('gemini-1.5-flash-8b', generation_config=generation_config)
except Exception as e:
    st.error(f"మోడల్ లోడ్ చేయడంలో లోపం: {e}")
    st.stop()

# 7. App Title
st.title("✨ Aurora AI")

# 8. Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 9. Bottom Media Inputs (ఫోటో మరియు వాయిస్ పక్కపక్కనే 2 కాలమ్స్)
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("🖼️ ఫోటో", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

with col2:
    audio_value = st.audio_input("🎙️ మైక్", label_visibility="collapsed")

# 10. Main Chat Input Box (ఎప్పుడూ స్క్రీన్ కింద ఉంటుంది)
user_input = st.chat_input("మీ సందేశాన్ని టైప్ చేయండి...")

# 11. Process Photo Upload
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="అప్‌లోడ్ చేసిన ఫోటో", width=200)
    if st.button("🔍 ఈ ఫోటోను విశ్లేషించు"):
        with st.chat_message("assistant"):
            with st.spinner("ఫోటోని చూస్తున్నాను..."):
                try:
                    response = model.generate_content(["ఈ ఫోటోలో ఏముందో వివరంగా వివరించండి.", image])
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"ఎర్రర్ వచ్చింది: {e}")

# 12. Process Voice Input
if audio_value:
    with st.chat_message("assistant"):
        st.write("🎙️ వాయిస్ రికార్డ్ అయ్యింది, ప్రాసెస్ చేస్తున్నాను...")

# 13. Process Text Input
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("ఆలోచిస్తోంది..."):
            try:
                response = model.generate_content(user_input)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")
