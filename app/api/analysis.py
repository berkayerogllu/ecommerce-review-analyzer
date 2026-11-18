import httpx
from fastapi import APIRouter, HTTPException

from app.core.http_client import create_http_client
from app.models.analysis import AnalyzeRequest
from app.services.ingestion_service import ingest_product_reviews
from app.services.product_resolver import extract_product_id, validate_trendyol_url
from app.services.rag_service import analyze_product
from app.services.vector_store import product_has_reviews

router = APIRouter(prefix="/api/v1", tags=["Analysis"])


@router.get("/analyze")
def analyze_info():
    return {
        "message": "Use POST /api/v1/analyze with product_url and question.",
        "docs": "/docs",
    }


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    url = str(request.product_url)
    if not validate_trendyol_url(url):
        raise HTTPException(status_code=400, detail="Only Trendyol URLs are supported")

    product_id_text = extract_product_id(url)
    if product_id_text is None:
        raise HTTPException(status_code=400, detail="Invalid product URL")
    product_id = int(product_id_text)

    if not product_has_reviews(product_id):
        try:
            async with create_http_client() as client:
                count = await ingest_product_reviews(client, product_id)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise HTTPException(status_code=503, detail="Review service is temporarily unavailable") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                raise HTTPException(status_code=503, detail="Review provider denied access") from exc
            raise HTTPException(status_code=502, detail="Review provider returned an error") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=502, detail="Review provider returned an invalid response") from exc

        if count == 0:
            raise HTTPException(status_code=404, detail="No reviews found for this product")

    try:
        answer = analyze_product(question=request.question, product_id=product_id)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Analysis service is not configured") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Analysis service failed") from exc

    return {"product_id": product_id, "answer": answer}
