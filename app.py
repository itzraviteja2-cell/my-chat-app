import os
import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# AURORA AI
# Complete Streamlit AI Chat App
# ============================================================

st.set_page_config(
    page_title="Aurora AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
        height: 0;
    }

    /* Main page */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 6rem;
        max-width: 1100px;
    }

    /* Aurora Header */
    .aurora-header {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 12px 8px 22px 8px;
        margin-bottom: 10px;
    }

    .aurora-logo {
        width: 72px;
        height: 72px;
        border-radius: 20px;
        background:
            linear-gradient(
                135deg,
                #1b1b4b,
                #4627a8,
                #168aad,
                #55e6c1
            );
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        box-shadow: 0 8px 25px rgba(70,39,168,0.30);
    }

    .aurora-title {
        font-size: 42px;
        font-weight: 800;
        line-height: 1;
        background:
            linear-gradient(
                90deg,
                #6a00ff,
                #008cff,
                #00c9a7
            );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .aurora-subtitle {
        margin-top: 7px;
        font-size: 16px;
        color: #777;
    }

    /* Mobile */
    @media (max-width: 600px) {

        .block-container {
            padding-top: 0.8rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .aurora-header {
            gap: 12px;
        }

        .aurora-logo {
            width: 58px;
            height: 58px;
            border-radius: 16px;
            font-size: 31px;
        }

        .aurora-title {
            font-size: 32px;
        }

        .aurora-subtitle {
            font-size: 13px;
        }
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 22px;
    }

    /* Send button */
    [data-testid="stChatInputSubmitButton"] {
        border-radius: 50%;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AURORA AI HEADER
# ============================================================

st.markdown(
    """
    <div class="aurora-header">

        <div class="aurora-logo">
            ✨
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
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI API
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY కనిపించలేదు. "
        "Streamlit App Settings → Secrets లో API key పెట్టండి."
    )
    st.stop()


client = genai.Client(api_key=api_key)

# Stable Gemini model
MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "నమస్కారం! నేను Aurora AI ✨\n\nమీకు ఎలా సహాయం చేయాలి?"
        }
    ]


# ============================================================
# SHOW CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message["role"]

    if role == "user":
        avatar = "👤"
    else:
        avatar = "✨"

    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# + FILE
# 🎤 AUDIO
# ============================================================

prompt = st.chat_input(
    "Aurora AI ని ఏమైనా అడగండి...",
    accept_file=True,
    accept_audio=True,
    file_type=[
        "png",
        "jpg",
        "jpeg",
        "webp",
        "pdf",
        "txt",
        "csv",
        "mp4",
        "mov",
        "avi",
        "wav",
        "mp3",
        "aac",
        "ogg",
        "flac"
    ],
)


# ============================================================
# PROCESS USER INPUT
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    user_text = prompt.text if hasattr(prompt, "text") else ""

    if not user_text:
        user_text = ""

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    files = []

    if hasattr(prompt, "files"):
        files = prompt.files

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    audio = None

    if hasattr(prompt, "audio"):
        audio = prompt.audio


    # --------------------------------------------------------
    # Check whether something was submitted
    # --------------------------------------------------------

    if not user_text and not files and not audio:
        st.warning("ఏదైనా message, file లేదా audio పంపండి.")
        st.stop()


    # ========================================================
    # USER MESSAGE DISPLAY
    # ========================================================

    display_message = user_text

    if files:

        file_names = []

        for file in files:
            file_names.append(file.name)

        if display_message:
            display_message += "\n\n📎 Files: " + ", ".join(file_names)
        else:
            display_message = "📎 Files: " + ", ".join(file_names)


    if audio:

        if display_message:
            display_message += "\n\n🎤 Audio message"
        else:
            display_message = "🎤 Audio message"


    st.session_state.messages.append(
        {
            "role": "user",
            "content": display_message
        }
    )


    with st.chat_message("user", avatar="👤"):
        st.markdown(display_message)


    # ========================================================
    # AI RESPONSE
    # ========================================================

    with st.chat_message("assistant", avatar="✨"):

        placeholder = st.empty()

        placeholder.markdown("ఆలోచిస్తోంది... ⏳")

        try:

            # ------------------------------------------------
            # Build conversation
            # ------------------------------------------------

            contents = []

            for old_message in st.session_state.messages[:-1]:

                old_role = old_message["role"]

                old_text = old_message["content"]

                if old_role == "user":

                    contents.append(
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(
                                    text=old_text
                                )
                            ],
                        )
                    )

                elif old_role == "assistant":

                    contents.append(
                        types.Content(
                            role="model",
                            parts=[
                                types.Part.from_text(
                                    text=old_text
                                )
                            ],
                        )
                    )


            # ------------------------------------------------
            # Current user text
            # ------------------------------------------------

            current_parts = []


            if user_text:

                current_parts.append(
                    types.Part.from_text(
                        text=user_text
                    )
                )


            # ------------------------------------------------
            # Files
            # ------------------------------------------------

            for uploaded_file in files:

                file_bytes = uploaded_file.getvalue()

                mime_type = uploaded_file.type

                if not mime_type:
                    mime_type = "application/octet-stream"

                current_parts.append(
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type
                    )
                )


            # ------------------------------------------------
            # Audio
            # ------------------------------------------------

            if audio:

                audio_bytes = audio.getvalue()

                audio_mime = audio.type

                if not audio_mime:
                    audio_mime = "audio/wav"

                current_parts.append(
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=audio_mime
                    )
                )


                # If only audio was sent, ask Gemini to understand it
                if not user_text:

                    current_parts.insert(
                        0,
                        types.Part.from_text(
                            text=(
                                "ఈ audio message ను వినండి. "
                                "అందులో చెప్పిన విషయాన్ని అర్థం చేసుకుని "
                                "తెలుగులో సహాయం చేయండి."
                            )
                        )
                    )


            # ------------------------------------------------
            # Make sure there is content
            # ------------------------------------------------

            if not current_parts:

                current_parts.append(
                    types.Part.from_text(
                        text="నమస్కారం"
                    )
                )


            contents.append(
                types.Content(
                    role="user",
                    parts=current_parts
                )
            )


            # =================================================
            # GEMINI REQUEST
            # =================================================

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "నీ పేరు Aurora AI. "
                        "నువ్వు స్నేహపూర్వకమైన, సహాయక AI assistant. "
                        "User తెలుగులో అడిగితే తెలుగులోనే సమాధానం ఇవ్వాలి. "
                        "User Englishలో అడిగితే Englishలో సమాధానం ఇవ్వాలి. "
                        "అవసరమైతే Telugu + English కలిపి సులభంగా వివరించాలి. "
                        "సమాధానాలు స్పష్టంగా, సహాయకంగా ఇవ్వాలి."
                    ),
                    temperature=0.7,
                    max_output_tokens=4096,
                ),
            )


            # =================================================
            # RESPONSE TEXT
            # =================================================

            reply = response.text

            if not reply:

                reply = (
                    "క్షమించండి, ఈసారి సమాధానం రాలేదు. "
                    "మళ్లీ ప్రయత్నించండి."
                )


            placeholder.markdown(reply)


            # =================================================
            # SAVE AI MESSAGE
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

            st.code(
                str(e),
                language="text"
            )
