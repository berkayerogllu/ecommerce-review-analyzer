from fastapi import FastAPI
from app.api.product import router as product_router
from app.api.analysis import router as analysis_router
from app.core.vector_db import create_collection

app = FastAPI(
    title="E-Commerce Review Analyzer",
    description="RAG-based Trendyol customer review analysis API",
    version="1.0.0"
)

app.include_router(product_router)
app.include_router(analysis_router)


@app.on_event("startup")
def initialize_storage():
    create_collection()

@app.get("/health")
def health_check():
    return {"status": "healthy"}
