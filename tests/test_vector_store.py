from app.services.vector_store import search_reviews
from app.models.review import Review
from app.services.vector_store import store_reviews
from app.core.vector_db import client, COLLECTION_NAME


def test_search_reviews_threshold(test_qdrant):
    reviews = [
        Review(
            review_id=101,
            product_id=12345,
            rating=2,
            comment="Ayakkabının kalıbı çok dar."
        ),
        Review(
            review_id=102,
            product_id=99999,
            rating=5,
            comment="Ayakkabının kalıbı çok dar."
        )
    ]

    store_reviews(reviews)

    results = search_reviews(
        question="Ayakkabının kalıbı dar mı?",
        product_id=12345,
        score_threshold=0.80
    )

    assert len(results) == 1
    assert results[0].id == 101
    assert results[0].score >= 0.80

def test_store_reviews_batch(test_qdrant):
    reviews = [
        Review(
            review_id=201,
            product_id=12345,
            rating=5,
            comment="Ayakkabı çok rahat."
        ),
        Review(
            review_id=202,
            product_id=12345,
            rating=2,
            comment="Kalıbı oldukça dar."
        )
    ]

    store_reviews(reviews)

    stored = test_qdrant.retrieve(
        collection_name=COLLECTION_NAME,
        ids=[201, 202],
        with_payload=True
    )

    assert len(stored) == 2
    assert {r.id for r in stored} == {201, 202}

from app.services.vector_store import product_has_reviews


def test_product_has_reviews(test_qdrant):

    assert product_has_reviews(12345) is False

    review = Review(
        review_id=501,
        product_id=12345,
        rating=5,
        comment="Ürün çok kaliteli."
    )

    store_reviews([review])

    assert product_has_reviews(12345) is True


    assert product_has_reviews(99999) is False
