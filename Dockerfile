FROM python:3.14-slim

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
      p7zip-full \
      unrar-free \
      cabextract \
      ffmpeg \
    && rm -rf /var/lib/apt/lists/ \
    && pip install --no-cache-dir "uv[rust]==0.7.19"

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY src/ src/

RUN uv sync --locked
