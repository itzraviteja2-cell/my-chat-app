import streamlit as st
from google import genai
import os
import tempfile


# =========================================================
# 1. PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide"
)


# =========================================================
# 2. AURORA AI HEADER
# =========================================================

st.markdown("""
<div style="
    display:flex;
    align-items:center;
    gap:15px;
    margin-bottom:25px;
">

    <div style="
        width:55px;
        height:55px;
        border-radius:50%;
        background:linear-gradient(135deg,#ff00aa,#6a00ff);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:30px;
        box-shadow:0 0 20px rgba(120,0,255,0.4);
    ">
        ⭐
    </div>

    <h1 style="
        margin:0;
        font-size:42px;
        background:linear-gradient(45deg,#7928CA,#FF0080);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    ">
        Aurora AI
    </h1>

</div>
""", unsafe_allow_html=True)


# =========================================================
# 3. GEMINI API
# =========================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY Streamlit Secrets లో పెట్టలేదు.")
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# 4. SIDEBAR TOOLS
# =========================================================

st.sidebar.header("🛠️ కంట్రోల్ ప్యానెల్")

audio_input = st.sidebar.audio_input(
    "🎙️ వాయిస్ మెసేజ్"
)

uploaded_file = st.sidebar.file_uploader(
    "📁 ఫోటో / వీడియో / ఫైల్",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp",
        "mp4",
        "mov",
        "avi",
        "pdf",
        "txt",
        "csv"
    ]
)


# =========================================================
# 5. CHAT HISTORY
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# 6. CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Aurora AI ని ఏమైనా అడగండి..."
)


# =========================================================
# 7. USER MESSAGE PROCESSING
# =========================================================

if prompt or audio_input or uploaded_file:

    if prompt:
        user_text = prompt

    elif uploaded_file:
        user_text = (
            f"ఈ ఫైల్‌ను పరిశీలించి నాకు తెలుగులో వివరించండి: "
            f"{uploaded_file.name}"
        )

    else:
        user_text = "ఈ ఆడియోను విని తెలుగులో వివరించండి."


    # -----------------------------------------------------
    # Show user message
    # -----------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_text
    })

    with st.chat_message("user"):
        st.markdown(user_text)


    # -----------------------------------------------------
    # AI response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        message_placeholder.markdown(
            "ఆలోచిస్తోంది... ⏳"
        )

        try:

            contents_list = [user_text]


            # =================================================
            # AUDIO PROCESSING
            # =================================================

            if audio_input:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                ) as tmp_audio:

                    tmp_audio.write(
                        audio_input.getvalue()
                    )

                    audio_path = tmp_audio.name


                audio_ref = client.files.upload(
                    file=audio_path
                )

                contents_list.append(audio_ref)


            # =================================================
            # FILE PROCESSING
            # =================================================

            if uploaded_file:

                file_extension = os.path.splitext(
                    uploaded_file.name
                )[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_extension
                ) as tmp_file:

                    tmp_file.write(
                        uploaded_file.getvalue()
                    )

                    file_path = tmp_file.name


                file_ref = client.files.upload(
                    file=file_path
                )

                contents_list.append(file_ref)


            # =================================================
            # GEMINI 2.5 FLASH
            # =================================================

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents_list
            )


            # =================================================
            # RESPONSE
            # =================================================

            full_response = response.text

            if not full_response:
                full_response = "క్షమించండి, ప్రస్తుతం సమాధానం రాలేదు."


            message_placeholder.markdown(
                full_response
            )


            # -------------------------------------------------
            # Save AI message
            # -------------------------------------------------

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })


        except Exception as e:

            message_placeholder.empty()

            st.error(
                f"ఎర్రర్ వచ్చింది: {e}"
            )
