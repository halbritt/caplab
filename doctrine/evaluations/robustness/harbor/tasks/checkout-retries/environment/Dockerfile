FROM golang:1.23-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ /app/
RUN chmod +x /app/scripts/smoke.sh && go build ./...
