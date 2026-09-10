import os
import base64
import time

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

        # MEMORY

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


        # CHAT HISTORY

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

        current_message = request.message


        # REGENERATE

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


        # GEMINI RESPONSE WITH RETRY

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


# IMAGE CHAT
# PHOTO + TEXT

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

        # READ IMAGE

        image_bytes = await image.read()


        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Image file is empty"
            )


        # MIME TYPE

        mime_type = (
            image.content_type
            or "image/jpeg"
        )


        # USER INSTRUCTION

        user_message = (
            message.strip()
            if message
            else "Analyze this image"
        )


        prompt = (
            "Look at the uploaded image carefully "
            "and respond to the user's request.\n\n"
            "User request:\n"
            + user_message
        )


        # SEND IMAGE + TEXT TO GEMINI

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=[

                types.Content(

                    role="user",

                    parts=[

                        types.Part.from_bytes(

                            data=image_bytes,

                            mime_type=mime_type

                        ),

                        types.Part.from_text(

                            text=prompt

                        )

                    ]

                )

            ]

        )


        # CHECK RESPONSE

        for candidate in response.candidates:

            if not candidate.content:

                continue


            for part in candidate.content.parts:


                # TEXT RESPONSE

                if part.text:

                    return {
                        "reply": part.text
                    }


                # IMAGE RESPONSE

                if part.inline_data:

                    image_data = (
                        part.inline_data.data
                    )


                    return {
                        "image":
                            base64.b64encode(
                                image_data
                            ).decode("utf-8")
                    }


        raise HTTPException(
            status_code=500,
            detail="No response generated from image"
        )


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# IMAGE GENERATION

@app.post("/generate-image")
def generate_image(
    request: ImageRequest
):

    if not os.getenv(
        "GEMINI_API_KEY"
    ):

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )


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

            "image":
                interaction.output_image.data

        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
