[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Build & Push Multi-Arch Docker Image](https://github.com/alexNMD/NMDownloader_bot/actions/workflows/build-and-deploy.yml/badge.svg?branch=main)](https://github.com/alexNMD/NMDownloader_bot/actions/workflows/build-and-deploy.yml)

## ✅ Prerequisites

- Python >=3.11
- [uv](https://github.com/astral-sh/uv)

## Friendly reminder...

### Install as dev
```shell
uv sync --group dev
```

### Dump dependencies version (uv.lock)
```shell
uv sync --upgrade
```

### Pre Commit Hook
```shell
uv run pre-commit install
```

### Start the debug flask app
```shell
uv run -- flask --app nmdownloader.apps.flask_app run --debug
```

### Start the celery app
```shell
uv run -- celery --app nmdownloader.apps.celery_app worker
```

### Start the discord app
```shell
uv run -- python -m nmdownloader.apps.discord_app
```

### Code Quality
```shell
uv run ruff check .
uv run ruff format .
```

### Typing Check
```shell
uv run mypy .
```

## Dotenv Example
| Variable                   | Explanation                                                                                                                            |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| DISCORD_TOKEN              | The bot authentication token from Discord Developer Portal. Required to connect and authenticate your bot with Discord's API.          |
| DISCORD_ADMINS             | JSON style list of Discord user IDs who have administrator privileges for bot commands and settings. Example: '["user1","user2#0000"]' |
| DISCORD_DEFAULT_CHANNEL_ID | The default Discord channel ID where the bot will send messages or notifications if no specific channel is specified.                  |
| DOWNLOAD_UN_FICHIER_TOKEN  | Authentication token for the file download service API. Used to authorize and authenticate requests to download files.                 |
