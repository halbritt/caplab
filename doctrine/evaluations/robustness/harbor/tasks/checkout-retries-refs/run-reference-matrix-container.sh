#!/bin/bash
# Run the reference-solution matrix inside a container namespace, matching
# the environment a Harbor trial actually uses. The host ephemeral-port pool
# is irrelevant here, so the verifier's per-phase port selection is not raced
# by unrelated host processes.
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
TASKS="$(dirname "$HERE")"
IMAGE="checkout-refs-runner:local"

docker build -q -t "$IMAGE" - >/dev/null <<'DOCKER'
FROM golang:1.23-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 curl \
    && rm -rf /var/lib/apt/lists/*
DOCKER

for TASK in checkout-retries-v2 checkout-retries-m1; do
  for REF in noop naive-retry random-key order-key decline; do
    [ "$REF" = decline ] && [ "$TASK" = checkout-retries-v2 ] && continue
    docker run --rm \
      -v "$TASKS/$TASK:/task:ro" \
      -v "$HERE:/refs:ro" \
      "$IMAGE" bash -c '
        set -e
        cp -r /task/environment/app /work
        cp -r /task/tests /tests-local
        mkdir -p /logs/verifier
        export APP_DIR=/work
        if ! bash "/refs/'"$REF"'.sh" >/tmp/ref.log 2>&1; then echo ref-failed; exit 0; fi
        CHECKOUT_APP_DIR=/work CHECKOUT_VERIFIER_LOGS=/logs/verifier \
          bash /tests-local/test.sh >/tmp/v.log 2>&1 || true
        cat /logs/verifier/reward.txt 2>/dev/null || echo no-reward
      ' | awk -v ref="$REF" -v task="$TASK" '{printf "%-14s %-24s %s\n", ref, task, $0}'
  done
done
