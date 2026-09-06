import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
def chat(request: ChatRequest):
    if not os.getenv("GEMINI_API_KEY"):

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    try:

        contents = []

        for item in request.history:

            if item.get("role") == "user":

                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": item.get(
                                    "text",
                                    ""
                                )
                            }
                        ]
                    }
                )

            elif item.get("role") == "bot":

                contents.append(
                    {
                        "role": "model",
                        "parts": [
                            {
                                "text": item.get(
                                    "text",
                                    ""
                                )
                            }
                        ]
                    }
                )


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
