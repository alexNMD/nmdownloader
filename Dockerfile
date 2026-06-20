FROM python:3.14-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
      p7zip-full=16.02+transitional.1* \
      unrar-free=1:0.3.1-1* \
      cabextract=1.11-2* \
      ffmpeg=7:7.1.4-0+deb13u1* \
    && rm -rf /var/lib/apt/lists/ \
    && pip install --no-cache-dir "uv[rust]==0.7.19"

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY src/ src/

RUN uv sync --locked
