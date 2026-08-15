import streamlit as st
from google import genai
import os

# Page Configuration
st.set_page_config(page_title="Aurora AI", layout="wide")

# Hide Streamlit UI elements
hide_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

st.title("🌌 Aurora AI")

# Retrieve API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
prompt = st.chat_input("Ask Aurora AI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking... ⏳")
        
        try:
            # 1. Fetch all models available for your exact API Key
            available_models = list(client.models.list())
            
            # 2. Filter model names that support generation
            target_model = None
            for m in available_models:
                m_name = m.name.replace("models/", "") if hasattr(m, 'name') else str(m)
                if "flash" in m_name or "pro" in m_name:
                    target_model = m_name
                    break
            
            if not target_model and len(available_models) > 0:
                target_model = available_models[0].name.replace("models/", "")

            # 3. Generate response with auto-detected model
            response = client.models.generate_content(
                model=target_model,
                contents=prompt
            )
            
            reply = response.text
            message_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error: {e}")
