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
            # 1. తదుపరి తరం మోడల్స్ వరుస క్రమం
            models_to_try = [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-1.5-flash-latest"
            ]
            
            response_text = None
            last_error = None

            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=prompt
                    )
                    response_text = response.text
                    break
                except Exception as err:
                    last_error = err
                    continue

            if response_text:
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error(f"Error: {last_error}")
            
        except Exception as e:
            st.error(f"Error: {e}")
