import streamlit as st
import google.generativeai as genai

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("చాలా முக்கியం: Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయలేదు!")
    st.stop()

st.title("🤖 smart AI")
st.write("మీకు కావలసిన ప్రశ్నను కింద అడగండి:")

# సరికొత్త మోడల్‌గా మార్చబడింది
model = genai.GenerativeModel('gemini-2.5-flash')

user_input = st.text_input("మీ ప్రశ్న ఇక్కడ టైప్ చేయండి:", key="user_question")

if user_input:
    with st.spinner("సమాధానం కోసం వెతుకుతున్నాను..."):
        try:
            response = model.generate_content(user_input)
            st.write("### సమాధానం:")
            st.write(response.text)
        except Exception as e:
            st.error(f"ఓ చిన్న సమస్య వచ్చింది: {e}")
