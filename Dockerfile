FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md uv.lock ./
COPY src ./src

RUN pip install .

ENTRYPOINT ["gemini-embedding-2-mcp"]
