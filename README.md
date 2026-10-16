# Price Drop Watcher

A personal Python price watcher. M2 provides configuration, strict price parsing,
Playwright extraction, and an extraction-only CLI. History and notifications come later.

## Setup (Windows, Git Bash)

Use Python 3.11 or newer. From the project directory:

```bash
python -m venv .venv  # only if the environment does not already exist
source .venv/Scripts/activate
python -m pip install -e '.[dev]'
python -m playwright install chromium
python -m pytest
```

Without activation, use `.venv/Scripts/python.exe` instead of `python`.
Playwright is the browser automation dependency; Chromium is installed separately
for the account that runs the watcher.

## Configuration

Copy `config/products.example.json` to `config/products.json` and edit it.
Local JSON configurations are ignored by Git; the example remains tracked.
The example uses the selected watchlist currency, **EGP**, with two decimal places.
The displayed symbol and actual price element will be confirmed with the first real product.

Each product requires nonempty string fields `name`, `url`, and `price_selector`.
URLs must use HTTP(S), contain a hostname, have no embedded credentials or whitespace,
and be unique as exact strings. `products` must be a nonempty list.
`currency` must be three uppercase ASCII letters; this checks shape, not a currency registry.
One currency applies to the entire watchlist and must use two decimal places.

You can load the configuration from Python:

```python
from pathlib import Path
from price_drop_watcher.config import load_config

config = load_config(Path("config/products.json"))
```

Invalid configuration raises `ValueError`; file access errors raise `OSError`.
Paths are relative to the current working directory. The example URL is a placeholder.
Never put Telegram credentials in configuration; later notification support will read
them from environment variables.

## Extract prices (M2)

```bash
python -m price_drop_watcher --config config/products.json --no-notify
```

This prints prices and a summary without credentials or database access. It returns
0 on success and 1 on configuration, browser, or product failures. Failed products
are reported and subsequent products continue, with five seconds between products.
Use only URLs you are authorized to access and respect site terms.

The CSS selector must match exactly one visible current-price element. Navigation
has a 30-second timeout; the price wait has a 10-second timeout. Pages, contexts,
the browser, and Playwright are closed on success and failure.

Supported text uses ASCII digits, optional comma thousands grouping, a dot with
at most two decimal places, and optionally the configured currency code at either
end (for example `EGP 1,234.50`). Prices must be positive. Symbols, other locales,
multiple amounts, and conflicting markers are rejected. No symbol is agreed yet.
Parsing uses Decimal and returns integer minor units without rounding.

`fetch_price(page, product, currency)` in `scraper.py` returns a frozen `PriceResult`
with the exact product URL, integer price, currency, and aware UTC observation time.
The caller owns the page/browser lifecycle; extraction failures raise `ScrapeError`.

Tests route all browser requests to local HTML fixtures; no shopping sites are
contacted. Fixture coverage does not prove retailer compatibility. There is no
CAPTCHA detection/bypass or automatic selector repair.
