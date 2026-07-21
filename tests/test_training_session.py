import unittest

from caplab.review_dissent.training_session import (
    SessionContractError,
    qualification_acceptance,
    validate_fleet_sample,
    validate_qualification,
)


class TrainingSessionTests(unittest.TestCase):
    def test_fleet_sample_must_preserve_exact_live_lease(self) -> None:
        sample = {
            "node": "peecee",
            "slot_id": 1,
            "status": "routable",
            "alive": True,
            "fresh": True,
            "lease_id": "lease-1",
            "heartbeat_ts": "2026-07-21T03:30:00Z",
        }
        self.assertEqual(
            validate_fleet_sample(sample, lease_id="lease-1"),
            "2026-07-21T03:30:00Z",
        )
        for field, value in (
            ("node", "other"),
            ("slot_id", 0),
            ("status", "unverified"),
            ("alive", False),
            ("fresh", False),
            ("lease_id", "other-lease"),
        ):
            changed = dict(sample)
            changed[field] = value
            with self.subTest(field=field):
                with self.assertRaises(SessionContractError):
                    validate_fleet_sample(changed, lease_id="lease-1")

    def test_qualification_requires_no_update_and_representative_duration(self) -> None:
        qualification = {
            "schema": "caplab.training.host-qualification/v1",
            "experiment_id": "caplab-review-dissent-qwen27b-qlora-r2",
            "duration_seconds": "61.25",
            "iterations": 4,
            "adapter_sha256_before": "a" * 64,
            "adapter_sha256_after": "a" * 64,
            "optimizer_steps": 0,
        }
        validate_qualification(qualification)
        changed = dict(qualification, adapter_sha256_after="b" * 64)
        with self.assertRaisesRegex(SessionContractError, "qualification_updated_adapter"):
            validate_qualification(changed)

    def test_acceptance_binds_four_distinct_heartbeats_and_boot_identity(self) -> None:
        acceptance = qualification_acceptance(
            lease_id="lease-1",
            host_boot_id="boot-1",
            qualification_sha256="a" * 64,
            heartbeat_timestamps=["h1", "h1", "h2", "h3", "h4"],
        )
        self.assertEqual(acceptance["distinct_fleet_heartbeats"], 4)
        self.assertEqual(acceptance["host_boot_id"], "boot-1")
        with self.assertRaisesRegex(SessionContractError, "qualification_heartbeat_floor"):
            qualification_acceptance(
                lease_id="lease-1",
                host_boot_id="boot-1",
                qualification_sha256="a" * 64,
                heartbeat_timestamps=["h1", "h2", "h3"],
            )


if __name__ == "__main__":
    unittest.main()
