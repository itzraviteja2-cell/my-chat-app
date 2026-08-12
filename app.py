import streamlit as st
import google.generativeai as genai

# Streamlit Advanced Settings (Secrets) నుండి API Key ని రీడ్ చేయడం
st_api_key = st.secrets.get("GEMINI_API_KEY")

if not st_api_key:
    st.error("చాలా ముఖ్యం: Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయలేదు!")
    st.stop()

# Gemini AI ని కాన్ఫిగర్ చేయడం
genai.configure(api_key=st_api_key)
model = genai.GenerativeModel("gemini-pro")

# యాప్ టైటిల్
st.title("🤖 నా Gemini AI చాట్‌బాట్")
st.write("మీకు కావలసిన ప్రశ్నను కింద అడగండి:")

# యూజర్ ఇన్‌పుట్ బాక్స్
user_input = st.text_input("మీ ప్రశ్న ఇక్కడ టైప్ చేయండి:", key="user_question")

if user_input:
    with st.spinner("సమాధానం వెతుకుతున్నాను..."):
        try:
            response = model.generate_content(user_input)
            st.success("🤖 సమాధానం:")
            st.write(response.text)
        except Exception as e:
            st.error(f"ఏదో పొరపాటు జరిగింది: {e}")
