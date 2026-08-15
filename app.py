import streamlit as st
from google import genai
import os
import tempfile
import base64


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
# 2. HIDE STREAMLIT TOP BAR
# ============================================================

st.markdown(
    """
    <style>

    /* Hide Streamlit top header */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Hide top decoration */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Remove extra top space */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* Main background */
    .stApp {
        background: #ffffff;
    }

    /* Aurora logo */
    .aurora-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 25px;
        padding: 5px 0;
    }

    .aurora-logo {
        width: 58px;
        height: 58px;
        min-width: 58px;
        border-radius: 16px;
        background:
            radial-gradient(circle at 25% 25%, #ffffff 0%, transparent 18%),
            linear-gradient(135deg, #5427ff, #8b5cf6, #06b6d4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 31px;
        box-shadow: 0 8px 25px rgba(83, 39, 255, 0.30);
    }

    .aurora-title {
        font-size: 42px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #5527ff, #8b5cf6, #00a6d6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .aurora-subtitle {
        font-size: 14px;
        color: #777777;
        margin-top: -4px;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
    }

    [data-testid="stChatInput"] textarea {
        border-radius: 18px !important;
        font-size: 16px !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 18px;
        margin-bottom: 10px;
    }

    /* Hide sidebar when not needed */
    section[data-testid="stSidebar"] {
        background: #fafafa;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. AURORA AI HEADER / LOGO
# ============================================================

st.markdown(
    """
    <div class="aurora-header">

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
        "Streamlit Secrets లో GEMINI_API_KEY పెట్టండి."
    )
    st.stop()


client = genai.Client(api_key=api_key)

# Stable Gemini model
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
        **Features**

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
        "🗑️ చాట్ మొత్తం క్లియర్ చేయండి",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# 7. DISPLAY OLD CHAT
# ============================================================

for message in st.session_state.messages:

    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        st.markdown(content)


# ============================================================
# 8. FILE TYPE SETTINGS
# ============================================================

allowed_file_types = [
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
]


# ============================================================
# 9. CHAT INPUT
# ============================================================

prompt_data = st.chat_input(
    "Aurora AI ని ఏమైనా అడగండి...",
    accept_file=True,
    accept_audio=True,
    file_type=allowed_file_types,
    max_upload_size=200,
    audio_sample_rate=16000
)


# ============================================================
# 10. PROCESS USER MESSAGE
# ============================================================

if prompt_data:

    # --------------------------------------------------------
    # Get text
    # --------------------------------------------------------

    user_text = prompt_data.get("text", "")

    if user_text is None:
        user_text = ""

    user_text = user_text.strip()


    # --------------------------------------------------------
    # Get uploaded files
    # --------------------------------------------------------

    uploaded_files = prompt_data.get("files", [])

    if uploaded_files is None:
        uploaded_files = []


    # --------------------------------------------------------
    # Get microphone audio
    # --------------------------------------------------------

    audio_input = prompt_data.get("audio", None)


    # --------------------------------------------------------
    # Check if anything was submitted
    # --------------------------------------------------------

    if (
        not user_text
        and not uploaded_files
        and not audio_input
    ):
        st.stop()


    # ========================================================
    # USER DISPLAY MESSAGE
    # ========================================================

    display_text = user_text

    if uploaded_files:

        file_names = ", ".join(
            file.name for file in uploaded_files
        )

        if display_text:
            display_text += f"\n\n📎 **Files:** {file_names}"
        else:
            display_text = f"📎 **Files:** {file_names}"


    if audio_input:

        if display_text:
            display_text += "\n\n🎤 **Voice message**"
        else:
            display_text = "🎤 **Voice message**"


    # ========================================================
    # SHOW USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": display_text
        }
    )


    with st.chat_message("user"):

        st.markdown(display_text)

        # Show uploaded images
        for file in uploaded_files:

            mime = file.type or ""

            if mime.startswith("image/"):
                st.image(
                    file,
                    caption=file.name,
                    use_container_width=True
                )


    # ========================================================
    # AI RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        message_placeholder.markdown(
            "⏳ **Aurora AI ఆలోచిస్తోంది...**"
        )


        try:

            # ------------------------------------------------
            # Gemini contents
            # ------------------------------------------------

            contents = []


            # ------------------------------------------------
            # User text
            # ------------------------------------------------

            if user_text:

                contents.append(user_text)

            else:

                contents.append(
                    "ఈ ఫైల్/ఆడియోను పరిశీలించి, "
                    "వినియోగదారుడికి తెలుగులో సహాయం చేయండి."
                )


            # =================================================
            # UPLOAD FILES TO GEMINI
            # =================================================

            temporary_files = []


            for uploaded_file in uploaded_files:

                suffix = ""

                if uploaded_file.name:
                    _, ext = os.path.splitext(
                        uploaded_file.name
                    )

                    suffix = ext


                # Create temporary file
                temp = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                )

                temp.write(
                    uploaded_file.getvalue()
                )

                temp.close()

                temporary_files.append(temp.name)


                # Upload to Gemini
                gemini_file = client.files.upload(
                    file=temp.name
                )

                contents.append(gemini_file)


            # =================================================
            # MICROPHONE AUDIO
            # =================================================

            if audio_input:

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

                contents.append(audio_file)


            # =================================================
            # GEMINI 2.5 FLASH
            # =================================================

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )


            # =================================================
            # RESPONSE TEXT
            # =================================================

            reply = response.text

            if not reply:

                reply = (
                    "క్షమించండి, ప్రస్తుతం సమాధానం "
                    "రాలేదు. మళ్లీ ప్రయత్నించండి."
                )


            # =================================================
            # SHOW RESPONSE
            # =================================================

            message_placeholder.markdown(reply)


            # =================================================
            # SAVE RESPONSE
            # =================================================

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )


            # =================================================
            # DELETE TEMPORARY FILES
            # =================================================

            for temp_path in temporary_files:

                try:
                    os.remove(temp_path)

                except Exception:
                    pass


        except Exception as e:

            message_placeholder.empty()

            st.error(
                "⚠️ Aurora AI లో సమస్య వచ్చింది."
            )

            st.code(
                str(e)
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content":
                    "⚠️ ప్రస్తుతం AIకి కనెక్ట్ అవ్వడంలో సమస్య వచ్చింది."
                }
            )
