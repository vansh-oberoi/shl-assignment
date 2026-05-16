from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

with open("catalog.json") as f:
    catalog = json.load(f)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):

    latest = request.messages[-1].content.lower()

    history = " ".join([
        m.content for m in request.messages
    ]).lower()

    if "salary" in latest or "legal" in latest:
        return {
            "reply": "I can only assist with SHL assessments.",
            "recommendations": [],
            "end_of_conversation": False
        }

    if "difference" in latest or "compare" in latest:
        return {
            "reply": "OPQ measures personality traits while GSA measures cognitive ability.",
            "recommendations": [],
            "end_of_conversation": False
        }

    if len(latest.split()) < 3:
        return {
            "reply": "Please share role and required skills.",
            "recommendations": [],
            "end_of_conversation": False
        }

    matches = []

    for item in catalog:

        text = (
            item["name"] + " " +
            item["description"] + " " +
            " ".join(item["skills"])
        ).lower()

        score = 0

        for word in history.split():
            if word in text:
                score += 1

        if score > 0:
            matches.append((score, item))

    matches.sort(reverse=True, key=lambda x: x[0])

    result = []

    for _, item in matches[:5]:
        result.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item["test_type"]
        })

    return {
        "reply": "Here are relevant SHL assessments.",
        "recommendations": result,
        "end_of_conversation": False
    }
