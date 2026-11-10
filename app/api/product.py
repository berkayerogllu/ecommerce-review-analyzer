from fastapi import APIRouter, HTTPException
from app.models.product import ProductRequest
from app.services.product_resolver import (
    validate_trendyol_url,
    extract_product_id)

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

@router.post("/resolve")
def resolve_product(request: ProductRequest):
    url = str(request.product_url)

    if not validate_trendyol_url(url):
        raise HTTPException(
            status_code=400,
            detail="Only Trendyol URLs are supported"
        )
    
    product_id = extract_product_id(url)
    return {"product_id": product_id}
    