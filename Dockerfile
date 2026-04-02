# ──────────────────────────────────────────────────────────────────────────────
# easyResearch Big Data — Dockerfile
# Supports CUDA 12.6 (GPU) or CPU-only mode
# ──────────────────────────────────────────────────────────────────────────────

# Base: Python 3.11 with CUDA 12.6 (devel for torch compatibility)
# Use nvidia/cuda image for GPU support; switch to python:3.11-slim for CPU-only.
ARG BASE_IMAGE=pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime
FROM ${BASE_IMAGE}

# Metadata
LABEL maintainer="easyResearch"
LABEL description="Production-Grade RAG System with Big Data Pipeline"
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
# PyTorch already included in base image (pytorch/pytorch).
# We install everything else from requirements.txt, skipping torch/torchvision/torchaudio
# to avoid re-downloading the large CUDA wheels unnecessarily.
RUN pip install --upgrade pip && \
    grep -v -E "^(torch|torchvision|torchaudio|--extra-index-url)" requirements.txt \
    | pip install -r /dev/stdin

# Copy application source code
COPY . .

# Create necessary directories
RUN mkdir -p \
    uploads \
    database/chat_history \
    database/summaries \
    logs

# Expose ports
# 8501 = Streamlit UI
# 8000 = FastAPI Backend
EXPOSE 8501 8000

# Default command (override in docker-compose)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
