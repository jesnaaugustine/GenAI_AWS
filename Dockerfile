FROM python:3.12-slim

# Prevent Python from creating .pyc files
# and make logs appear immediately in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies into the system environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY app ./app

# Application listens on 8000
EXPOSE 8000

# Start FastAPI application
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]