# Minimal V1 architecture

Status: simplified V1 approved; M1 and M2 implemented. PROJECT.md defines behavior; TASKS.md defines implementation order.

## Flow and boundaries

Single-run CLI → load/validate config → open SQLite and Chromium → for each product: extract, read previous price, insert observation, attempt notification if lower → close resources and summarize.

Use ordinary synchronous functions and a few dataclasses. Keep scraping, storage, and Telegram requests separate so each can be tested directly. No service hierarchy, generic repositories, protocols, event model, or framework. Keep orchestration in __main__.py until it becomes hard to read.

## Proposed structure

    pyproject.toml
    README.md
    .gitignore
    config/products.example.json
    src/price_drop_watcher/
        __init__.py
        __main__.py       # CLI and straightforward orchestration
        config.py         # Product and Config dataclasses; JSON validation
        prices.py         # pure Decimal parsing
        scraper.py        # Playwright extraction
        storage.py        # SQLite functions
        telegram.py       # plain-text formatting and HTTPS send
    tests/
        fixtures/         # local HTML
        test_config.py
        test_prices.py
        test_scraper.py
        test_storage.py
        test_telegram.py
        test_cli.py
    docs/                 # project, architecture, tasks, handoff
    data/                 # ignored runtime database

Create each file only when needed. Ignore .venv, local product configuration, .env files, databases/sidecars, logs, and caches. Do not modify existing local artifacts unnecessarily.

## Simple configuration and parsing

Example shape: {"currency": "EGP", "products": [{"name": "Example", "url": "https://example.com/product", "price_selector": ".price"}]}.

EGP is the user-selected currency shared by all products and used in fixtures/examples. Confirm one optional displayed currency symbol before real use. No per-product locale/currency settings or currency allowlist registry. Validate nonempty fields, basic three-uppercase-letter currency shape, product field types, HTTP(S) URLs, and duplicate exact URLs. Document that the chosen currency must use two decimal places; code-format validation is not a currency database.

The parser supports comma grouping and dot decimals, strips only the configured code/agreed symbol, and requires one unambiguous positive amount with at most two fractional digits. Validate grouping; reject conflicting markers and extra amounts. Use Decimal and multiply by 100 to get integer minor units without rounding. Add another format only when an actual product needs it.

## Browser extraction

Use synchronous Playwright, one Chromium browser per run, and one page per product. Use fixed, named timeout constants (navigation 30 seconds; price locator 10 seconds). Navigate, wait for the configured CSS locator, require exactly one match, read text, and parse it. Close pages/browser/Playwright with context managers or finally. Use a fixed five-second inter-product delay, replaceable in tests. Report missing/ambiguous prices and navigation failures; do not guess or bypass challenges. There is no universal challenge detector in V1.

## SQLite: one table

Use sqlite3 and a local file. Initialize with CREATE TABLE IF NOT EXISTS. Use parameterized queries, a finite connection timeout, and short write transactions. No network calls inside transactions.

| observations column | Definition |
| --- | --- |
| id | INTEGER PRIMARY KEY |
| product_url | TEXT NOT NULL |
| product_name | TEXT NOT NULL |
| price_minor | INTEGER NOT NULL CHECK(price_minor > 0) |
| currency | TEXT NOT NULL |
| observed_at_utc | TEXT NOT NULL; consistent UTC ISO 8601 |

Add one index on (product_url, currency, id). Fetch the previous observation for the exact URL and currency ordered by id descending. Store each successful observation, even unchanged prices. Names are snapshots, not identity. Changed URLs start new histories; removed products retain rows. No products table, foreign keys, extraction signatures, or schema-version framework. If an incompatible schema is encountered, report it; do not silently delete/recreate data. Handle future changes manually after backup; migration tooling is V2.

## Drop and notification semantics

For each success: fetch previous amount → commit current row → if previous exists and current is lower, send once. The single-user/no-overlap assumption makes separate read and insert operations sufficient. Database failure stops the run. Scrape/send failures are reported per product and other products continue.

Telegram uses standard-library HTTPS, a fixed 15-second timeout, and environment credentials. Format plain text with name, URL, currency, and previous/current price. Check both HTTP success and Telegram ok=true. Report sanitized errors without raw bot-token URLs or credentials. No saved notification status, retry classification, queue, or replay. Saved history survives failed delivery; the alert may be lost. --no-notify uses the same history flow but skips sending and credential requirements.

## Main interfaces (proposed)

Use type hints for public functions; these contracts do not require class abstractions.

| Function | Responsibility |
| --- | --- |
| load_config(path: Path) -> Config | Read and validate JSON; Config contains currency and list[Product]. |
| parse_price(text: str, currency: str) -> int | Return positive integer minor units using the single documented format. |
| fetch_price(page: Page, product: Product, currency: str) -> PriceResult | Navigate, wait, extract, and parse; caller owns browser/page lifecycle. Result contains product_url, price_minor, currency, and aware observed_at_utc. |
| initialize_database(connection: sqlite3.Connection) -> None | Create history table/index if absent. |
| latest_price(connection, url: str, currency: str) -> int or None | Return preceding successful amount. |
| save_price(connection, product: Product, currency: str, price_minor: int, observed_at: datetime) -> None | Insert and commit one observation. |
| send_drop(product: Product, currency: str, previous: int, current: int, token: str, chat_id: str) -> None | Attempt one send; raise a sanitized error on failure. |
| main() -> int | Parse CLI, validate credentials when needed, coordinate, summarize, return 0 or 1. |

Concrete implementation will fully annotate connection parameters and return types. Use ValueError for invalid input and small component-specific errors only where useful; avoid an exception hierarchy. Environment values need not be stored in configuration dataclasses or logs.

## Deterministic testing

- M1: JSON parsing and required-field/type/URL/duplicate validation using temporary files.
- M2: pure parser cases plus actual Chromium against local HTML: valid, delayed, missing, ambiguous, malformed prices. Verify error cleanup. No retailer requests.
- M3: temporary SQLite files; baseline, reopen persistence, unchanged observations, URL/currency separation, and ordering. Check rollback on an insert failure without touching previous rows.
- M4: mock HTTP success, HTTP/API failure, malformed response, timeout, and secret redaction; no real sends.
- M5: local-page/real-database integration with mocked Telegram. Sequence 100 → 90 → 90 → 95 → 92 produces five rows and two send attempts. Test first baseline, scrape failure, failed send with saved history/no replay, no-notify baseline advancement, and nonzero failure status. Replace sleep and clock as needed; no general injection framework.
- M6: manual Windows scheduler verification under the intended account; keep real-service smoke tests separate and explicitly authorized.

## V2 boundary

Queues/retries, delivery records, migrations, identity synchronization, multi-currency/locale parsing, application locking, and richer abstractions are postponed. See PROJECT.md for the complete V2 list. V1 accepts missed alerts and assumes no overlapping runs in exchange for a smaller system.
