from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"

model = None


def get_model() -> SentenceTransformer:
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

def embed_review(text: str):
    return get_model().encode(f"passage: {text}")

def embed_query(question: str):
    return get_model().encode(f"query: {question}")
