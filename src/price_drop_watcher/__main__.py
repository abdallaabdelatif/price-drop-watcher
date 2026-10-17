"""M2 extraction-only command; persistence and notifications come later."""

import argparse
from pathlib import Path
import sys
import time

from playwright.sync_api import Error, sync_playwright

from price_drop_watcher.config import load_config
from price_drop_watcher.scraper import ScrapeError, fetch_price

INTER_PRODUCT_DELAY_SECONDS = 5


def main() -> int:
    """Print successful prices and return one if any check fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/products.json"))
    parser.add_argument(
        "--no-notify",
        action="store_true",
        required=True,
        help="Required during M2; extract without storing or notifying",
    )
    args = parser.parse_args()
    try:
        config = load_config(args.config)
    except (OSError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    succeeded = failed = 0
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            try:
                for index, product in enumerate(config.products):
                    if index:
                        time.sleep(INTER_PRODUCT_DELAY_SECONDS)
                    try:
                        with browser.new_context() as context:
                            result = fetch_price(
                                context.new_page(), product, config.currency
                            )
                        major, fraction = divmod(result.price_minor, 100)
                        print(
                            f"{product.name}: {result.currency} {major}.{fraction:02d}"
                        )
                        succeeded += 1
                    except (ScrapeError, Error) as exc:
                        print(f"{product.name}: {exc}", file=sys.stderr)
                        failed += 1
            finally:
                browser.close()
    except Error:
        print(
            "Browser failed; verify Playwright Chromium installation", file=sys.stderr
        )
        return 1
    print(f"Checked {succeeded + failed}: {succeeded} succeeded, {failed} failed")
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
