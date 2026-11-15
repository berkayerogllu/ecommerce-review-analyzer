from app.services.review_collector import parse_review , parse_reviews , collect_reviews , collect_review_pages
import pytest
import httpx
from urllib.parse import urlparse, parse_qs
from app.services.review_collector import build_review_url


def test_parse_review():
    raw_review = {
        "id": 666411762,
        "contentId": 1198082362,
        "rate": 5,
        "comment": "Kamera özellikleri çok iyi."
    }

    review = parse_review(raw_review)

    assert review.review_id == 666411762
    assert review.product_id == 1198082362
    assert review.rating == 5
    assert review.comment == "Kamera özellikleri çok iyi."


def test_parse_reviews():
    raw_data = {
        "result": {
            "reviews": [
                {
                    "id": 101,
                    "contentId": 12345,
                    "rate": 5,
                    "comment": "Ürün çok güzel."
                },
                {
                    "id": 102,
                    "contentId": 12345,
                    "rate": 2,
                    "comment": "Beklediğim gibi değildi."
                }
            ]
        }
    }

    reviews = parse_reviews(raw_data)

    assert len(reviews) == 2
    assert reviews[0].review_id == 101
    assert reviews[1].rating == 2    

@pytest.mark.anyio
async def test_collect_reviews():
    def mock_handler(request):
        return httpx.Response(200, json={
            "result": {
                "reviews": [
                    {
                        "id": 101,
                        "contentId": 12345,
                        "rate": 5,
                        "comment": "Ürün çok kaliteli."
                    }
                ]
            }
        })

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        reviews = await collect_reviews(
            client,
            "https://example.com/reviews"
        )

    assert len(reviews) == 1
    assert reviews[0].comment == "Ürün çok kaliteli."

@pytest.mark.anyio
async def test_collect_reviews_http_error():
    def mock_handler(request):
        return httpx.Response(500)

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await collect_reviews(
                client,
                "https://example.com/reviews"
            )

@pytest.mark.anyio
async def test_collect_reviews_timeout():
    def mock_handler(request):
        raise httpx.ReadTimeout("Request timed out", request=request)

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.ReadTimeout):
            await collect_reviews(
                client,
                "https://example.com/reviews"
            )


def test_build_review_url():
    url = build_review_url(product_id=1198082362, page=1)

    params = parse_qs(urlparse(url).query)

    assert params["contentId"] == ["1198082362"]
    assert params["page"] == ["1"]
    assert params["pageSize"] == ["20"]


@pytest.mark.anyio
async def test_collect_review_pages():
    from app.services.review_collector import collect_review_pages

    requested_pages = []

    def mock_handler(request):
        from urllib.parse import parse_qs

        page = int(parse_qs(request.url.query.decode())["page"][0])
        requested_pages.append(page)

        # İlk sayfada 20, ikinci sayfada 2 yorum
        count = 20 if page == 0 else 2

        reviews = [
            {
                "id": page * 100 + i,
                "contentId": 12345,
                "rate": 5,
                "comment": f"Yorum {i}"
            }
            for i in range(count)
        ]

        return httpx.Response(200, json={"result": {"reviews": reviews}})

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        reviews = await collect_review_pages(client, 12345)

    assert len(reviews) == 22
    assert requested_pages == [0, 1]


@pytest.mark.anyio
async def test_collect_reviews_filters_wrong_product():
    from app.services.review_collector import collect_review_pages

    def mock_handler(request):
        return httpx.Response(200, json={
            "result": {
                "reviews": [
                    {
                        "id": 101,
                        "contentId": 12345,
                        "rate": 5,
                        "comment": "Doğru ürün"
                    },
                    {
                        "id": 102,
                        "contentId": 99999,
                        "rate": 1,
                        "comment": "Yanlış ürün"
                    }
                ]
            }
        })

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        reviews = await collect_review_pages(client, 12345)

    assert len(reviews) == 1
    assert reviews[0].product_id == 12345

@pytest.mark.anyio
async def test_collect_reviews_removes_duplicates():
    def mock_handler(request):
        return httpx.Response(200, json={
            "result": {
                "reviews": [
                    {
                        "id": 101,
                        "contentId": 12345,
                        "rate": 5,
                        "comment": "Güzel ürün"
                    },
                    {
                        "id": 101,
                        "contentId": 12345,
                        "rate": 5,
                        "comment": "Güzel ürün"
                    }
                ]
            }
        })

    transport = httpx.MockTransport(mock_handler)

    async with httpx.AsyncClient(transport=transport) as client:
        reviews = await collect_review_pages(client, 12345)

    assert len(reviews) == 1
    assert reviews[0].review_id == 101    