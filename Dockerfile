FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY aeronavx/ ./aeronavx/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[api]"

ENV AERONAVX_CACHE=/data/aeronavx

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "aeronavx.api.server"]
