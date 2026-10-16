# Session handoff

Updated: 2026-10-16.

## Current milestone

M1 and M2 complete; M3 through M6 not started. Simplified V1 approved; watchlist currency is EGP.

## Completed work

M1: package setup, Product/Config dataclasses, JSON validation, example configuration, ignore rules, and setup documentation.

M2: strict Decimal parsing, synchronous Playwright scraping, structured PriceResult (exact URL, integer minor units, currency, aware UTC timestamp), and extraction-only CLI requiring --no-notify. Expected product failures are reported while remaining products continue. SQLite and Telegram are not implemented. Changes remain uncommitted.

## Important architectural decisions

Use Python 3.11+, synchronous Playwright, SQLite, Telegram, and Windows Task Scheduler; keep modules small. Playwright is the only new direct dependency; install Chromium separately.

Accept comma grouping, dot decimals, at most two fractional digits, and an optional configured currency code. Reject ambiguous/nonpositive prices. Require exactly one visible CSS price match. Navigation/price timeouts are 30/10 seconds. The caller owns pages; CLI closes browser resources and pauses five seconds between products.

Planned storage uses one observations table keyed for lookup by exact URL/currency. First success establishes baseline; save every success before attempting one notification for a strictly lower price. Failed/suppressed notifications are not replayed. Queues, retries, migrations, multiple locales, and application locks are deferred.

## Relevant files

- AGENTS.md; docs/PROJECT.md, ARCHITECTURE.md, TASKS.md: instructions and acceptance criteria.
- src/price_drop_watcher/{config,prices,scraper,__main__}.py: implementation.
- tests/test_{config,prices,scraper}.py; tests/fixtures/: deterministic tests.
- README.md, pyproject.toml, config/products.example.json, .gitignore: setup/configuration.

## Tests and their results

Python 3.12.6; Playwright 1.64.0 and Chromium installed. Latest full suite: 113 passed (73 configuration, 29 parser, 11 Chromium/CLI), one pytest cache permission warning. Browser requests use local routed HTML only. Sandbox temporary-file restrictions required an authorized test run. Tests were not rerun for this documentation-only update.

## Known issues and blockers

Real URL, selector, EGP symbol, and intended price meaning remain unspecified; these do not block M3. Symbols and other number formats are unsupported. Fixtures do not establish retailer compatibility. No CAPTCHA bypass or selector repair. Real-page checks require separate authorization.

## Next recommended task

Implement M3 SQLite observations, latest-price lookup, committed insertion, and drop comparisons per TASKS.md. Test persistence, unchanged prices, URL/currency separation, ordering, and rollback. Leave Telegram for M4.
