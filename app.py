import streamlit as st
import google.generativeai as genai

# Streamlit Secrets నుండి API Key ని పొందడం
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("చాలా முக்கியం: Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయలేదు!")
    st.stop()

# గూగుల్ రికమండ్ చేసిన సరికొత్త అఫీషియల్ మోడల్
model = genai.GenerativeModel('gemini-2.0-flash')

# సైడ్‌బార్ సమాచారం మరియు ఫీచర్స్
with st.sidebar:
    st.title("⚙️ సెట్టింగ్స్ / Features")
    
    app_mode = st.radio(
        "మీరు ఏం చేయాలనుకుంటున్నారు?:",
        ["🤖 AI చాటింగ్ (Chat)", "🎬 వీడియో ఎడిటింగ్ అసిస్టెంట్ (Video Assistant)"]
    )
    
    st.write("---")
    
    language = st.selectbox(
        "సమాధానం చెప్పాల్సిన భాష (Language):",
        ["Telugu (తెలుగు)", "English", "Hindi (हिंदी)"]
    )
    
    st.write("---")
    st.write("### 🤖 యాప్ వివరాలు:")
    st.info("ఈ **Smart AI** చాట్‌బాట్‌ను రవీんだర్ గారు రూపొందించారు.")
    
    if st.button("🧹 చాట్ క్లియర్ చేయండి (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

# ----------------- మోడ్ 1: AI చాటింగ్ -----------------
if app_mode == "🤖 AI చాటింగ్ (Chat)":
    st.title("✨ smart AI")
    st.subheader("మీ స్మార్ట్ ఆలోచనలకు.. సరైన AI తోడు!")
    st.write("మీకు కావలసిన ప్రశ్నను కింద అడగండి:")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_input := st.chat_input("మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("సమాధానం కోసం వెతుకుతున్నాను..."):
                try:
                    prompt = f"Please respond strictly in {language}. User question: {user_input}"
                    response = model.generate_content(prompt)
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"ఓ చిన్న సమస్య వచ్చింది: {e}")

# ----------------- మోడ్ 2: వీడియో ఎడిటింగ్ అసిస్టెంట్ -----------------
else:
    st.title("🎬 ✨ Smart AI - వీడియో ఎడిటింగ్ అసిస్టెంట్")
    st.write("యూట్యూబ్ (YouTube), ఇన్‌స్టాగ్రామ్ రీల్స్ కోసం వీడియోలు ఎలా చేయాలో ఈ AI మీకు స్క్రిప్ట్ మరియు ఎడిటింగ్ ఐడియాలు ఇస్తుంది!")
    
    video_topic = st.text_input("మీరు ఏ టాపిక్ పై వీడియో చేయాలనుకుంటున్నారు? (ఉదాహరణకు: వంటలు, టెక్నాలజీ, ట్రావెల్):")
    video_type = st.selectbox("వీడియో రకం ఎంచుకోండి:", ["YouTube Long Video", "Instagram Reel / YouTube Short"])
    
    if st.button("🚀 వీడియో స్క్రిప్ట్ & ఎడిటింగ్ ప్లాన్ తయారుచేయి"):
        if video_topic:
            with st.spinner("మీ కోసం వీడియో ప్లాన్ రెడీ చేస్తున్నాను..."):
                try:
                    video_prompt = f"""
                    Provide a complete response strictly in {language}.
                    Create a full video production plan for a {video_type} on the topic: '{video_topic}'.
                    Include:
                    1. A catchy title.
                    2. A step-by-step video script (Intro, Main Body, Outro).
                    3. Specific Video Editing tips (where to add text, effects, cuts, and background music).
                    """
                    response = model.generate_content(video_prompt)
                    st.success("✨ మీ వీడియో ప్లాన్ రెడీ అయింది!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"సమస్య వచ్చింది: {e}")
        else:
            st.warning("దయచేసి పైన ఒక టాపిక్ టైప్ చేయండి!")
