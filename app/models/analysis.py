from pydantic import BaseModel, HttpUrl, Field

class AnalyzeRequest(BaseModel):
    product_url: HttpUrl
    question: str = Field(min_length=3, max_length=500)