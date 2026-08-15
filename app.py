import streamlit as st
from google import genai
import os

# 1. PAGE SETTINGS
st.set_page_config(page_title="Aurora AI", layout="wide")

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

# New Gemini SDK Client initialization
client = genai.Client(api_key=api_key)

# 4. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display welcome message if chat is empty
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("✨ **నమస్కారం! నేను Aurora AI** ✨\n\nమీకు ఎలా సహాయం చేయాలి?")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. INPUT & INTERACTIONS API HANDLING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        try:
            # Interactions API pattern with latest model
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            # Fallback if primary model fails
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash-latest",
                    contents=prompt
                )
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as ex:
                st.error(f"⚠️ Aurora AI లో సమస్య వచ్చింది: {ex}")
