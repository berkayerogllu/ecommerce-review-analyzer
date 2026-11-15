from app.services.embedding_service import embed_review
from sentence_transformers import util


def test_semantic_similarity():
    text1 = embed_review("Ayakkabının kalıbı dar.")
    text2 = embed_review("Ayakkabı ayağımı sıkıyor.")
    text3 = embed_review("Kargo çok hızlı geldi.")

    similarity_12 = util.cos_sim(text1, text2).item()
    similarity_13 = util.cos_sim(text1, text3).item()

    print(f"Benzer yorumlar: {similarity_12:.3f}")
    print(f"Farklı yorumlar: {similarity_13:.3f}")

    assert similarity_12 > similarity_13