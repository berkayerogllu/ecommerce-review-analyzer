from app.models.review import Review
from typing import List
import httpx
from urllib.parse import urlencode


def parse_review(data: dict) -> Review:
    return Review(
        review_id=data["id"],
        product_id=data["contentId"],
        rating=data["rate"],
        comment=data["comment"]
    )

def parse_reviews(data: dict) -> List[Review]:
    raw_reviews = data["result"]["reviews"]

    return [
        parse_review(review)
        for review in raw_reviews
    ]

async def collect_reviews(
    client: httpx.AsyncClient,
    url: str
) -> List[Review]:

    response = await client.get(url)
    response.raise_for_status()

    return parse_reviews(response.json())


REVIEW_API_URL = (
    "https://apigw.trendyol.com/"
    "discovery-storefront-trproductgw-service/"
    "api/review-read/product-reviews/detailed"
)

def build_review_url(product_id: int, page: int = 0) -> str:
    params = {
        "contentId": product_id,
        "page": page,
        "pageSize": 20,
        "order": "DESC",
        "orderBy": "Score",
        "channelId": 1
    }

    return f"{REVIEW_API_URL}?{urlencode(params)}"

async def collect_review_pages(
    client: httpx.AsyncClient,
    product_id: int,
    max_pages: int = 3
) -> List[Review]:

    all_reviews = []
    seen_review_ids = set()

    for page in range(max_pages):
        url = build_review_url(product_id, page)
        reviews = await collect_reviews(client, url)

        valid_reviews = [
        review for review in reviews
        if review.product_id == product_id
        ]
        
        for review in valid_reviews:
            if review.review_id not in seen_review_ids:
                seen_review_ids.add(review.review_id)
                all_reviews.append(review)

        if len(reviews) < 20:
            break

    return all_reviews


