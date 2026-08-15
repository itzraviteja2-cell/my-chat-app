import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Aurora AI", layout="wide")

st.title("🌌 Aurora AI")

# API Key செக் చేస్తున్నాం
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key దొరకలేదు!")
    st.stop()

# Client setup
client = genai.Client(api_key=api_key)

st.write("Aurora AI సిద్ధంగా ఉంది! ఇది టెస్ట్ కోడ్.")
