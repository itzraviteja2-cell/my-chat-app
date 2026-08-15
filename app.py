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

client = genai.Client(api_key=api_key)

# 4. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages only
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. INPUT & AUTO-MODEL SELECTION HANDLING
prompt = st.chat_input("Aurora AI ని ఏదైనా అడగండి...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            # 1. ఖాతాలో అందుబాటులో ఉన్న మోడల్స్ జాబితాను ఆటోమేటిక్‌గా ఫెచ్ చేయడం
            working_model = None
            for m in client.models.list():
                # generate_content సపోర్ట్ చేసే మోడల్‌ను ఎంచుకోవడం
                if hasattr(m, 'supported_actions') and 'generateContent' in m.supported_actions:
                    working_model = m.name
                    break
                elif hasattr(m, 'name'):
                    working_model = m.name
                    break

            # మోడల్ పేరు దొరక్కపోతే డిఫాల్ట్‌గా gemini-2.0-flash వాడటం
            if not working_model:
                working_model = "gemini-2.0-flash"

            # 2. రెస్పాన్స్ జనరేట్ చేయడం
            response = client.models.generate_content(
                model=working_model,
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"⚠️ ఎర్రర్ వచ్చింది: {e}")
