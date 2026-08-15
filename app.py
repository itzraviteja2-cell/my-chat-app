import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Aurora AI", layout="wide")

# Logo & Title
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.title("🌌")
with col2:
    st.title("Aurora AI")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask Aurora AI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... ⏳")
        
        try:
            # 1. Available active models list
            active_models = []
            for m in client.models.list():
                if "generateContent" in m.supported_actions:
                    active_models.append(m.name)
            
            # 2. Pick the first available working model automatically
            if active_models:
                target_model = active_models[0]
            else:
                target_model = "gemini-1.5-flash"
                
            response = client.models.generate_content(
                model=target_model,
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error: {e}")
