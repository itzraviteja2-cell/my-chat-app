import streamlit as st
from google import genai
from google.genai import types

# Streamlit Secrets నుండి API Key ని పొందడం
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయలేదు!")
    st.stop()

# ఎర్రర్ రాకుండా ఐకాన్ స్టైలింగ్ కోడ్
st.markdown("""
    <style>
    .stTextInput div[data-baseweb="input"] {
        border: 2px solid #1E88E5 !important;
        border-radius: 8px !important;
    }
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #1565C0 !important;
        box-shadow: 0 0 2px #1565C0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# సైడ్‌బార్ సెట్టింగ్‌లు
with st.sidebar:
    st.title("⚙️ సెట్టింగ్స్ / Features")
    
    app_mode = st.radio(
        "మీరు ఏమి చేయాలనుకుంటున్నారు?:",
        ["💬 AI చాటింగ్ (Chat)", "🎬 వీడియో ఎడిటింగ్ అసిస్టెంట్ (Video Assistant)"]
    )
    
    st.write("---")
    
    language = st.selectbox(
        "సంభాషణ చేయాల్సిన భాష (Language):",
        ["Telugu (తెలుగు)", "English", "Hindi (हिंदी)"]
    )
    
    st.write("---")
    st.write("### 🤖 యాప్ వివరాలు:")
    st.info("ఈ **Smart AI** అసిస్టెంట్‌ని మీ అవసరాల కోసం రూపొందించాము.")
    
    if st.button("🧹 చాట్ క్లియర్ చేయండి (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

# మోడ్ 1: AI చాటింగ్
if app_mode == "💬 AI చాటింగ్ (Chat)":
    st.title("✨ Smart AI")
    st.subheader("మీ స్మార్ట్ ఆలోచనలకు... సరైన AI తోడు!")
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
                    
                    # సరిచేయబడిన సరియైన మోడల్ నేమ్
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt,
                    )
                    
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    # ఒకవేళ ఎర్రర్ వస్తే అసలు సమస్య ఏంటో స్క్రీన్ పైన చూపిస్తుంది
                    st.error(f"Error details: {e}")

# మోడ్ 2: వీడియో ఎడిటింగ్ అసిస్టెంట్
else:
    st.title("🎬 Smart AI - వీడియో ఎడిటింగ్ అసిస్టెంట్")
    st.write("వీడియో ఎడిటింగ్ కి సంబంధించిన సందేహాలను ఇక్కడ అడగవచ్చు.")
