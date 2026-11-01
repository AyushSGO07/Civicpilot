# ==============================================================================
# CivicPilot Backend Dockerfile
# Base image includes Python 3 and all Playwright Chromium system dependencies
# ==============================================================================
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Playwright Chromium binary is provisioned
RUN playwright install chromium

# Copy application source
COPY . /app

# Create storage directory for PDF receipts
RUN mkdir -p storage/receipts

# Environment configuration
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_HEADLESS=true

EXPOSE 8000

# Launch FastAPI ASGI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
