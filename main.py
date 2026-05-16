from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

with open("catalog.json", "r") as f:
    catalog = json.loads(f.read(), strict=False)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommendation API Running"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

def extract_text(item):

    values = []

    for key, value in item.items():

        if isinstance(value, str):
            values.append(value.lower())

        elif isinstance(value, list):

            for v in value:

                if isinstance(v, str):
                    values.append(v.lower())

    return " ".join(values)

def generate_recommendations(history):

    query_words = set(history.split())

    important_keywords = [
        "java",
        "spring",
        "sql",
        "aws",
        "docker",
        "angular",
        "python",
        "excel",
        "word",
        "finance",
        "sales",
        "leadership",
        "safety",
        "networking",
        "customer",
        "service"
    ]

    detected_keywords = []

    for keyword in important_keywords:

        if keyword in history:
            detected_keywords.append(keyword)

    scored = []

    for item in catalog:

        text = extract_text(item)

        score = 0

        for keyword in detected_keywords:

            if keyword in text:
                score += 5

        for word in query_words:

            if len(word) > 3 and word in text:
                score += 1

        if score >= 3:
            scored.append((score, item))

    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    recommendations = []

    seen = set()

    for _, item in scored:

        name = item.get(
            "name",
            item.get("title", "Unknown")
        )

        if name in seen:
            continue

        seen.add(name)

        recommendations.append({
            "name": name,
            "url": item.get(
                "url",
                item.get("product_url", "")
            ),
            "test_type": item.get(
                "test_type",
                item.get("assessment_type", "Unknown")
            )
        })

        if len(recommendations) >= 10:
            break

    return recommendations

@app.post("/chat")
def chat(request: ChatRequest):

    latest = request.messages[-1].content.lower()

    history = " ".join([
        m.content for m in request.messages
    ]).lower()

    blocked_words = [
        "salary",
        "legal",
        "law",
        "visa",
        "immigration",
        "tax"
    ]

    for word in blocked_words:

        if word in latest:

            return {
                "reply": "I can only assist with SHL assessment recommendations and catalog-related queries.",
                "recommendations": None,
                "end_of_conversation": False
            }

    if (
        "difference" in latest or
        "compare" in latest or
        "vs" in latest
    ):

        return {
            "reply": "These assessments measure different dimensions such as aptitude, personality, technical knowledge, or situational judgement.",
            "recommendations": None,
            "end_of_conversation": False
        }

    vague_terms = [
        "assessment",
        "test",
        "solution",
        "hiring"
    ]

    if (
        any(word in latest for word in vague_terms)
        and len(latest.split()) < 6
    ):

        return {
            "reply": "Could you share the role, seniority level, and the most important skills or competencies required?",
            "recommendations": None,
            "end_of_conversation": False
        }

    recommendations = generate_recommendations(history)

    if not recommendations:

        return {
            "reply": "I could not find strong matches in the SHL catalog. Could you refine the role requirements or required skills?",
            "recommendations": None,
            "end_of_conversation": False
        }

    return {
        "reply": "Here are relevant SHL assessments based on your requirements.",
        "recommendations": recommendations,
        "end_of_conversation": True
    }

@app.get("/evaluate")
def evaluate():

    sample_query = (
        "Hiring Java backend developer with Spring and SQL"
    )

    expected = [
        "Core Java (Advanced Level) (New)",
        "Java 8 (New)"
    ]

    predictions = generate_recommendations(
        sample_query.lower()
    )

    predicted_names = [
        item["name"]
        for item in predictions
    ]

    hits = 0

    matched = []

    for item in expected:

        if item in predicted_names:
            hits += 1
            matched.append(item)

    recall_at_10 = hits / len(expected)

    return {
        "query": sample_query,
        "expected": expected,
        "predicted": predicted_names,
        "matched_items": matched,
        "hits": hits,
        "recall@10": recall_at_10
    }
