from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock
import httpx
import pytest

client = TestClient(app)


def test_analyze_existing_product():
    with patch(
        "app.api.analysis.product_has_reviews",
        return_value=True
    ), patch(
        "app.api.analysis.analyze_product",
        return_value="Kalıbı dar. (Review ID: 101)"
    ) as mock_analyze:

        response = client.post(
            "/api/v1/analyze",
            json={
                "product_url": "https://www.trendyol.com/nike/air-max-p-12345",
                "question": "Kalıbı dar mı?"
            }
        )

    assert response.status_code == 200
    assert response.json()["product_id"] == 12345
    mock_analyze.assert_called_once()

def test_analyze_new_product():
    with patch(
        "app.api.analysis.product_has_reviews",
        return_value=False
    ), patch(
        "app.api.analysis.ingest_product_reviews",
        new_callable=AsyncMock
    ) as mock_ingest, patch(
        "app.api.analysis.analyze_product",
        return_value="Ürün rahat. (Review ID: 101)"
    ):

        mock_ingest.return_value = 3

        response = client.post(
            "/api/v1/analyze",
            json={
                "product_url": "https://www.trendyol.com/nike/air-max-p-12345",
                "question": "Ayakkabı rahat mı?"
            }
        )

    assert response.status_code == 200
    mock_ingest.assert_awaited_once()

def test_analyze_ingestion_timeout():
    with patch(
        "app.api.analysis.product_has_reviews",
        return_value=False
    ), patch(
        "app.api.analysis.ingest_product_reviews",
        new_callable=AsyncMock
    ) as mock_ingest, patch(
        "app.api.analysis.analyze_product"
    ) as mock_analyze:

        mock_ingest.side_effect = httpx.ReadTimeout(
            "Review service timed out"
        )

        response = client.post(
    "/api/v1/analyze",
        json={
            "product_url": "https://www.trendyol.com/nike/air-max-p-12345",
            "question": "Ayakkabı rahat mı?"
        }
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Review service is temporarily unavailable"
    )
    mock_analyze.assert_not_called()

def test_analyze_no_reviews():
    with patch(
        "app.api.analysis.product_has_reviews",
        return_value=False
    ), patch(
        "app.api.analysis.ingest_product_reviews",
        new_callable=AsyncMock
    ) as mock_ingest, patch(
        "app.api.analysis.analyze_product"
    ) as mock_analyze:

        mock_ingest.return_value = 0

        response = client.post(
            "/api/v1/analyze",
            json={
                "product_url": "https://www.trendyol.com/nike/air-max-p-12345",
                "question": "Ayakkabı rahat mı?"
            }
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this product"
    mock_analyze.assert_not_called()