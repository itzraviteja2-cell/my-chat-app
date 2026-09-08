import os
import base64
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

        if request.memory:
            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Important user memory: "
                            + request.memory
                        )
                    }
                ]
            })

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
            if not isinstance(text, str):
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


        # CURRENT MESSAGE

        contents.append({
            "role": "user",
            "parts": [
                {
                    "text": request.message
                }
            ]
        })


                # GEMINI RESPONSE WITH RETRY

        import time


        response = None
        last_error = None


        for attempt in range(3):

            try:

                response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=contents
)

                break


            except Exception as e:

                last_error = e


                if attempt < 2:

                    time.sleep(
                        2
                    )


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
@app.post("/generate-image")
def generate_image(request: ImageRequest):

    try:
        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",
            input=request.prompt
        )

        if not interaction.output_image:
            raise HTTPException(
                status_code=500,
                detail="Image was not generated"
            )

        return {
            "image": interaction.output_image.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
