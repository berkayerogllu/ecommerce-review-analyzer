from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"

model = SentenceTransformer(MODEL_NAME)

def embed_review(text: str):
    return model.encode(f"passage: {text}")

def embed_query(question: str):
    return model.encode(f"query: {question}")