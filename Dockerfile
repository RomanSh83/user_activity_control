# Этап сборки (собираем билдер (ставим зависимости, .venv))
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends make
WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

# Переменные для корректного вывода логов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
