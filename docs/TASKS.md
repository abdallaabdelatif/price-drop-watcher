# Development milestones — simplified V1

Status: simplified V1 approved. M1 and M2 complete; validation results recorded below. M3 through M6 are not started.

## P0 — Planning revision

- [x] Inspect original plan for unnecessary complexity.
- [x] Replace it with a minimal personal-tool design.
- [x] User reviews this simplified revision.

Acceptance: PROJECT.md, ARCHITECTURE.md, and TASKS.md agree on configuration, one-table history, one-attempt delivery, ordering, and V2 scope. No application code added.

## M1 — Small bootstrap and configuration

Depends on revised P0 approval.

- [x] Check existing .venv; establish package metadata, pytest, Git Bash instructions, and ignore rules.
- [x] Add small Product/Config dataclasses, basic JSON validation, and nonsecret example.
- [x] Use one watchlist currency; EGP selected by the user and used in fixtures/examples. No currency registry, locale options, product keys, or environment abstraction.

Acceptance: package imports and pytest runs using .venv. Tests pass for valid JSON, missing/empty fields, invalid types/currency-code shape, invalid HTTP(S) URLs, and duplicate URLs. No browser, database, or Telegram needed. Local environments/secrets/databases are ignored before commits.

Validation (2026-10-15): Python 3.12.6 in the existing .venv; editable install and package import succeeded. Configuration suite: 73 passed. The sandbox blocked temporary-file fixtures on the initial run; an authorized rerun passed with one pytest cache permission warning. Ignore rules verified for environments, secrets, local configuration, databases/sidecars, and logs; the example remains visible to Git.

## M2 — Extract a price with Playwright

Depends on M1. This is the first functional slice, before persistence.

- [x] Add Decimal-to-minor-unit parsing for one documented format.
- [x] Add synchronous Playwright extraction with explicit waits/timeouts and resource cleanup.
- [x] Provide a minimal --no-notify CLI check that prints extracted prices; database recording is added in M3.

Validation (2026-10-16): complete suite `python -m pytest -q --tb=short`: 113 passed in 10.20 seconds, one existing pytest cache permission warning. Actual Chromium tests route every browser request to local HTML fixtures and cover normal/delayed, missing/multiple/malformed prices, navigation timeout, HTTP/network failure, invalid selectors, and CLI success/failure continuation and cleanup. No shopping-site requests, SQLite, or Telegram. Playwright and Chromium installed with authorization. Initial sandbox run hit temporary-file permissions; an early browser run preceded completion of the browser download. The final authorized run passed after installation. Currency symbols remain deferred until one is agreed.

Acceptance: pure parser tests cover valid grouping/decimals/currency marker, malformed grouping, ambiguous amounts, excess precision, and nonpositive values. Actual Chromium tests use local HTML for normal/delayed prices and missing/multiple selectors. The CLI can demonstrate extraction without credentials or a database. Optional real-page review requires a supplied URL/currency/selector and separate authorization; it is not an automated-test dependency.

## M3 — SQLite history and price comparisons

Depends on M2.

- [ ] Create the single observations table and lookup index.
- [ ] Add latest-price lookup and committed insertion of every successful observation.
- [ ] Compare current price with the previous successful value for exact URL/currency; print a drop indication for now.

Acceptance: temporary-file tests prove persistence after reopen, baseline handling, unchanged rows, URL/currency separation, ordering, and insert-failure rollback. Sequence 100 → 90 → 90 → 95 → 92 stores five rows and indicates two drops. Failed extraction adds no row. No queue, product synchronization, or migration tooling.

## M4 — Telegram sends

Depends on M3.

- [ ] Add plain-text formatting and one timeout-bound HTTPS send per detected drop.
- [ ] Read credentials from environment when notifications are enabled; retain --no-notify.
- [ ] Report send errors without secrets; keep the saved history and do not retry/replay.

Acceptance: mocked HTTP tests cover success, HTTP/API failures, malformed responses, timeout, message amounts, and redaction. Missing credentials fail before a notification-enabled run starts scraping. No-notify needs no credentials. No real Telegram messages in tests. Document that failed/suppressed sends may be lost permanently.

## M5 — Complete single-run integration

Depends on M4.

- [ ] Finish sequential CLI orchestration, fixed inter-product delay, resource cleanup, summary, and exit 0/1 behavior.
- [ ] Isolate scraping/sending errors per product; stop on configuration/database failure.

Acceptance: offline integration with local HTML, actual Playwright/SQLite, and mocked Telegram verifies baseline → drop → unchanged behavior across runs. The five-price sequence produces five rows and two sends. Test scrape recovery, one product failing while another succeeds, database failure, no-notify history advancement, and failed send followed by unchanged price with no retry. Replace waits for fast tests; avoid infrastructure abstractions.

## M6 — Windows Task Scheduler and personal-use check

Depends on M5; task registration and live sends require explicit authorization.

- [ ] Document Git Bash manual commands and Task Scheduler setup using absolute .venv interpreter/config/database paths and working directory.
- [ ] Set four-hour repetition and do-not-start-another-instance; document avoiding concurrent manual runs.
- [ ] Verify browser/credentials under the scheduled account. Document simple diagnostics and backing up the database while stopped.
- [ ] Confirm first real product/currency/price meaning and record authorized smoke-check outcomes.

Acceptance: manual and scheduled local-fixture runs use the same configuration/history; inspect repetition and overlap settings without waiting four hours. Record one authorized real-page extraction and Telegram send separately from automated tests. Note machine-sleep and failed-delivery limitations. No application lock or always-running scheduler.

## V2 — intentionally postponed

Durable queues, retries/delivery status, migration framework, product identity synchronization, multiple currencies/locales/scales, application locks, configurable operational policies, advanced alert rules, retention, UI/cloud/concurrency/multi-user features, and generalized adapters. Add these only when personal usage demonstrates a need; they are not V1 acceptance requirements.

## Completion discipline

For each milestone, run relevant pytest checks, review the diff, record results here, and update HANDOFF.md at meaningful boundaries. Add regression tests for actual bugs. Use local fixtures and mock Telegram; do not require live sites for tests. Record runtime test outcomes for each implemented milestone.
