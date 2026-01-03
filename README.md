[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Build & Push Multi-Arch Docker Image](https://github.com/alexNMD/NMDownloader_bot/actions/workflows/build-and-deploy.yml/badge.svg?branch=main)](https://github.com/alexNMD/NMDownloader_bot/actions/workflows/build-and-deploy.yml)

## ✅ Prerequisites

- Python 3.14
- [uv](https://github.com/astral-sh/uv)

## Friendly reminder...

### Install as dev
```
uv sync --group dev
```

### Pre Commit Hook
```
uv run pre-commit install
```

### Start the debug flask app
```
uv run -- flask --app nmdownloader.apps.flask_app run --debug
```

### Start the celery app
```
uv run -- celery --app nmdownloader.apps.celery_app worker
```

### Code Quality
```
uv run ruff check .
uv run ruff format .
```

### Typing Check
```
uv run mypy .
```

## Dotenv Example
- DISCORD_TOKEN
- DISCORD_ADMINS
- DISCORD_DEFAULT_CHANNEL_ID
- DOWNLOAD_UN_FICHIER_TOKEN
