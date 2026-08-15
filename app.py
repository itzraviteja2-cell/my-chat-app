import streamlit as st
from google import genai
import os

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# 2. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు!")
    st.stop()

client = genai.Client(api_key=api_key)

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
            # కొత్త Interactions API పద్ధతి
            # మోడల్ పేరును మనం ఖచ్చితంగా ఇవ్వాల్సిన అవసరం లేదు, 
            # డిఫాల్ట్‌గా ఇది ఉత్తమమైన మోడల్‌ను తీసుకుంటుంది.
            response = client.interactions.create(
                model="gemini-2.0-flash", 
                input=prompt
            )
            
            # రిజల్ట్ పొందడం
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
