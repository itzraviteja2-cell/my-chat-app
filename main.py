import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
def chat(request: ChatRequest):
