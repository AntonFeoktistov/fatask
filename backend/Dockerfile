# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1

# Копируем pyproject.toml и uv.lock (они в backend/)
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Копируем весь код (main.py, api/, core/, ...)
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim

# Создаём non-root пользователя
RUN useradd -m -u 1000 appuser

WORKDIR /app/backend

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app/backend

# Даём права на /app пользователю appuser
RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]