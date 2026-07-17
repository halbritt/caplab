"""Exact source identities selected for CAPLAB Study 001 P6."""

from __future__ import annotations

from pathlib import Path

from .models import GitRecord, SourceSet


PRESERVATION_ROOT = Path(
    "/var/tmp/striatum-bench/luna-bv-confirmation-preserved-2026-07-14"
)
PRESERVATION_MANIFEST_SHA256 = (
    "081a14d9b4f2872a2d8058f1b0896a7d0e4fd954f164b8c46d2d768558a0d50c"
)
PREREGISTRATION_COMMIT = "598c670885626d598a03a84a7274286ffca5ab8a"
RESULT_COMMIT = "dbe6f7e8b988823c754ad232c74ad414119a3375"


def source_set(*, preservation_root: Path = PRESERVATION_ROOT) -> SourceSet:
    return SourceSet(
        study_id="caplab-study-001",
        preservation_root=preservation_root,
        preservation_manifest_sha256=PRESERVATION_MANIFEST_SHA256,
        git_records=(
            GitRecord(
                record_id="preregistration",
                commit=PREREGISTRATION_COMMIT,
                path=(
                    "doctrine/evaluations/robustness/native/"
                    "checkout-retries-luna-bv-confirmation.md"
                ),
                content_sha256=(
                    "4d8b1418172a0fc6b042efcca6dad96a5dcb08c7ded4006804fce7aa18ff3eb9"
                ),
                already_preserved_path=(
                    "frozen-inputs/checkout-retries-luna-bv-confirmation.md"
                ),
            ),
            GitRecord(
                record_id="result-record",
                commit=RESULT_COMMIT,
                path=(
                    "doctrine/evaluations/robustness/native/"
                    "checkout-retries-luna-bv-confirmation-result.md"
                ),
                content_sha256=(
                    "870a96b8b528dee1c85337d83662d9900a1fccd7531c181914ed948d02ed0bf4"
                ),
            ),
            GitRecord(
                record_id="result-csv",
                commit=RESULT_COMMIT,
                path=(
                    "doctrine/evaluations/robustness/native/"
                    "checkout-retries-luna-bv-confirmation-results.csv"
                ),
                content_sha256=(
                    "af8d64fde0b7a93773dfc2ac36651d61ee7259095eef792fa7515810a57a2374"
                ),
            ),
        ),
        expected_preservation_records=681,
        expected_total_records=684,
        expected_attempts=20,
    )
