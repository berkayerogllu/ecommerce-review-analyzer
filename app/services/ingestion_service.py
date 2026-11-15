import httpx

from app.services.review_collector import collect_review_pages
from app.services.vector_store import store_reviews


async def ingest_product_reviews(
    client: httpx.AsyncClient,
    product_id: int
) -> int:
    reviews = await collect_review_pages(client, product_id)

    if not reviews:
        return 0

    store_reviews(reviews)

    return len(reviews)