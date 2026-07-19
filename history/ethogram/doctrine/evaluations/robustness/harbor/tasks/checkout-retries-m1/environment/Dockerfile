FROM golang:1.23-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --break-system-packages --no-cache-dir \
    "jsonschema>=4.18,<5" "PyYAML>=6.0,<7"

WORKDIR /app
COPY app/ /app/
COPY corpus/ /home/halbritt/git/books/
RUN chmod +x /app/scripts/smoke.sh && go build ./...
