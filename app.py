import streamlit as st
from google import genai
import os

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# 2. API SETUP
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు! Streamlit Secrets సరిచూసుకోండి.")
    st.stop()

# Client Init
client = genai.Client(api_key=api_key)

# 3. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. INPUT & RESPONSE HANDLING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            # మోడల్ పేరును కచ్చితమైన వర్షన్‌తో `models/` ప్రిఫిక్స్‌తో పిలవడం
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            # మొదటి మోడల్ ఫెయిల్ అయితే ప్రత్యామ్నాయ మోడల్ (Fallback) ని ట్రై చేయడం
            try:
                response = client.models.generate_content(
                    model="models/gemini-1.5-pro-002",
                    contents=prompt
                )
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as ex:
                st.error(f"ఎర్రర్ వచ్చింది: {ex}")
