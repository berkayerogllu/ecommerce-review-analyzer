from app.models.review import Review
from app.services.vector_store import store_review

reviews = [
    Review(review_id=102, product_id=12345, rating=2,
           comment="Kalıbı çok dar, ayağımı sıkıyor."),
    Review(review_id=103, product_id=12345, rating=5,
           comment="Kargo çok hızlı geldi."),
    Review(review_id=104, product_id=12345, rating=4,
           comment="Ayakkabının malzeme kalitesi güzel.")
]

for review in reviews:
    store_review(review)

print("3 reviews stored")