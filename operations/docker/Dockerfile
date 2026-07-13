FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the platform package (build context is the repo root)
COPY src/ /app/src/
COPY operations/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# src/ holds the `communication` package; put it on the path so module-style
# entrypoints (python -m communication.calling.agent) resolve.
ENV PYTHONPATH=/app/src

# FastAPI (communication.api.main) listens here; the LiveKit agent worker has
# no inbound port.
EXPOSE 8080

# Runs both the FastAPI server and the LiveKit agent worker.
CMD ["/app/start.sh"]
