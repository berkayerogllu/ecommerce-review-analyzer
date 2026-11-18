from urllib.parse import urlparse
import re
from typing import Optional


def validate_trendyol_url(product_url: str) -> bool:
    parsed_url = urlparse(product_url)

    return (
        parsed_url.scheme == "https"
        and parsed_url.hostname in ("trendyol.com", "www.trendyol.com")
        and not parsed_url.username
        and not parsed_url.password
    )


def extract_product_id(product_url: str) -> Optional[str]:
    parsed_url = urlparse(product_url)

    match = re.search(r"-p-(\d+)(?:/|$)", parsed_url.path)

    return match.group(1) if match else None
