import os

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types


app = FastAPI(
    title="Aurora Smart AI",
    version="2.0.0"
)
app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# TEXT CHAT

@app.post("/chat")
def chat(request: ChatRequest):

    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=request.message
        )

        return {
            "reply": response.text
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# IMAGE + MESSAGE CHAT

@app.post("/chat-image")
async def chat_image(

    message: str = Form(...),

    image: UploadFile = File(...)

):

    if not os.getenv("GEMINI_API_KEY"):

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
