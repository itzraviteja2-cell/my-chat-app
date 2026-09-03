import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(
    title="Aurora AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "app": "Aurora AI",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured"
        )

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=request.message
        )

        return {
            "reply": response.output_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
