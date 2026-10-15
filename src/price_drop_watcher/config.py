"""Read and validate the JSON watchlist."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass
class Product:
    name: str
    url: str
    price_selector: str


@dataclass
class Config:
    currency: str
    products: list[Product]


def _required_text(data: dict, key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a nonempty string")
    return value


def load_config(path: Path) -> Config:
    """Load a watchlist; raise ValueError for invalid configuration.

    File access failures propagate as OSError. Currency validation checks the
    code shape only; the configured currency must use two decimal places.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Configuration must contain valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a JSON object")
    currency = _required_text(data, "currency", "config")
    if re.fullmatch(r"[A-Z]{3}", currency) is None:
        raise ValueError("config.currency must contain three uppercase letters")
    entries = data.get("products")
    if not isinstance(entries, list) or not entries:
        raise ValueError("config.products must be a nonempty list")

    products = []
    seen_urls: set[str] = set()
    for index, entry in enumerate(entries):
        context = f"products[{index}]"
        if not isinstance(entry, dict):
            raise ValueError(f"{context} must be an object")
        name = _required_text(entry, "name", context)
        url = _required_text(entry, "url", context)
        selector = _required_text(entry, "price_selector", context)
        try:
            parsed = urlsplit(url)
            # Accessing port validates its syntax and range.
            _ = parsed.port
            valid = (
                parsed.scheme in {"http", "https"}
                and bool(parsed.hostname)
                and not any(char.isspace() or ord(char) < 32 for char in url)
                and parsed.username is None
                and parsed.password is None
            )
        except ValueError:
            valid = False
        if not valid:
            raise ValueError(f"{context}.url must be a valid HTTP(S) URL without credentials")
        if url in seen_urls:
            raise ValueError(f"{context}.url duplicates an earlier URL")
        seen_urls.add(url)
        products.append(Product(name=name, url=url, price_selector=selector))
    return Config(currency=currency, products=products)
