import streamlit as st
from google import genai
import os

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide", initial_sidebar_state="expanded")

# 2. HIDE STREAMLIT MENU & FOOTER
hide_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌌 Aurora AI")

# 3. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు! Streamlit Secrets సరిచూసుకోండి.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. SIDEBAR
st.sidebar.title("🛠️ టూల్స్")

if st.sidebar.button("➕ కొత్త చాట్", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# 5. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT & RESPONSE HANDLING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            # కొత్త API సపోర్ట్ చేసే వర్టికల్ ఆటో-సెలెక్షన్
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
