import streamlit as st
import google.generativeai as genai
import os

# Page Config
st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# Retrieve API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

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
            # 1. API కీ కి అందుబాటులో ఉన్న ప్రతీ మోడల్‌ను ఆటోమేటిక్‌గా చెక్ చేస్తుంది
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if not available_models:
                st.error("మీ API Key కి ఏ మోడల్ అందుబాటులో లేదు. దయచేసి AI Studio లో కొత్త Key తీసుకోండి.")
            else:
                # 2. అందుబాటులో ఉన్న మొదటి మోడల్‌తో రన్ చేస్తుంది
                selected_model = available_models[0]
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt)
                
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
        except Exception as e:
            st.error(f"Error: {e}")
