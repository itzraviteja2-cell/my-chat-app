import os
import base64
import time

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google import genai
from google.genai import types


# APP

app = FastAPI(
    title="Aurora Smart AI",
    version="2.0.0"
)


# BASE DIRECTORY

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# STATIC FILES

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR
    ),
    name="static"
)


# GEMINI CLIENT

client = genai.Client(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


# CHAT REQUEST

class ChatRequest(BaseModel):
    message: str
    history: list = []
    memory: str = ""
    regenerate: bool = False


# IMAGE REQUEST

class ImageRequest(BaseModel):
    prompt: str


# HOME PAGE

@app.get("/")
def home():

    return FileResponse(
        os.path.join(
            BASE_DIR,
            "index.html"
        )
    )
    
# POLLINATIONS CALLBACK

@app.get("/pollinations/callback")
def pollinations_callback():

    return FileResponse(
        os.path.join(
            BASE_DIR,
            "index.html"
        )
    )

# HEALTH CHECK

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
    
# TINYFISH WEB SEARCH

from urllib.parse import quote
from urllib.request import Request, urlopen
import json


@app.get("/web-search")
def web_search(query: str):

    api_key = os.getenv("TINYFISH_API_KEY")

    if not api_key:

        raise HTTPException(
            status_code=500,
            detail="TINYFISH_API_KEY is not configured"
        )

    if not query.strip():

        raise HTTPException(
            status_code=400,
            detail="Search query is required"
        )

    try:

        url = (
            "https://api.search.tinyfish.ai?query="
            + quote(query.strip())
        )

        request = Request(
            url,
            headers={
                "X-API-Key": api_key
            }
        )

        with urlopen(
            request,
            timeout=10
        ) as response:

            search_data = json.loads(
                response.read().decode("utf-8")
            )

        return search_data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# TEXT CHAT

@app.post("/chat")
def chat(request: ChatRequest):

    if not os.getenv(
        "GEMINI_API_KEY"
    ):

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    try:

        contents = []

        # =========================
        # CHAT HISTORY
        # =========================

        for item in request.history:

            role = item.get(
                "role",
                ""
            )

            text = item.get(
                "text",
                ""
            )

            if not isinstance(
                text,
                str
            ):
                continue

            if not text.strip():
                continue

            if role == "user":

                contents.append({
                    "role": "user",
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                })

            elif role == "bot":

                contents.append({
                    "role": "model",
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                })


        # =========================
        # CURRENT MESSAGE
        # =========================

        current_message = request.message


        # =========================
        # REGENERATE
        # =========================

        if request.regenerate:

            current_message = (
                request.message
                + "\n\n"
                + "Give a fresh alternative answer. "
                + "Do not repeat your previous answer. "
                + "Use different wording, examples, "
                + "or approach."
            )


        contents.append({
            "role": "user",
            "parts": [
                {
                    "text": current_message
                }
            ]
        })


        # =========================
        # SMART MEMORY INSTRUCTION
        # =========================

        memory_instruction = ""

        if request.memory:

            memory_instruction = (
                "You have access to important saved memory "
                "about the user.\n\n"

                "IMPORTANT MEMORY:\n"
                + request.memory
                + "\n\n"

                "MEMORY RULES:\n"
                "1. Treat the saved memory above as trusted "
                "user information.\n"

                "2. If the user asks for information that is "
                "already present in the saved memory, use that "
                "information directly.\n"

                "3. Do NOT ask the user to provide information "
                "again when it is already present in memory.\n"

                "4. If the saved memory contains the user's name "
                "and the user asks 'నా పేరు ఏమిటి?', "
                "'What is my name?', or an equivalent question, "
                "answer using the saved name directly.\n"

                "5. Do not say that you need to remember the name "
                "again if the name is already in memory.\n"

                "6. Never invent information that is not present "
                "in memory.\n"
            )


        # =========================
        # GEMINI RESPONSE
        # =========================

        response = None
        last_error = None


        for attempt in range(3):

            try:

                response = client.models.generate_content(

                    model="gemini-3.6-flash",

                    contents=contents,

                    config=types.GenerateContentConfig(
                        system_instruction=
                            memory_instruction
                            if memory_instruction
                            else (
                                "You are Aurora Smart AI. "
                                "Answer the user's question "
                                "helpfully and naturally."
                            )
                    )

                )

                break


            except Exception as e:

                last_error = e

                if attempt < 2:

                    time.sleep(2)


        if response is None:

            raise last_error


        return {
            "reply": response.text
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
