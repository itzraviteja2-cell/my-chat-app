import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Aurora AI", layout="wide")
st.title("🌌 Aurora AI")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Check Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

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
            # మోడల్స్ జాబితా నుండి పని చేసే మొదటి మోడల్‌ను మాత్రమే ఆటో-సెలెక్ట్ చేస్తుంది
            valid_models = [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            if not valid_models:
                st.error("సరికొత్త API Key ని AI Studio లో జనరేట్ చేయండి.")
            else:
                chosen_model = valid_models[0]
                model = genai.GenerativeModel(chosen_model)
                response = model.generate_content(prompt)
                
                reply = response.text
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
        except Exception as e:
            st.error(f"Error: {e}")
