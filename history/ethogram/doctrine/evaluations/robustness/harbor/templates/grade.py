#!/usr/bin/env python3
"""Grade one doctrine-skill arm inside the separate Harbor verifier environment.

Reads only the transferred decision receipt, writes the complete mechanical
arm result and a numeric reward projection under the verifier log directory.
A verifier-internal error exits nonzero without a reward file, which Harbor
reports as a verifier error rather than a subject failure.
"""

import json
import os
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
RECEIPT_PATH = Path(
    os.environ.get("DOCTRINE_EVAL_RECEIPT", "/app/decision-receipt.json")
)
VERIFIER_LOGS = Path(
    os.environ.get("DOCTRINE_EVAL_VERIFIER_LOGS", "/logs/verifier")
)

sys.path.insert(0, str(TESTS / "repo" / "doctrine" / "tools"))
import evaluate_doctrine_skill as harness


def main() -> int:
    VERIFIER_LOGS.mkdir(parents=True, exist_ok=True)
    result = harness.grade_arm(TESTS / "case.json", RECEIPT_PATH)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    (VERIFIER_LOGS / "arm-result.json").write_text(rendered, encoding="utf-8")
    rewards = harness.harbor_rewards(result["arm"])
    (VERIFIER_LOGS / "reward.json").write_text(
        json.dumps(rewards, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
