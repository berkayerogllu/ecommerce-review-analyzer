from app.services.product_resolver import extract_product_id
from app.services.product_resolver import validate_trendyol_url

def test_extract_product_id():
    url = "https://www.trendyol.com/lumenascent/snow-soft-oda-kokusu-kar-yumusakliginda-huzur-p-1080007436"
    result = extract_product_id(url)
    assert result == "1080007436"

def test_validate_trendyo_url():
    valid_url = "https://www.trendyol.com/lumenascent/snow-soft-oda-kokusu-kar-yumusakliginda-huzur-p-1080007436"
    invalid_url = "https://www.example.com/product/12345"

    assert validate_trendyol_url(valid_url) is True
    assert validate_trendyol_url(invalid_url) is False