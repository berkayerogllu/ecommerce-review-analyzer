from qdrant_client.models import PointStruct

from app.core.vector_db import client, COLLECTION_NAME
from app.services.embedding_service import embed_review
from app.models.review import Review
from app.services.embedding_service import embed_query
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List
from app.services.embedding_service import get_model


def store_review(review: Review):
    vector = embed_review(review.comment).tolist()

    point = PointStruct(
        id=review.review_id,
        vector=vector,
        payload={
            "product_id": review.product_id,
            "rating": review.rating,
            "comment": review.comment
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )

def search_reviews(question: str, product_id: int, limit: int = 5,score_threshold: float = 0.80):
    query_vector = embed_query(question).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="product_id",
                    match=MatchValue(value=product_id)
                )
            ]
        ),
        limit=limit,
        score_threshold=score_threshold
    )

    return results.points

def store_reviews(reviews: List[Review]):
    if not reviews:
        return

    vectors = get_model().encode(
        [f"passage: {review.comment}" for review in reviews]
    )

    points = [
        PointStruct(
            id=review.review_id,
            vector=vector.tolist(),
            payload={
                "product_id": review.product_id,
                "rating": review.rating,
                "comment": review.comment
            }
        )
        for review, vector in zip(reviews, vectors)
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def product_has_reviews(product_id: int) -> bool:
    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="product_id",
                    match=MatchValue(value=product_id)
                )
            ]
        ),
        limit=1,
        with_payload=False,
        with_vectors=False
    )

    points, _ = results
    return len(points) > 0
