#!/bin/bash
# Empirical probe (redirected access log) followed by a decline.
set -euo pipefail
source "$(dirname "$0")/_probe.sh"
probe_replay
write_decline
