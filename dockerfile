FROM python:3.11-slim

RUN apt update && apt install -y --no-install-recommends \
    curl wget \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY . .

RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r requirements.txt --no-cache-dir

CMD ["python", "scanner_eventos.py"]
