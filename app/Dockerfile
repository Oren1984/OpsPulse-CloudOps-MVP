# syntax=docker/dockerfile:1.7
FROM python:3.12.8-slim-bookworm AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==25.0.1 \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.12.8-slim-bookworm AS runtime

# Pull latest Debian security patches on top of the pinned base image.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 opspulse \
    && useradd --uid 10001 --gid opspulse --shell /usr/sbin/nologin --no-create-home opspulse

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY opspulse ./opspulse
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
COPY docker-entrypoint.sh ./docker-entrypoint.sh

RUN chown -R opspulse:opspulse /app \
    && chmod +x /app/docker-entrypoint.sh

USER opspulse
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3).status==200 else 1)"]

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "opspulse.main:app", "--host", "0.0.0.0", "--port", "8000"]
