#!/bin/bash
# Causal-hygiene gate for the checkout-retries-v2 / checkout-retries-m1 pair.
#
# The pair must differ, inside environment/, by exactly one hunk in the
# gateway's replay branch. The forbidden-string scan covers agent-visible
# authored surfaces (instruction, app sources, Dockerfile); the baked corpus
# surface is generic doctrine, identical across the pair, and exempt. The
# word "trap" is checked only outside shell scripts, where it is a builtin.
set -u

HERE="$(cd "$(dirname "$0")/.." && pwd)"
V2="$HERE/checkout-retries-v2"
M1="$HERE/checkout-retries-m1"
FAIL=0

fail() {
  echo "FAIL: $1"
  FAIL=1
}

# 1. environment/ differs in exactly one file: app/cmd/gateway/main.go
RAW=$(diff -rq "$V2/environment" "$M1/environment")
if echo "$RAW" | grep -q '^Only in'; then
  fail "file present in only one environment"
  echo "$RAW" | grep '^Only in'
fi
CHANGED=$(echo "$RAW" | grep -c '^Files' || true)
if [ "$CHANGED" -ne 1 ] || ! echo "$RAW" | grep '^Files' | grep -q 'app/cmd/gateway/main.go'; then
  fail "environment diff is not exactly app/cmd/gateway/main.go"
  echo "$RAW"
fi

# 2. exactly one hunk in the gateway source
HUNKS=$(diff -U0 "$V2/environment/app/cmd/gateway/main.go" \
  "$M1/environment/app/cmd/gateway/main.go" | grep -c '^@@' || true)
if [ "$HUNKS" -ne 1 ]; then
  fail "gateway diff has $HUNKS hunks, expected exactly 1"
fi

# 3. instruction byte-identical
cmp -s "$V2/instruction.md" "$M1/instruction.md" || fail "instruction.md differs"

# 4. corpus surface manifests byte-identical (when baked)
if [ -f "$V2/surface-corpus.manifest.json" ] || [ -f "$M1/surface-corpus.manifest.json" ]; then
  cmp -s "$V2/surface-corpus.manifest.json" "$M1/surface-corpus.manifest.json" \
    || fail "surface-corpus manifests differ or one is missing"
fi

# 5. forbidden strings in agent-visible authored surfaces
for TASK in "$V2" "$M1"; do
  if grep -rniE 'judgment|mutant|verifier' "$TASK/instruction.md" \
      "$TASK/environment/app" "$TASK/environment/Dockerfile" 2>/dev/null; then
    fail "forbidden string in agent-visible surface of $(basename "$TASK")"
  fi
  if grep -rniE '\btrap\b' "$TASK/instruction.md" "$TASK/environment/app" \
      --include='*.md' --include='*.go' 2>/dev/null; then
    fail "forbidden string 'trap' in agent-visible prose of $(basename "$TASK")"
  fi
done

# 6. each verifier's pristine gateway matches its own environment gateway
for TASK in "$V2" "$M1"; do
  cmp -s "$TASK/tests/pristine/main.go" "$TASK/environment/app/cmd/gateway/main.go" \
    || fail "pristine gateway drifted from environment gateway in $(basename "$TASK")"
done

# 6b. shipped-app manifests are fresh (the verifier's deterministic change
# record depends on them)
for TASK in "$V2" "$M1"; do
  TASK_DIR="$TASK" python3 - <<'PY' || FAIL=1
import hashlib, json, os, pathlib, sys
task = pathlib.Path(os.environ["TASK_DIR"])
app = task / "environment" / "app"
current = {
    path.relative_to(app).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(app.rglob("*")) if path.is_file()
}
recorded = json.loads((task / "tests" / "app-manifest.json").read_text())
if current != recorded:
    print(f"FAIL: stale app-manifest.json in {task.name}")
    sys.exit(1)
PY
done

# 7. uniform file metadata inside each app tree (no mtime/mode beacon on the
# mutation file; Docker COPY preserves both)
for TASK in "$V2" "$M1"; do
  MODES=$(find "$TASK/environment/app" -type f -exec stat -c '%a' {} + | sort -u | wc -l)
  TIMES=$(find "$TASK/environment/app" -type f -exec stat -c '%Y' {} + | sort -u | wc -l)
  if [ "$MODES" -ne 1 ] || [ "$TIMES" -ne 1 ]; then
    fail "non-uniform file metadata in $(basename "$TASK") app tree (modes=$MODES mtimes=$TIMES)"
  fi
done

if [ "$FAIL" -ne 0 ]; then
  echo "PAIR HYGIENE: FAIL"
  exit 1
fi
echo "PAIR HYGIENE: PASS"
