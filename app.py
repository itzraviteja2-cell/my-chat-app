import streamlit as st
from google import genai
import os
import tempfile


# ============================================================
# 1. PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Aurora AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 2. STREAMLIT UI CLEANUP
# ============================================================

st.markdown(
    """
    <style>

    /* Hide Streamlit top header */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Hide decoration */
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* Page spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* Aurora title */
    .aurora-title {
        font-size: 42px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(
            90deg,
            #5427ff,
            #8b5cf6,
            #00a6d6
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .aurora-subtitle {
        color: #777777;
        font-size: 14px;
        margin-top: -5px;
        margin-bottom: 25px;
    }

    /* Logo */
    .aurora-logo {
        width: 60px;
        height: 60px;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #5427ff,
            #8b5cf6,
            #06b6d4
        );
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        box-shadow: 0 7px 25px rgba(84, 39, 255, 0.30);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. AURORA AI HEADER
# ============================================================

st.markdown(
    """
    <div style="
        display:flex;
        align-items:center;
        gap:14px;
        margin-bottom:25px;
    ">

        <div class="aurora-logo">
            🌌
        </div>

        <div>
            <div class="aurora-title">
                Aurora AI
            </div>

            <div class="aurora-subtitle">
                Your intelligent AI assistant
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. GEMINI API
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY కనబడలేదు. "
        "Streamlit Secrets లో GEMINI_API_KEY ఉందో చూడండి."
    )
    st.stop()


client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# 5. CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🌌 Aurora AI")

    st.markdown("---")

    st.markdown(
        """
        ### Features

        💬 AI Chat

        📎 File Upload

        🎤 Voice Input

        🖼️ Image Understanding

        🎬 Video Understanding

        📄 PDF / Text

        🧠 Gemini 2.5 Flash
        """
    )

    st.markdown("---")

    if st.button(
        "🗑️ చాట్ క్లియర్ చేయండి",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# 7. SHOW OLD CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# 8. CHAT INPUT
# ============================================================

chat_data = st.chat_input(
    "Aurora AI ని ఏమైనా అడగండి...",
    accept_file=True,
    accept_audio=True,
    file_type=[
        "png",
        "jpg",
        "jpeg",
        "webp",
        "heic",
        "heif",
        "mp4",
        "mov",
        "avi",
        "mp3",
        "wav",
        "m4a",
        "flac",
        "pdf",
        "txt",
        "csv"
    ],
    max_upload_size=200,
    audio_sample_rate=16000
)


# ============================================================
# 9. WHEN USER SENDS MESSAGE
# ============================================================

if chat_data:

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    user_text = chat_data.text or ""


    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    uploaded_files = chat_data.files or []


    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    audio_input = chat_data.audio


    # --------------------------------------------------------
    # NOTHING?
    # --------------------------------------------------------

    if (
        not user_text.strip()
        and not uploaded_files
        and audio_input is None
    ):
        st.stop()


    # ========================================================
    # USER DISPLAY MESSAGE
    # ========================================================

    display_text = user_text.strip()


    if uploaded_files:

        names = ", ".join(
            file.name for file in uploaded_files
        )

        if display_text:

            display_text += (
                f"\n\n📎 Files: {names}"
            )

        else:

            display_text = (
                f"📎 Files: {names}"
            )


    if audio_input is not None:

        if display_text:

            display_text += "\n\n🎤 Voice message"

        else:

            display_text = "🎤 Voice message"


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": display_text
        }
    )


    # ========================================================
    # SHOW USER MESSAGE
    # ========================================================

    with st.chat_message("user"):

        st.markdown(display_text)

        for file in uploaded_files:

            mime_type = file.type or ""

            if mime_type.startswith("image/"):

                st.image(
                    file,
                    caption=file.name,
                    use_container_width=True
                )


    # ========================================================
    # AI MESSAGE
    # ========================================================

    with st.chat_message("assistant"):

        placeholder = st.empty()

        placeholder.markdown(
            "⏳ **Aurora AI ఆలోచిస్తోంది...**"
        )


        temporary_files = []


        try:

            # =================================================
            # GEMINI CONTENTS
            # =================================================

            contents = []


            # -------------------------------------------------
            # TEXT
            # -------------------------------------------------

            if user_text.strip():

                contents.append(
                    user_text.strip()
                )

            else:

                contents.append(
                    "ఈ ఫైల్ లేదా ఆడియోను పరిశీలించి "
                    "వినియోగదారుడికి తెలుగులో సమాధానం ఇవ్వండి."
                )


            # =================================================
            # FILE UPLOAD
            # =================================================

            for uploaded_file in uploaded_files:

                file_name = uploaded_file.name or "file"

                _, extension = os.path.splitext(
                    file_name
                )

                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=extension
                )

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_file.close()

                temporary_files.append(
                    temp_file.name
                )


                # Upload to Gemini
                gemini_file = client.files.upload(
                    file=temp_file.name
                )

                contents.append(
                    gemini_file
                )


            # =================================================
            # AUDIO UPLOAD
            # =================================================

            if audio_input is not None:

                temp_audio = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                )

                temp_audio.write(
                    audio_input.getvalue()
                )

                temp_audio.close()

                temporary_files.append(
                    temp_audio.name
                )


                audio_file = client.files.upload(
                    file=temp_audio.name
                )

                contents.append(
                    audio_file
                )


            # =================================================
            # GEMINI 2.5 FLASH
            # =================================================

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )


            # =================================================
            # RESPONSE
            # =================================================

            reply = response.text


            if not reply:

                reply = (
                    "క్షమించండి. ప్రస్తుతం సమాధానం "
                    "రాలేదు. మళ్లీ ప్రయత్నించండి."
                )


            # =================================================
            # SHOW AI RESPONSE
            # =================================================

            placeholder.markdown(reply)


            # =================================================
            # SAVE AI RESPONSE
            # =================================================

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )


        except Exception as e:

            placeholder.empty()

            st.error(
                "⚠️ Aurora AI లో సమస్య వచ్చింది."
            )

            # Actual error for debugging
            st.code(
                str(e)
            )


        finally:

            # =================================================
            # DELETE TEMP FILES
            # =================================================

            for path in temporary_files:

                try:

                    os.remove(path)

                except Exception:

                    pass
