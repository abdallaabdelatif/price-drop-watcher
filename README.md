# Price Drop Watcher

A personal Python price watcher. M1 provides package setup and JSON configuration;
browser extraction, history, notifications, and the CLI arrive in later milestones.

## Setup (Windows, Git Bash)

Use Python 3.11 or newer. From the project directory:

```bash
python -m venv .venv  # only if the environment does not already exist
source .venv/Scripts/activate
python -m pip install -e '.[dev]'
python -m pytest
```

Without activation, use `.venv/Scripts/python.exe` instead of `python`.
Playwright and Chromium setup will be added in M2.

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
