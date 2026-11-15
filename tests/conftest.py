import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

@pytest.fixture
def test_qdrant(monkeypatch):
    client = QdrantClient(":memory:")

    client.create_collection(
        collection_name="product_reviews",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    monkeypatch.setattr(
        "app.services.vector_store.client",
        client
    )

    yield client
    client.close()