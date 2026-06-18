FROM python:3.11-slim

# Python and pip settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Set the working directory
WORKDIR /app

# Install required Linux packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements before installing packages
# This allows Docker to find requirements.txt
COPY requirements.txt /app/requirements.txt

# Install CPU-only PyTorch first,
# then install the project's remaining dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch && \
    python -m pip install --no-cache-dir \
        -r /app/requirements.txt && \
    python -m pip install --no-cache-dir \
        psutil \
        sentence-transformers \
        scikit-learn \
        transformers

COPY . /app/

# Fix Windows line endings and permissions
RUN sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]