import streamlit as st
import google.generativeai as genai
import os

# Page Config
st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# API Setup
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# 1. API KEY కి అందుబాటులో ఉన్న మోడల్స్ లిస్ట్ తెలుసుకోవడం
try:
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
except Exception as err:
    available_models = []

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
        
        if not available_models:
            st.error("మీ API Key కి ఎలాంటి మోడల్స్ సపోర్ట్ చేయడం లేదు. దయచేసి AI Studio లో కొత్త API Key జనరేట్ చేయండి.")
        else:
            # లిస్ట్‌లో ఉన్న మొదటి వ్యాలిడ్ మోడల్‌ను ఆటోమేటిక్‌గా వాడుతుంది
            selected_model = available_models[0]
            try:
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt)
                
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error ({selected_model}): {e}")
