[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![Tests](https://github.com/alexNMD/nmdownloader/actions/workflows/tests.yml/badge.svg)](https://github.com/alexNMD/nmdownloader/actions/workflows/tests.yml)

## ✅ Prerequisites

- Python >=3.11
- [uv](https://github.com/astral-sh/uv)
- [direnv](https://direnv.net)

## Friendly reminder...

### Install as dev
```shell
direnv allow
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
uv run gunicorn --config src/apps/flask_app/gunicorn.conf.py apps.flask_app:flask_app --reload
```

### Start the celery app
```shell
uv run -- celery --app apps.celery_app worker --loglevel=info
```

### Start the discord app
```shell
uv run -- python -m apps.discord_app.runners
```

### Code Quality
```shell
uv run ruff check
uv run ruff format
```

### Typing Check
```shell
uv run ty check
```

### Testing (with coverage)
```shell
uv run pytest --cov
```
