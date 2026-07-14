#!/bin/bash
# Reproduce the ambient-VCS verifier defect without invoking a model.
#
# Each task is copied below both an ordinary Git parent and a non-Git parent.
# A git shim records any invocation and exits 128. The go shim disables VCS
# stamping only for the subject-tree builds, isolating the verifier-owned
# pristine gateway build that previously exited before producing a reward.
# The repaired verifier must produce the baseline 0.3 reward without invoking
# git in either parent.
set -eu

HERE="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_ROOT="${VCS_STAMPING_TASKS_ROOT:-$HERE}"
SCRATCH="${VCS_STAMPING_SCRATCH:-$(mktemp -d)}"
REAL_GO="$(command -v go)"
REAL_GIT="$(command -v git)"
SHIMS="$SCRATCH/shims"

mkdir -p "$SHIMS"

printf '%s\n' \
  '#!/bin/sh' \
  'printf "%s\n" "$*" >> "$GIT_SHIM_LOG"' \
  'exit 128' > "$SHIMS/git"

printf '%s\n' \
  '#!/bin/sh' \
  'if [ "${1:-}" = build ] && case "$PWD" in */environment/app) true;; *) false;; esac; then' \
  '  for argument in "$@"; do' \
  '    case "$argument" in -buildvcs=*) exec "$REAL_GO" "$@";; esac' \
  '  done' \
  '  shift' \
  '  exec "$REAL_GO" build -buildvcs=false "$@"' \
  'fi' \
  'exec "$REAL_GO" "$@"' > "$SHIMS/go"

chmod +x "$SHIMS/git" "$SHIMS/go"

FAIL=0
for parent in ordinary-git-parent non-git-parent; do
  root="$SCRATCH/$parent"
  mkdir -p "$root"
  [ "$parent" = ordinary-git-parent ] && "$REAL_GIT" init -q "$root"
  for task in checkout-retries-v2 checkout-retries-m1; do
    label="$parent/$task"
    task_root="$root/$task"
    app="$task_root/environment/app"
    logs="$SCRATCH/$parent-$task-logs"
    git_log="$SCRATCH/$parent-$task-git-shim.log"
    verifier_log="$SCRATCH/$parent-$task-verifier.log"

    cp -a "$TASKS_ROOT/$task" "$task_root"
    mkdir -p "$logs"
    : > "$git_log"

    if ! PATH="$SHIMS:$PATH" REAL_GO="$REAL_GO" GIT_SHIM_LOG="$git_log" \
        bwrap --die-with-parent --bind / / --dev /dev --proc /proc \
          --unshare-user --uid 0 --gid 0 --cap-add CAP_NET_ADMIN --unshare-net -- \
          /bin/sh -c 'ip link set lo up 2>/dev/null; exec "$@"' netns-init \
          env CHECKOUT_APP_DIR="$app" CHECKOUT_VERIFIER_LOGS="$logs" \
          bash "$task_root/tests/test.sh" > "$verifier_log" 2>&1; then
      echo "$label: verifier failed before reward"
      sed -n '1,80p' "$verifier_log"
      echo "git shim invocations: $(wc -l < "$git_log")"
      FAIL=1
      continue
    fi

    if [ "$(cat "$logs/reward.txt")" != "0.3" ]; then
      echo "$label: expected reward 0.3, got $(cat "$logs/reward.txt")"
      exit 1
    fi
    if [ -s "$git_log" ]; then
      echo "$label: verifier invoked git despite disabled VCS stamping"
      sed -n '1,20p' "$git_log"
      exit 1
    fi

    echo "$label: reward=0.3 git-shim-invocations=0"
  done
done

echo "scratch: $SCRATCH"
if [ "$FAIL" -ne 0 ]; then
  echo "VERIFIER VCS STAMPING: FAIL"
  exit 1
fi
echo "VERIFIER VCS STAMPING: PASS"
