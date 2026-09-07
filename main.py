import os

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form
)

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


# HOME PAGE

@app.get("/")
def home():

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

        for item in request.history:

                    role = item.get(
                "role",
                ""
            )

            text = item.get(
                "text",
                ""
            )


            # Image objects skip
            if not isinstance(
                text,
                str
            ):
                continue


            if role == "user":

                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    }
                )


            elif role == "bot":

                contents.append(
                    {
                        "role": "model",
                        "parts": [
                            {
                                "text": text
                            }
                        ]
                    }
                )


        # CURRENT MESSAGE

        contents.append(
            {
                "role": "user",
                "parts": [
                    {
                        "text": request.message
                    }
                ]
            }
        )


        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=contents

        )


        return {
            "reply": response.text
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# IMAGE CHAT

@app.post("/chat-image")
async def chat_image(

    message: str = Form(...),

    image: UploadFile = File(...)

):

    if not os.getenv(
        "GEMINI_API_KEY"
    ):

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )


    try:

        image_data = await image.read()


        image_part = types.Part.from_bytes(

            data=image_data,

            mime_type=image.content_type

        )


        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=[
                image_part,
                message
            ]

        )


        return {
            "reply": response.text
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
