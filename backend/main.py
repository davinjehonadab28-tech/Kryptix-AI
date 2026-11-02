
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000)
)

MODEL = "gemini-3.5-flash-lite"

# FastAPI application
app = FastAPI(
    title="Valentius Kryptix Chatbot",
    description="An AI chatbot powered by Google Gemini"
)

# Custom system prompt
SYSTEM_PROMPT = """
You are Kryptix Assistant, a helpful and friendly AI chatbot.

Your purpose is to answer questions, explain concepts,
assist with learning, and help users solve problems.

Personality:
- Friendly and professional.
- Clear and easy-to-understand explanations.
- Give accurate and useful answers.
- Remember the context of the current conversation.
"""

# Store conversation history
conversation_history = {}

# Keep only the latest 10 messages
MAX_HISTORY = 10


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


@app.get("/")
def home():
    return {
        "message": "Kryptix Assistant API is running!"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    conversation_id = request.conversation_id or str(uuid.uuid4())

    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = []

    history = conversation_history[conversation_id]

    # Add the latest user message
    history.append({
        "role": "user",
        "parts": [{"text": request.message}]
    })

    # Context management
    recent_history = history[-MAX_HISTORY:]

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=recent_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        reply = response.text

        # Save assistant response
        history.append({
            "role": "model",
            "parts": [{"text": reply}]
        })

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply
        )

    except Exception as error:

        # Remove the failed user message
        history.pop()

        raise HTTPException(
            status_code=503,
            detail=f"Gemini API error: {str(error)}"
        )
