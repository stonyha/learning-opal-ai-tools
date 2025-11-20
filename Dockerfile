# syntax=docker/dockerfile:1

FROM python:3.13.7-bookworm

RUN mkdir -p /root/.local/share/webtech

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    gnupg \
    git \
    cmake \
    pkg-config \
    python3-dev \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy minimal requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with error handling
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install minimal essential dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code 
# Note: .dockerignore excludes: frontend/, .venv/, __pycache__/, .chainlit/, .files/, *.db
COPY . .

# Expose port
EXPOSE 50505

# Default command: start both web and worker via your script
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:50505", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120"]