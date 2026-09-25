# ── Stage 1: base image ──────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production image ─────────────────────────────────────────────────
FROM base AS production

COPY . .

# Remove .env from the container (inject via docker run -e or secrets)
RUN rm -f .env

EXPOSE 5000

ENV FLASK_ENV=production

CMD ["python", "run.py"]
