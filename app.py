 importstreamlitas st
 importgoogle.generativeaias genai
 importos
 importtempfile

# 1. PAGE SETTINGS
st.set_page_config(
    page_title="Aurora AI", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. HEADER & CSS
hide_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌌 Aurora AI")
st.caption("మీ వ్యక్తిగత AI అసిస్టెంట్")

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key Missing! Streamlit Secrets సరిచూసుకోండి.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. SIDEBAR (➕ బటన్ & 🎙️ మైక్ స్పష్టంగా కనిపిస్తాయి)
st.sidebar.title("🛠️ టూల్స్ & ఆప్షన్లు")

# ➕ కొత్త చాట్ బటన్
if st.sidebar.button("➕ కొత్త చాట్ (New Chat)", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# 🎙️ మైక్ ఆప్షన్
st.sidebar.subheader("🎙️ వాయిస్ మెసేజ్")
audio_input = st.sidebar.audio_input("ఇక్కడ మాట్లాడండి")

st.sidebar.markdown("---")

# 📂 ఫైల్ అప్‌లోడర్
st.sidebar.subheader("📂 ఫైల్ అప్‌లోడ్")
uploaded_file = st.sidebar.file_uploader("ఫోటో లేదా వీడియో", type=["mp4", "png", "jpg", "jpeg"])

# 5. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT & GENERATION
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt or audio_input or uploaded_file:
    user_text = prompt if prompt else "ఈ ఆడియో లేదా ఫైల్ ని విశ్లేషించి వివరించండి."
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            contents = [user_text]
            
            # ఆడియో ప్రాసెసింగ్
            if audio_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as t:
                    t.write(audio_input.getvalue())
                    uploaded_audio = client.files.upload(file=t.name)
                    contents.append(uploaded_audio)
                    
            # మీడియా ప్రాసెసింగ్
            if uploaded_file:
                ext = uploaded_file.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as t:
                    t.write(uploaded_file.getvalue())
                    uploaded_media = client.files.upload(file=t.name)
                    contents.append(uploaded_media)
            
            # Gemini 2.5 Flash మోడల్
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )
            
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
