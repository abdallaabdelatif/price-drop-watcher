import json
from pathlib import Path

import pytest

from price_drop_watcher.config import Config, Product, load_config


@pytest.fixture
def watchlist():
    return {
        "currency": "EGP",
        "products": [
            {
                "name": "Example",
                "url": "https://example.com/item",
                "price_selector": ".price",
            }
        ],
    }


def write_config(tmp_path, value):
    path = tmp_path / "products.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_valid_config(tmp_path, watchlist):
    watchlist["products"].append(
        {
            "name": "Second",
            "url": "http://example.com/other",
            "price_selector": "#price",
        }
    )
    assert load_config(write_config(tmp_path, watchlist)) == Config(
        currency="EGP",
        products=[Product(**entry) for entry in watchlist["products"]],
    )


def test_example_config():
    path = Path(__file__).resolve().parents[1] / "config/products.example.json"
    assert load_config(path).currency == "EGP"


@pytest.mark.parametrize("value", [None, [], "text", 42, True])
def test_invalid_root(tmp_path, value):
    with pytest.raises(ValueError, match="JSON object"):
        load_config(write_config(tmp_path, value))


@pytest.mark.parametrize("field", ["currency", "products"])
def test_missing_root_fields(tmp_path, watchlist, field):
    del watchlist[field]
    with pytest.raises(ValueError, match=field):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize(
    "value",
    [None, True, 123, [], {}, "", " ", "egp", "EG", "EGPP", "E1P", "ÉGP", " EGP"],
)
def test_invalid_currency(tmp_path, watchlist, value):
    watchlist["currency"] = value
    with pytest.raises(ValueError, match="currency"):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize("value", [None, True, 123, {}, "products", []])
def test_invalid_products(tmp_path, watchlist, value):
    watchlist["products"] = value
    with pytest.raises(ValueError, match="products"):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize("value", [None, [], "product", 123, True])
def test_invalid_product_entry(tmp_path, watchlist, value):
    watchlist["products"] = [value]
    with pytest.raises(ValueError, match=r"products\[0\]"):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize("field", ["name", "url", "price_selector"])
def test_missing_product_fields(tmp_path, watchlist, field):
    del watchlist["products"][0][field]
    with pytest.raises(ValueError, match=field):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize("field", ["name", "url", "price_selector"])
@pytest.mark.parametrize("value", [None, True, 123, [], {}, "", " \t"])
def test_invalid_product_fields(tmp_path, watchlist, field, value):
    watchlist["products"][0][field] = value
    with pytest.raises(ValueError, match=field):
        load_config(write_config(tmp_path, watchlist))


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/item",
        "/item",
        "example.com",
        "https:///item",
        "https://",
        "https://example.com/a b",
        "https://example.com/\nitem",
        "https://[invalid",
        "https://example.com:bad/item",
        "https://example.com:99999/item",
        "https://user:secret@example.com/item",
    ],
)
def test_invalid_url(tmp_path, watchlist, url):
    watchlist["products"][0]["url"] = url
    with pytest.raises(ValueError, match="HTTP"):
        load_config(write_config(tmp_path, watchlist))


def test_duplicate_url(tmp_path, watchlist):
    watchlist["products"].append({**watchlist["products"][0], "name": "Different name"})
    with pytest.raises(ValueError, match="duplicates"):
        load_config(write_config(tmp_path, watchlist))


def test_exact_url_identity(tmp_path, watchlist):
    watchlist["products"].append(
        {**watchlist["products"][0], "url": "https://example.com/item?variant=2"}
    )
    assert len(load_config(write_config(tmp_path, watchlist)).products) == 2


@pytest.mark.parametrize("content", [b"{", b"\xff"])
def test_invalid_json(tmp_path, content):
    path = tmp_path / "products.json"
    path.write_bytes(content)
    with pytest.raises(ValueError, match="valid UTF-8 JSON"):
        load_config(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.json")
