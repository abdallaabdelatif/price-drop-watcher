# AGENTS.md

## Project

Price Drop Watcher is a Python application that uses Playwright to visit product pages, extract prices, store price history in SQLite, and send Telegram notifications when prices drop.

## Technology

- Python 3
- Playwright for browser automation
- SQLite for persistence
- Telegram Bot API for notifications
- pytest for testing
- Git for version control

## Engineering Principles

- Prefer simple, maintainable solutions.
- Use small modules with clear responsibilities.
- Avoid unnecessary dependencies and abstractions.
- Use type hints for public functions.
- Use integer minor currency units or Decimal for monetary values.
- Handle expected failures explicitly.
- Do not silently ignore errors.

## Agent Workflow

1. Inspect only files relevant to the current task.
2. For nontrivial changes, provide a short implementation plan.
3. Keep changes within the agreed task scope.
4. Implement the smallest complete solution.
5. Run relevant tests.
6. Review the diff for unrelated changes.
7. Summarize changes, tests, and remaining issues.

## Browser Automation

- Use Playwright for product page navigation.
- Prefer robust locators over brittle selectors.
- Use explicit timeouts and appropriate waits.
- Close browser resources after use.
- Do not attempt to bypass CAPTCHAs, access controls, or anti-bot protections.
- Respect website terms and reasonable request rates.
- Do not assume every website has the same price structure.

## Database

- Use SQLite.
- Store product identity, price, currency, and observation timestamp.
- Use parameterized SQL queries.
- Keep database access separate from scraping logic.

## Security

- Never hardcode API tokens or credentials.
- Load secrets from environment variables.
- Never commit .env files or local databases.
- Do not print secrets in logs.
- Ask before destructive operations or external deployments.

## Testing

- Use pytest.
- Prefer deterministic tests using local HTML fixtures.
- Do not require live shopping websites for unit tests.
- Mock Telegram requests during automated tests.
- Add regression tests when fixing bugs.

## Completion Criteria

A task is complete only when:

- Its acceptance criteria are satisfied.
- Relevant tests pass.
- No unrelated files were changed.
- Any remaining limitations are documented.

## Documentation

- Read docs/PROJECT.md when requirements are relevant.
- Read docs/ARCHITECTURE.md when changing component boundaries.
- Use docs/TASKS.md to track milestone progress.
- Update docs/HANDOFF.md at meaningful session boundaries.
