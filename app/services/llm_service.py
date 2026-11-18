from groq import Groq
from app.core.config import get_groq_api_key

MODEL_NAME = "qwen/qwen3.8-27b"


def generate_answer(messages: list) -> str:
    client = Groq(api_key=get_groq_api_key())

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2,
        max_completion_tokens=500
    )

    return response.choices[0].message.content