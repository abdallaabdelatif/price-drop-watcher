# Price Drop Watcher — V1 plan

Status: simplified V1 approved. M1 bootstrap/configuration and M2 extraction are implemented; later milestones remain planned.

## Purpose and scope

Build a small personal price watcher while learning agentic AI development with Codex. Favor short, understandable increments over platform infrastructure. Keep Python, synchronous Playwright, SQLite, Telegram, and Windows Task Scheduler.

One invocation reads a JSON watchlist, visits products sequentially, records successful prices, sends a Telegram message on a drop, and exits. Schedule it every four hours using Windows Task Scheduler. Start with one real product, then add a second through configuration.

## Minimal behavior

- Configuration is a JSON object containing one currency and a products list. Each product needs only name, url, and price_selector. Remove a product from the list to stop checking it. Reject missing/empty fields, wrong types, duplicate URLs, and non-HTTP(S) URLs with useful errors. No schema library, stable keys, enabled flags, or identity synchronization.
- Use EGP, selected by the user, as the single watchlist currency and in fixtures/examples. Support two decimal places only. Accept ordinary digits with comma thousands separators and a dot decimal separator, optionally surrounded by the configured currency code or one agreed symbol. Reject ambiguous amounts, invalid grouping, excess precision, nonpositive prices, and conflicting currency markers. Other formats need a deliberate later change, not configurable locale machinery.
- Parse with Decimal and store integer minor units. A CSS selector must identify exactly one current item price for a fixed variant. No guessing between list prices, installments, or discounts.
- Use the exact configured URL as product identity. Compare against its last successful observation in the configured currency. First check establishes a baseline; strictly lower prices notify. Equal/higher prices do not. Example: 100 → 90 → 90 → 95 → 92 yields two drop attempts.
- Store every successful check, including unchanged prices, with URL, name, integer price, currency, and UTC timestamp. Failed extraction creates no row. A changed URL starts fresh history; old rows remain. If selector/variant meaning changes under the same URL, the user must choose a separate database to start a new baseline. V1 does not detect such changes.
- Read previous price, save the new observation, then attempt Telegram delivery once for a drop. No notification queue or automatic retries. A failed send is reported, but the saved price remains the next baseline. A crash between save and send, or a delivery failure followed by an unchanged price, can lose an alert. Do not promise exactly-once or eventual delivery.
- Read TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment variables when notifications are enabled. Never commit or log secrets. A simple --no-notify option allows local checks; it still saves history and advances the baseline, so suppressed alerts are not replayed.
- Use finite browser/HTTP/database timeouts and a fixed conservative five-second delay between products. Close resources on all paths. Report individual scrape/send failures and continue; stop on invalid configuration or database failure. Exit 0 on success and 1 on any failure; print a short summary.

## Development and operation

Use Python 3.11+ as the proposed baseline, subject to checking the existing .venv. Dependencies: Playwright and pytest; use standard-library JSON, sqlite3, urllib, argparse, and logging. Small functions and type hints are sufficient; no framework, ORM, plugin system, or dependency-injection infrastructure.

Develop in Git Bash; activate with source .venv/Scripts/activate or invoke .venv/Scripts/python.exe directly. Document installation and Chromium setup during M1/M2. Proposed command: python -m price_drop_watcher --config config/products.json --database data/prices.sqlite3. Relative paths use the invocation working directory.

Task Scheduler launches the virtualenv interpreter directly with absolute paths and an explicit working directory. Set it not to start another instance while running. Do not run manual checks concurrently with a scheduled check; V1 has no application lock. Ensure the scheduled account has the browser and environment credentials; interactive shell exports are insufficient. A sleeping/offline machine misses checks.

## Tests and completion

Use pytest with pure parsing/config tests, local HTML Playwright fixtures, temporary SQLite files, and mocked Telegram HTTP. No automated shopping-site requests or real messages. Each milestone in TASKS.md has its own test boundary. V1 is complete when offline end-to-end checks pass and the manual Git Bash/scheduling runbook is verified, with real-service checks separately authorized and recorded.

## Assumptions and limitations

The first URL, displayed EGP symbol, and intended price element still need confirmation before real-site use; basic work can proceed with fixtures. Price means the selected item price, excluding shipping/tax unless already included. Sites can change layouts or block automation; stop and report challenges without bypassing CAPTCHA/access controls. Respect site terms and reasonable rates. Fixture tests do not prove retailer compatibility. Keep the local database and secrets out of Git; M1 provides ignore rules for local artifacts.

## Postponed until V2 (only if needed)

Durable notification queues, delivery retries/status tracking, schema migration tooling, product tables/identity synchronization, multiple currencies/locales or minor-unit scales, application locks, configurable timeout/rate policies, advanced alert rules, retention, dashboards, cloud hosting, concurrency, multiple users/chats, additional channels, and generalized extraction adapters. A built-in scheduler is unnecessary while Task Scheduler suffices. Authentication, automatic selector repair, and AI extraction are outside V1; access-control evasion is never a feature.
