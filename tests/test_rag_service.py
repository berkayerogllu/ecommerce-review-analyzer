from unittest.mock import patch, MagicMock
from app.services.rag_service import build_context , build_messages , analyze_product

def test_build_context():
    review = MagicMock()
    review.id = 102
    review.payload = {
        "comment": "Kalıbı çok dar, ayağımı sıkıyor."
    }

    with patch(
        "app.services.rag_service.search_reviews",
        return_value=[review]
    ):
        context = build_context(
            question="Ayakkabının kalıbı nasıl?",
            product_id=12345
        )

    assert "[Review ID: 102]" in context
    assert "Kalıbı çok dar" in context

def test_build_context_empty():
    with patch(
        "app.services.rag_service.search_reviews",
        return_value=[]
    ):
        context = build_context(
            question="Bu ayakkabı su geçiriyor mu?",
            product_id=12345
        )

    assert context == ""

def test_build_messages():
    question = "Ayakkabının kalıbı dar mı?"
    context = "[Review ID: 102] Kalıbı çok dar."

    messages = build_messages(question, context)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert question in messages[1]["content"]
    assert context in messages[1]["content"]

def test_analyze_product():
    with patch(
        "app.services.rag_service.build_context",
        return_value="[Review ID: 101] Kalıbı dar."
    ), patch(
        "app.services.rag_service.generate_answer",
        return_value="Yorumlara göre kalıbı dar. (Review ID: 101)"
    ) as mock_llm:

        result = analyze_product(
            question="Ayakkabının kalıbı dar mı?",
            product_id=12345
        )

        assert "kalıbı dar" in result
        mock_llm.assert_called_once()

def test_analyze_product_empty_context():
    with patch(
        "app.services.rag_service.build_context",
        return_value=""
    ), patch(
        "app.services.rag_service.generate_answer"
    ) as mock_llm:

        result = analyze_product(
            question="Bu ayakkabı su geçiriyor mu?",
            product_id=12345
        )

        assert "yeterli müşteri yorumu bulunamadı" in result
        mock_llm.assert_not_called()

from app.services.rag_service import validate_citations


def test_validate_citations_valid():
    context = "[Review ID: 101] Kalıbı dar."
    answer = "Kalıbı dar olduğu belirtilmiş. (Review ID: 101)"

    assert validate_citations(answer, context) is True


def test_validate_citations_invalid():
    context = "[Review ID: 101] Kalıbı dar."
    answer = "Ürün çok rahat. (Review ID: 999)"

    assert validate_citations(answer, context) is False

def test_validate_citations_missing():
    context = "[Review ID: 101] Kalıbı dar."
    answer = "Ayakkabının kalıbı dar."

    assert validate_citations(answer, context) is False

def test_analyze_product_invalid_citation():
    with patch(
        "app.services.rag_service.build_context",
        return_value="[Review ID: 101] Kalıbı dar."
    ), patch(
        "app.services.rag_service.generate_answer",
        return_value="Ayakkabı rahat. (Review ID: 999)"
    ):
        result = analyze_product(
            question="Ayakkabının kalıbı dar mı?",
            product_id=12345
        )

    assert result == "Yanıtta doğrulanamayan kaynaklar bulundu."

def test_analyze_product_missing_citation():
    with patch(
        "app.services.rag_service.build_context",
        return_value="[Review ID: 101] Kalıbı dar."
    ), patch(
        "app.services.rag_service.generate_answer",
        return_value="Ayakkabının kalıbı dar."
    ):
        result = analyze_product(
            question="Ayakkabının kalıbı dar mı?",
            product_id=12345
        )

    assert result == "Yanıtta doğrulanamayan kaynaklar bulundu."

