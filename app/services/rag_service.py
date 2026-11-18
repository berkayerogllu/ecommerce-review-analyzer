from app.services.vector_store import search_reviews
from app.core.prompts import RAG_SYSTEM_PROMPT
from app.services.llm_service import generate_answer
import re


def build_context(question: str, product_id: int) -> str:
    results = search_reviews(
        question=question,
        product_id=product_id,
        limit=5,
        score_threshold=0.80
    )

    if not results:
        return ""

    context = "\n".join(
        f"[Review ID: {result.id}] {result.payload['comment']}"
        for result in results
    )

    return context

def build_messages(question: str ,context: str) -> list:
    return [
        {
            "role": "system",
            "content": RAG_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": (
                f"Müşteri yorumları:\n{context}\n\n"
                f"Soru: {question}"
            )
        }
    ]

def analyze_product(question: str, product_id: int) -> str:
    context = build_context(question, product_id)

    if not context:
        return "Bu soruyu yanıtlamak için yeterli müşteri yorumu bulunamadı."

    messages = build_messages(question, context)
    answer = generate_answer(messages)

    if not validate_citations(answer, context):
        return "Yanıtta doğrulanamayan kaynaklar bulundu."

    return answer

def validate_citations(answer: str, context: str) -> bool:
    valid_ids = set(re.findall(r"\[Review ID: (\d+)\]", context))
    cited_ids = set(re.findall(r"Review ID:\s*(\d+)", answer))

    return bool(cited_ids) and cited_ids.issubset(valid_ids)


