import streamlit as st
from google import genai

# Streamlit Secrets నుండి API Key పొందడం
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయలేదు!")
    st.stop()

# ఐకాన్ స్టైలింగ్
st.markdown("""
    <style>
    .stTextInput div[data-baseweb="input"] {
        border: 2px solid #1E88E5 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# సైడ్‌బార్
with st.sidebar:
    st.title("⚙️ సెట్టింగ్స్")
    app_mode = st.radio("ఎంచుకోండి:", ["💬 AI చాటింగ్ (Chat)", "🎬 వీడియో ఎడిటింగ్ అసిస్టెంట్"])
    st.write("---")
    language = st.selectbox("భాష:", ["Telugu (తెలుగు)", "English", "Hindi (हिंदी)"])
    if st.button("🧹 చాట్ క్లియర్ చేయండి"):
        st.session_state.messages = []
        st.rerun()

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
                    
                    # SDK v2 కోసం మోడల్ ఫార్మాట్
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',  # లేదా 'gemini-1.5-flash-002'
                        contents=prompt,
                    )
                    
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Error details: {e}")
