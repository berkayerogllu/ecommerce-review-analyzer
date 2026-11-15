from unittest.mock import AsyncMock, patch
import pytest

from app.models.review import Review
from app.services.ingestion_service import ingest_product_reviews


@pytest.mark.anyio
async def test_ingest_product_reviews():
    reviews = [
        Review(
            review_id=301,
            product_id=12345,
            rating=5,
            comment="Ürün çok kaliteli."
        )
    ]

    with patch(
        "app.services.ingestion_service.collect_review_pages",
        new_callable=AsyncMock
    ) as mock_collect, patch(
        "app.services.ingestion_service.store_reviews"
    ) as mock_store:

        mock_collect.return_value = reviews

        result = await ingest_product_reviews(None, 12345)

        assert result == 1
        mock_collect.assert_awaited_once_with(None, 12345)
        mock_store.assert_called_once_with(reviews)

@pytest.mark.anyio
async def test_ingest_product_reviews_empty():
    with patch(
        "app.services.ingestion_service.collect_review_pages",
        new_callable=AsyncMock
    ) as mock_collect, patch(
        "app.services.ingestion_service.store_reviews"
    ) as mock_store:

        mock_collect.return_value = []

        result = await ingest_product_reviews(None, 12345)

        assert result == 0
        mock_store.assert_not_called()

import httpx


@pytest.mark.anyio
async def test_ingest_product_reviews_collector_error():
    with patch(
        "app.services.ingestion_service.collect_review_pages",
        new_callable=AsyncMock
    ) as mock_collect, patch(
        "app.services.ingestion_service.store_reviews"
    ) as mock_store:

        mock_collect.side_effect = httpx.ReadTimeout(
            "Review service timed out"
        )

        with pytest.raises(httpx.ReadTimeout):
            await ingest_product_reviews(None, 12345)

        mock_store.assert_not_called()

