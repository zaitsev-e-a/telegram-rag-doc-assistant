FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    ca-certificates \
    redis-server \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/qdrant.tar.gz https://github.com/qdrant/qdrant/releases/download/v1.13.2/qdrant-x86_64-unknown-linux-gnu.tar.gz && \
    tar -xzf /tmp/qdrant.tar.gz -C /tmp && \
    mv /tmp/qdrant /usr/local/bin/qdrant && \
    chmod +x /usr/local/bin/qdrant && \
    rm -f /tmp/qdrant.tar.gz

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip==24.0 && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/data/tmp
RUN mkdir -p /qdrant/storage
RUN chmod +x /app/entrypoint.sh

EXPOSE 7860
EXPOSE 6333
EXPOSE 6379

CMD ["bash", "/app/entrypoint.sh"]