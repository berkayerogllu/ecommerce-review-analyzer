from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_resolve_product():
    response = client.post(
        "/api/v1/products/resolve",
        json={
            "product_url": "https://www.trendyol.com/nike/air-max-p-123456",
            "question": "Bu ayakkabının kalıbı dar mı?"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"product_id": "123456"}