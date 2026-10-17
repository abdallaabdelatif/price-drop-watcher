"""Synchronous extraction; the caller owns the page and browser."""

from dataclasses import dataclass
from datetime import datetime, timezone

from playwright.sync_api import Error, Page, TimeoutError as PlaywrightTimeoutError

from price_drop_watcher.config import Product
from price_drop_watcher.prices import parse_price

NAVIGATION_TIMEOUT_MS = 30_000
PRICE_TIMEOUT_MS = 20_000


@dataclass(frozen=True)
class PriceResult:
    product_url: str
    price_minor: int
    currency: str
    observed_at_utc: datetime


class ScrapeError(Exception):
    """A product could not yield one valid current price."""


def fetch_price(page: Page, product: Product, currency: str) -> PriceResult:
    """Navigate to the exact URL and extract exactly one CSS-matched price."""
    try:
        response = page.goto(
            product.url, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS
        )
        if response is not None and response.status >= 400:
            raise ScrapeError(f"Navigation returned HTTP {response.status}")
    except PlaywrightTimeoutError as exc:
        raise ScrapeError("Navigation timed out") from exc
    except Error as exc:
        raise ScrapeError("Navigation failed") from exc

    try:
        locator = page.locator(f"css={product.price_selector}")
        locator.first.wait_for(state="visible", timeout=PRICE_TIMEOUT_MS)
        if locator.count() != 1:
            raise ScrapeError("Price selector must match exactly one element")
        text = locator.inner_text(timeout=PRICE_TIMEOUT_MS)
    except PlaywrightTimeoutError as exc:
        raise ScrapeError("Price missing or not visible before timeout") from exc
    except Error as exc:
        raise ScrapeError("Price selector or extraction failed") from exc
    try:
        minor = parse_price(text, currency)
    except ValueError as exc:
        raise ScrapeError(f"Invalid price: {exc}") from exc
    return PriceResult(product.url, minor, currency, datetime.now(timezone.utc))
