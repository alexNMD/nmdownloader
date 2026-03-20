[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Build & Push Multi-Arch Docker Image](https://github.com/alexNMD/nmdownloader/actions/workflows/build.yml/badge.svg)](https://github.com/alexNMD/nmdownloader/actions/workflows/build.yml)

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

### Docker
```shell
# Build
docker compose -f compose-dev.yaml build

# Start
docker compose -f compose-dev.yaml up
```
