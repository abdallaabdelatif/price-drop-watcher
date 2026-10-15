# Session handoff

Updated: 2026-10-15.

## Current milestone

Simplified V1 approved; M1 complete. User selected EGP. M2 through M6 are not started.

## Completed work

Added src-layout package metadata, Product/Config dataclasses, JSON validation, EGP example configuration, ignore rules, Git Bash setup instructions, and configuration tests. Planning documents reflect approval and EGP. Existing virtual environment preserved. No commits made; project files remain untracked.

## Important architectural decisions

Use Python 3.11+, synchronous Playwright, SQLite, Telegram, and Windows Task Scheduler. Prefer small functions and standard-library dependencies.

One watchlist currency (EGP); products contain name, exact URL, and CSS price selector. Validate currency-code shape without a registry. Planned parsing uses comma grouping, dot decimals, Decimal, and integer minor units with two decimal places.

One observations table; exact URL/currency identifies history. First observation establishes a baseline. Save every successful observation before one Telegram attempt per drop. Failed sends and --no-notify advance history without replay, so alerts can be lost.

Task Scheduler prevents scheduled overlap; avoid concurrent manual runs. Retries, queues, migrations, multiple locales/currencies, and application locks are deferred to V2. Secrets belong in environment variables.

## Relevant files

- AGENTS.md: workflow and safeguards.
- docs/PROJECT.md, docs/ARCHITECTURE.md, docs/TASKS.md: requirements, design, acceptance criteria.
- src/price_drop_watcher/config.py and tests/test_config.py: M1 implementation/tests.
- pyproject.toml, README.md, .gitignore, config/products.example.json: setup/configuration.
- Generated *.egg-info files are ignored build metadata; edit pyproject.toml instead.

## Tests and their results

Existing .venv: Python 3.12.6. Editable dev installation and package import succeeded. Latest pytest run: 73 passed, one cache permission warning. Initial sandbox run could not access temporary-file fixtures; authorized rerun passed. Dependency download required network approval. Ignore checks passed. No live-site requests, browser installation, scheduling, or Telegram sends occurred. Tests were not rerun for this documentation update.

## Known issues and blockers

Real product URL, displayed EGP symbol, selector, and price meaning remain unspecified; example values are placeholders. These do not block local-fixture development. No CLI, scraper, persistence, or notification implementation exists yet.

## Next recommended task

M2: price parser, synchronous Playwright extraction with cleanup/timeouts, local Chromium fixtures, and minimal --no-notify CLI without persistence/credentials. Follow TASKS.md acceptance criteria. Real-page checks require separate authorization.
