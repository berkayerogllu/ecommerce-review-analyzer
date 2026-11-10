from pydantic import BaseModel, HttpUrl

class ProductRequest(BaseModel):
    product_url: HttpUrl
    question: str
    