import streamlit as st
from google import genai
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Aurora AI", page_icon="🤖", layout="wide")

# 2. API Setup (New Google GenAI SDK)
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 API Key దొరకలేదు! Streamlit Secrets లో చూడండి.")
    st.stop()

client = genai.Client(api_key=api_key)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. SIDEBAR (అకౌంట్, సెట్టింగ్స్ & భాషల ఎంపిక)
with st.sidebar:
    st.title("👤 Account & Settings")
    
    # అకౌంట్ ప్రొఫైల్ వివరాలు
    st.info("Logged in as: **itzraviteja2-cell**")
    
    st.write("---")
    
    # 🌐 Language Selector
    lang = st.selectbox(
        "🌐 Choose Language / భాషను ఎంచుకోండి:",
        ["Telugu (తెలుగు)", "English", "Hindi (हिंदी)"]
    )
    
    st.write("---")
    
    if lang == "Telugu (తెలుగు)":
        clear_btn = "🗑️ చాట్ రద్దు చేయి"
        upload_label = "🖼️ ఫోటో అప్‌లోడ్"
        mic_label = "🎙️ వాయిస్ ఇన్‌పుట్ (మైక్)"
        input_placeholder = "మీ సందేశాన్ని టైప్ చేయండి..."
        system_prompt = "సమాధానాలు స్పష్టమైన తెలుగులో ఇవ్వండి."
    elif lang == "Hindi (हिंदी)":
        clear_btn = "🗑️ चैट साफ करें"
        upload_label = "🖼️ फोटो अपलोड करें"
        mic_label = "🎙️ वॉइस इनपुट (माइक)"
        input_placeholder = "अपना संदेश टाइप करें..."
        system_prompt = "सभी उत्तर स्पष्ट हिंदी में दें।"
    else:  # English
        clear_btn = "🗑️ Clear Chat"
        upload_label = "🖼️ Upload Image"
        mic_label = "🎙️ Voice Input (Mic)"
        input_placeholder = "Type your message here..."
        system_prompt = "Respond clearly in English."

    if st.button(clear_btn):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    uploaded_file = st.file_uploader(upload_label, type=["png", "jpg", "jpeg"])
    
    st.write("---")
    st.write(mic_label)
    audio_value = st.audio_input("Record")

# 4. MAIN TITLE
st.title("✨ Aurora AI")
st.caption("Multi-Language AI Assistant (తెలుగు | English | हिंदी)")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. Image Processing
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=300)
    if st.button("🔍 Analyze Image"):
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    prompt_img = f"{system_prompt} Explain what is in this image."
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=[prompt_img, image]
                    )
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# 6. Text Input Processing
if prompt := st.chat_input(input_placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                full_prompt = f"Instruction: {system_prompt}\nUser Query: {prompt}"
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=full_prompt
                )
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
