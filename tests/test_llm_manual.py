from app.services.llm_service import generate_answer
from app.services.rag_service import build_messages

question = "Bu ayakkabının kalıbı dar mı?"

context = """
[Review ID: 101] Kalıbı çok dar, ayağımı sıkıyor.
[Review ID: 102] Bence oldukça rahat.
"""

messages = build_messages(question, context)

answer = generate_answer(messages)

print(answer)