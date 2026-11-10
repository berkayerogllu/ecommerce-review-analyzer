from fastapi import FastAPI
from app.api.product import router as product_router

app = FastAPI(
    title="E-Commerce Review Analyzer",
    description="RAG-based Trendyol customer review analysis API",
    version="1.0.0"
)

app.include_router(product_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}