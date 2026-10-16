from datetime import timedelta
from contextlib import contextmanager
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from price_drop_watcher.config import Product
from price_drop_watcher import scraper
from price_drop_watcher.scraper import ScrapeError, fetch_price
from price_drop_watcher import __main__ as cli

FIXTURES = Path(__file__).parent / "fixtures"
URL = "http://fixture.test/product"
PRODUCT = Product("Fixture", URL, ".price")


@pytest.fixture
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


def serve(context, fixture):
    html = (FIXTURES / fixture).read_text(encoding="utf-8")
    context.route("**/*", lambda route: route.fulfill(content_type="text/html", body=html))


@pytest.mark.parametrize("fixture,expected", [("normal.html", 123450), ("delayed.html", 9995)])
def test_extract(browser, fixture, expected):
    with browser.new_context() as context:
        serve(context, fixture)
        result = fetch_price(context.new_page(), PRODUCT, "EGP")
    assert result.product_url == URL
    assert result.price_minor == expected
    assert result.currency == "EGP"
    assert result.observed_at_utc.utcoffset() == timedelta(0)
    assert browser.contexts == []


@pytest.mark.parametrize("fixture,message", [
    ("missing.html", "missing"), ("multiple.html", "exactly one"),
    ("malformed.html", "Invalid price"),
])
def test_extraction_errors(browser, monkeypatch, fixture, message):
    monkeypatch.setattr(scraper, "PRICE_TIMEOUT_MS", 300)
    with pytest.raises(ScrapeError, match=message):
        with browser.new_context() as context:
            serve(context, fixture)
            fetch_price(context.new_page(), PRODUCT, "EGP")
    assert browser.contexts == []


def test_navigation_timeout(browser, monkeypatch):
    monkeypatch.setattr(scraper, "NAVIGATION_TIMEOUT_MS", 300)
    with browser.new_context() as context:
        def route_request(route):
            if route.request.resource_type == "document":
                route.fulfill(content_type="text/html", body=(
                    FIXTURES / "navigation_timeout.html"
                ).read_text(encoding="utf-8"))
            # Leave the local script pending to prevent DOMContentLoaded.
        context.route("**/*", route_request)
        page = context.new_page()
        with pytest.raises(ScrapeError, match="Navigation timed out") as error:
            fetch_price(page, PRODUCT, "EGP")
        assert isinstance(error.value.__cause__, PlaywrightTimeoutError)
    assert browser.contexts == []


@pytest.mark.parametrize("mode,message", [("http", "HTTP 403"), ("abort", "Navigation failed"), ("selector", "selector")])
def test_browser_errors(browser, mode, message):
    with browser.new_context() as context:
        if mode == "http":
            context.route("**/*", lambda route: route.fulfill(status=403, body="Forbidden"))
        elif mode == "abort":
            context.route("**/*", lambda route: route.abort())
        else:
            serve(context, "normal.html")
        product = Product("Fixture", URL, "[" if mode == "selector" else ".price")
        with pytest.raises(ScrapeError, match=message):
            fetch_price(context.new_page(), product, "EGP")


@pytest.mark.parametrize("names,exit_code", [(["bad", "good"], 1), (["good"], 0)])
def test_cli_local_prices_and_cleanup(browser, monkeypatch, tmp_path, capsys, names, exit_code):
    # Reuse real Chromium while intercepting every request before network access.
    original = browser.new_context
    contexts = []
    def new_context():
        context = original()
        context.route("**/*", lambda route: route.fulfill(
            content_type="text/html", body=(FIXTURES / (
                "malformed.html" if route.request.url.endswith("bad") else "normal.html"
            )).read_text(encoding="utf-8")))
        contexts.append(context)
        return context
    monkeypatch.setattr(browser, "new_context", new_context)
    @contextmanager
    def existing_playwright():
        yield SimpleNamespace(chromium=SimpleNamespace(launch=lambda: browser))
    monkeypatch.setattr(cli, "sync_playwright", existing_playwright)
    monkeypatch.setattr(cli.time, "sleep", lambda seconds: None)
    config = tmp_path / "products.json"
    config.write_text(json.dumps({"currency": "EGP", "products": [
        {"name": name, "url": f"{URL}/{name}", "price_selector": ".price"}
        for name in names
    ]}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["watcher", "--config", str(config), "--no-notify"])
    assert cli.main() == exit_code
    output = capsys.readouterr()
    assert "good: EGP 1234.50" in output.out
    assert f"1 succeeded, {exit_code} failed" in output.out
    if exit_code:
        assert "Invalid price" in output.err
    assert len(contexts) == len(names)
    assert not browser.is_connected()
