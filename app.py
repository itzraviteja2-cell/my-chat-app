import streamlit as st
from google import genai
from google.genai import types
import os
import tempfile

# 1. పేజీ సెట్టింగ్స్ మరియు ఐకాన్ (Page Config)
st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide"
)

# 2. అరోరా AI స్టైలిష్ SVG లోగో & హెడర్
logo_svg = """
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
    <svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="auroraGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#7928CA;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#FF0080;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#00DFD8;stop-opacity:1" />
            </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="45" fill="url(#auroraGrad)" />
        <path d="M50 18 L58 40 L82 42 L63 57 L70 80 L50 66 L30 80 L37 57 L18 42 L42 40 Z" fill="#FFFFFF" />
    </svg>
    <span style="font-size: 36px; font-weight: 800; background: linear-gradient(45deg, #7928CA, #FF0080, #00DFD8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Aurora AI
    </span>
</div>
"""
st.markdown(logo_svg, unsafe_allow_html=True)
st.caption("మీ వ్యక్తిగత AI & వీడియో / ఇమేజ్ అసిస్టెంట్")

# 3. Gemini API క్లయింట్ సెటప్
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("దయచేసి మీ Streamlit Secrets లో GEMINI_API_KEY ని సెట్ చేయండి.")
    st.stop()

client = genai.Client(api_key=api_key)

# 4. సైడ్‌బార్ - వీడియో / ఫోటో అప్‌లోడ్ ఫీచర్
st.sidebar.header("🎬 వీడియో & మీడియా ఎడిటర్ / అనలైజర్")
uploaded_file = st.sidebar.file_uploader(
    "వీడియో లేదా ఇమేజ్ ఫైల్ అప్‌లోడ్ చేయండి", 
    type=["mp4", "mov", "avi", "png", "jpg", "jpeg"]
)

uploaded_file_ref = None

if uploaded_file is not None:
    # సైడ్‌బార్‌లో ప్రీవ్యూ చూపించడం
    if uploaded_file.type.startswith("video"):
        st.sidebar.video(uploaded_file)
    elif uploaded_file.type.startswith("image"):
        st.sidebar.image(uploaded_file)
    
    st.sidebar.info("ఫైల్ సిద్ధంగా ఉంది. కింద చాట్‌లో ఫైల్ గురించి ఏదైనా అడగండి!")

# 5. చాట్ హిస్టరీ సేవ్ చేయడం (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. పాత మెసేజ్ లను స్క్రీన్ పై చూపించడం
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. యూజర్ నుండి ఇన్‌పుట్ తీసుకోవడం & AI రెస్పాన్స్
if prompt := st.chat_input("Aurora AI ని ప్రతీది అడగండి లేదా వీడియో గురించి విశ్లేషించమనండి..."):
    # యూజర్ మెసేజ్ ని చూపించడం
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI నుండి సమాధానం పొందడం
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("ఆలోచిస్తోంది... ⏳")
        
        try:
            contents_list = [prompt]
            
            # ఒకవేళ ఫైల్ అప్‌లోడ్ చేసి ఉంటే, దాన్ని గూగుల్ API కి పంపడానికి సిద్ధం చేయడం
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Gemini Files API ద్వారా ఫైల్ అప్‌లోడ్ చేయడం
                uploaded_file_ref = client.files.upload(file=tmp_file_path)
                contents_list.append(uploaded_file_ref)

            # Gemini-2.5-flash మోడల్ ని ఉపయోగించి రెస్పాన్స్ తెప్పించడం
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents_list,
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # AI మెసేజ్ ని హిస్టరీలో సేవ్ చేయడం
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # తాత్కాలిక ఫైల్ డిలీట్ చేయడం
            if uploaded_file_ref and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

        except Exception as e:
            st.error(f"ఎర్రర్ వచ్చింది: {e}")
