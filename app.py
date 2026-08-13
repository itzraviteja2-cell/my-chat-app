import streamlit as st
import google.generativeai as genai

# Streamlit Secrets నుండి API Key ని పొందడం
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # ఎల్లప్పుడూ లేటెస్ట్ వర్కింగ్ మోడల్‌కి కనెక్ట్ అవుతుంది
    model = genai.GenerativeModel('gemini-flash-latest')
except Exception as e:
    st.error(f"API Key సెటప్ లోపం: {e}")
    st.stop()

# UI Styling
st.markdown("""
    <style>
    .stTextInput div[data-baseweb="input"] {
        border: 2px solid #1E88E5 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# సైడ్‌బార్ సెట్టింగ్‌లు
with st.sidebar:
    st.title("⚙️ సెట్టింగ్స్")
    app_mode = st.radio("ఎంచుకోండి:", ["💬 AI చాటింగ్ (Chat)", "🎬 వీడియో ఎడిటింగ్ అసిస్టెంట్"])
    st.write("---")
    language = st.selectbox("భాష:", ["Telugu (తెలుగు)", "English", "Hindi (हिंदी)"])
    
    if st.button("🧹 చాట్ క్లియర్ చేయండి"):
        st.session_state.messages = []
        st.rerun()

# AI చాటింగ్ విభాగం
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
                    response = model.generate_content(prompt)
                    
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error details: {e}")
else:
    st.title("🎬 Smart AI - వీడియో ఎడిటింగ్ అసిస్టెంట్")
    st.write("వీడియో ఎడిటింగ్ కి సంబంధించిన సందేహాలను ఇక్కడ అడగవచ్చు.")
