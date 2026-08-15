import streamlit as st
import google.generativeai as genai
import os

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# 2. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు! Secrets లో GEMINI_API_KEY ఉందో లేదో సరిచూసుకోండి.")
    st.stop()

# Configure API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. INPUT & RESPONSE
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            response = model.generate_content(prompt)
            reply = response.text
            
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
