from pydantic import BaseModel


class Review(BaseModel):
    review_id: int
    product_id: int
    rating: int
    comment: str