"""Behavior tests for the read-only CAPLAB study-results dashboard."""

import copy
import json
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CARD_PROPOSAL = (
    ROOT / "docs/product/capability-cards/"
    "caplab-study-001-explicit-verification-elicited-harm-avoidance.md"
)
CSV_OBJECT = (
    "dbe6f7e8b988823c754ad232c74ad414119a3375:"
    "doctrine/evaluations/robustness/native/"
    "checkout-retries-luna-bv-confirmation-results.csv"
)


def bound_csv_bytes() -> bytes:
    return subprocess.run(
        ["git", "show", CSV_OBJECT],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


@contextmanager
def running_dashboard(studies_dir: Path | None = None):
    from caplab.dashboard.server import create_server

    application_root = ROOT / "caplab" / "dashboard"
    server = create_server(
        ("127.0.0.1", 0),
        application_root=application_root,
        studies_dir=studies_dir,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class StudyProjectorTests(unittest.TestCase):
    def test_bound_study_projects_recomputed_primary_result(self) -> None:
        from caplab.dashboard.projector import project_study_001

        projection = project_study_001(ROOT, CARD_PROPOSAL)

        self.assertEqual(projection["schema_version"], "study-results-dashboard/2")
        self.assertEqual(projection["study_id"], "caplab-study-001")
        self.assertEqual(len(projection["trials"]), 20)
        self.assertEqual(
            projection["primary"],
            {
                "b": {"harmful_shipments": 8, "trials": 8},
                "v": {"harmful_shipments": 0, "trials": 8},
                "risk_difference": 1.0,
                "t_observed": 8,
                "exact_one_sided": {
                    "numerator": 1,
                    "denominator": 256,
                    "p_value": 0.00390625,
                },
            },
        )

    def test_bound_study_projects_first_time_reviewer_context(self) -> None:
        from caplab.dashboard.projector import project_study_001

        projection = project_study_001(ROOT, CARD_PROPOSAL)
        context = projection["study_context"]

        self.assertIn("Pre-edit gateway verification", projection["title"])
        self.assertIn("double-charges customers", projection["catalog_summary"])
        self.assertIn("documented retry contract", context["why"])
        self.assertIn("complete preserved", context["selection_rationale"])
        self.assertIn("duplicate charge", context["scenario"])
        self.assertIn("exact verification package", context["question"])
        self.assertIn("RD > 0", context["hypothesis"])
        self.assertIn("p < 0.05", context["hypothesis"])
        self.assertEqual(set(context["arms"]), {"b", "v"})
        self.assertIn("nothing appended", context["arms"]["b"]["description"])
        self.assertIn("same charge twice", context["arms"]["v"]["description"])
        self.assertIn("reward 0.2", context["harmful_shipment_definition"])
        self.assertIn("eight", context["design"].lower())
        self.assertIn("8/8", context["result_in_plain_english"])
        self.assertIn("0/8", context["result_in_plain_english"])
        self.assertIn("does not show why", context["interpretation"])
        self.assertIn(
            "100-percentage-point",
            context["metric_explanations"]["risk_difference"],
        )
        self.assertIn(
            "not the probability",
            context["metric_explanations"]["exact_one_sided_p"],
        )
        self.assertEqual(
            {entry["term"] for entry in context["glossary"]},
            {
                "B",
                "V",
                "Mutant task",
                "Clean sentinel",
                "Harmful shipment",
                "Paired block",
                "Risk difference",
                "T_obs",
                "Exact one-sided p",
                "Status ledger",
                "DECISION.md",
                "P6-P9",
                "Historical estimate",
                "Unavailable",
                "Traffic observation",
                "Capability card",
            },
        )
        glossary = {entry["term"]: entry["definition"] for entry in context["glossary"]}
        self.assertIn("not yet independently recomputed", glossary["Historical estimate"])
        self.assertIn("has not earned", glossary["Unavailable"])
        self.assertIn("event order", glossary["Traffic observation"])
        self.assertIn("measurement and claim-boundary contract", glossary["Capability card"])

    def test_bound_study_projects_review_states_and_secondary_observations(self) -> None:
        from caplab.dashboard.projector import project_study_001

        projection = project_study_001(ROOT, CARD_PROPOSAL)

        self.assertEqual(
            projection["secondary"],
            {
                "pre_edit_replay_and_ledger": {
                    "label": "Pre-edit same-key replay followed by ledger query",
                    "b": {"observed": 0, "trials": 8},
                    "v": {"observed": 8, "trials": 8},
                },
                "decision_artifact_presence": {
                    "label": "DECISION.md presence",
                    "b": {"observed": 0, "trials": 8},
                    "v": {"observed": 8, "trials": 8},
                },
                "payment_client_modified": {
                    "label": "Payment-client modification",
                    "b": {"observed": 8, "trials": 8},
                    "v": {"observed": 0, "trials": 8},
                },
                "post_edit_replay": {
                    "label": "Post-edit same-key replay",
                    "b": {"observed": 8, "trials": 8},
                    "v": {"observed": 1, "trials": 8},
                },
            },
        )
        self.assertEqual(projection["clean_sentinels"]["b"]["guard_passed"], 2)
        self.assertEqual(projection["clean_sentinels"]["v"]["guard_passed"], 2)
        self.assertEqual(
            projection["clean_sentinels"]["label"], "Fault-clean, not concurrency-clean"
        )
        self.assertEqual(len(projection["paired_blocks"]), 8)
        self.assertEqual(projection["claims"]["historical_execution"]["status"], "complete")
        self.assertEqual(projection["claims"]["study_identity_selection"]["status"], "decided")
        self.assertEqual(projection["claims"]["historical_aggregate"]["status"], "observed")
        self.assertEqual(
            projection["claims"]["exact_v_treatment_estimate"]["status"], "historical_estimate"
        )
        self.assertEqual(projection["claims"]["evidence_admission_p6"]["status"], "unavailable")
        self.assertEqual(
            projection["claims"]["independent_recomputation_p7"]["status"], "unavailable"
        )
        self.assertEqual(projection["claims"]["capability_card"]["status"], "selected")
        self.assertEqual(projection["claims"]["capability_card"]["decision"], "ADR 0006")
        self.assertEqual(projection["claims"]["capability_card"]["decision_status"], "decided")
        self.assertEqual(
            projection["claims"]["evidence_admission_p6"]["state_kind"],
            "registration",
        )
        self.assertEqual(
            projection["claims"]["independent_recomputation_p7"]["state_kind"],
            "recomputation",
        )
        self.assertEqual(
            projection["claims"]["technical_verification"]["state_kind"],
            "verification",
        )
        self.assertEqual(
            projection["claims"]["technical_verification"]["status"],
            "unavailable",
        )
        self.assertEqual(
            projection["claims"]["capability_inference_p8_p9"]["status"], "unavailable"
        )
        self.assertEqual(projection["capability_card"]["artifact_status"], "proposed")
        self.assertEqual(projection["capability_card"]["current_disposition"], "selected")
        self.assertEqual(
            projection["capability_card"]["selection_decision"],
            {"id": "adr-0006", "status": "decided"},
        )
        self.assertEqual(
            projection["presentation"],
            {
                "primary_heading": "Harmful shipment, B versus V",
                "arm_headings": {"b": "B / bare", "v": "V / exact append"},
                "paired_blocks_heading": "Eight mutant B/V blocks",
                "block_column_heading": "Block",
                "trial_ledger_heading": "Twenty frozen trial slots",
                "trial_count_noun": {"singular": "trial", "plural": "trials"},
            },
        )
        self.assertIn(
            "Technical verification",
            projection["claim_boundary"]["unavailable_claims"],
        )
        self.assertIn(
            "CAPLAB acceptance",
            projection["claim_boundary"]["unavailable_claims"],
        )

    def test_malformed_or_drifted_trial_csv_is_rejected(self) -> None:
        from caplab.dashboard.projector import ProjectionError, project_trial_csv

        source_text = bound_csv_bytes().decode("utf-8")
        lines = source_text.splitlines()
        mutations = {
            "wrong header": source_text.replace("sequence,block", "seq,block", 1),
            "missing row": "\n".join(lines[:-1]) + "\n",
            "extra row": source_text + lines[-1] + "\n",
            "duplicate sequence": source_text.replace("1,m1,", "2,m1,", 1),
            "incomplete block": source_text.replace("1,m1,", "1,m2,", 1),
            "changed arm order": source_text.replace(
                "1,m1,checkout-retries-m1,B,", "1,m1,checkout-retries-m1,V,", 1
            ),
            "malformed boolean": source_text.replace(",true,true,false,", ",TRUE,true,false,", 1),
            "observer error": source_text.replace(
                ",false,false,,s01-", ",false,false,boom,s01-", 1
            ),
            "mutant concurrency value": source_text.replace(
                ",false,false,,,160.", ",false,false,0,,160.", 1
            ),
            "clean concurrency missing": source_text.replace(
                ",false,40,10,180.", ",false,,10,180.", 1
            ),
            "replacement attempt": source_text.replace(",valid,1,0.2,", ",valid,2,0.2,", 1),
            "provider failure status": source_text.replace(
                ",valid,1,0.2,", ",provider_error,1,0.2,", 1
            ),
        }

        for scenario, malformed_text in mutations.items():
            with self.subTest(scenario=scenario), self.assertRaises(ProjectionError):
                project_trial_csv(malformed_text.encode("utf-8"))

    def test_projection_bytes_are_deterministic_typed_and_safe(self) -> None:
        from caplab.dashboard.projector import project_study_001_bytes

        first = project_study_001_bytes(ROOT, CARD_PROPOSAL)
        second = project_study_001_bytes(ROOT, CARD_PROPOSAL)
        self.assertEqual(first, second)
        projection = json.loads(first)

        self.assertIs(projection["trials"][0]["harmful_shipment"], True)
        self.assertIsNone(projection["trials"][0]["concurrency_successes"])
        self.assertIsNone(projection["trials"][0]["observer_error"])
        self.assertEqual(projection["trials"][8]["concurrency_successes"], 40)
        self.assertEqual(projection["missingness"]["valid_first_attempts"], 20)
        self.assertEqual(projection["missingness"]["provider_failures"], 0)
        self.assertEqual(
            projection["capability_card"]["construct"],
            "explicit-verification-elicited harm avoidance in checkout retries",
        )
        self.assertGreaterEqual(len(projection["capability_card"]["exclusions"]), 6)
        self.assertGreaterEqual(len(projection["capability_card"]["promotion_gates"]), 5)

        serialized = first.decode("utf-8").lower()
        for prohibited in (
            "/var/tmp/",
            "/tmp/",
            "presigned_url",
            "access_key",
            "secret_key",
            "trajectory.json",
            "workspace contents",
            "object locator",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, serialized)

    def test_checked_in_projection_matches_current_bound_sources(self) -> None:
        from caplab.dashboard.projector import project_study_001_bytes

        checked_in = ROOT / "caplab/dashboard/studies/caplab-study-001.json"
        self.assertEqual(checked_in.read_bytes(), project_study_001_bytes(ROOT, CARD_PROPOSAL))

    def test_source_hash_mismatch_fails_before_csv_projection(self) -> None:
        from caplab.dashboard.projector import ProjectionError, project_study_001

        corrupt_git_read = subprocess.CompletedProcess(
            args=["git", "show"], returncode=0, stdout=b"changed bytes", stderr=b""
        )
        with (
            mock.patch("caplab.dashboard.projector.subprocess.run", return_value=corrupt_git_read),
            self.assertRaisesRegex(ProjectionError, "hash mismatch"),
        ):
            project_study_001(ROOT, CARD_PROPOSAL)

    def test_unresolved_git_source_fails_closed(self) -> None:
        from caplab.dashboard.projector import ProjectionError, project_study_001

        unavailable = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "show"],
            stderr=b"fatal: bad object",
        )
        with (
            mock.patch(
                "caplab.dashboard.projector.subprocess.run",
                side_effect=unavailable,
            ),
            self.assertRaisesRegex(ProjectionError, "bound Git source is unavailable"),
        ):
            project_study_001(ROOT, CARD_PROPOSAL)

    def test_changed_card_artifact_is_unavailable_while_selection_remains_decided(
        self,
    ) -> None:
        from caplab.dashboard.projector import project_study_001

        with tempfile.TemporaryDirectory() as temporary:
            changed_card = Path(temporary) / "card.md"
            changed_card.write_text("changed proposal\n", encoding="utf-8")
            projection = project_study_001(ROOT, changed_card)
        self.assertEqual(projection["capability_card"]["artifact_status"], "unavailable")
        self.assertEqual(projection["capability_card"]["current_disposition"], "selected")
        self.assertEqual(projection["claims"]["capability_card"]["status"], "selected")

    def test_capability_card_is_parsed_from_the_verified_bytes(self) -> None:
        from caplab.dashboard.projector import project_study_001

        with mock.patch.object(
            Path,
            "read_text",
            side_effect=AssertionError("verified card must not be reopened"),
        ):
            projection = project_study_001(ROOT, CARD_PROPOSAL)

        self.assertEqual(projection["capability_card"]["artifact_status"], "proposed")


class DashboardServiceTests(unittest.TestCase):
    def test_same_origin_service_is_read_only_and_hardened(self) -> None:
        with running_dashboard() as base_url:
            with urllib.request.urlopen(f"{base_url}/") as response:
                html = response.read()
                self.assertEqual(response.status, 200)
                self.assertIn(b"CAPLAB Study Results", html)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                self.assertIn("default-src 'none'", response.headers["Content-Security-Policy"])
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
                self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")
                self.assertEqual(response.headers["X-Robots-Tag"], "noindex, nofollow")

            with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                catalog_bytes = response.read()
                catalog = json.loads(catalog_bytes)
                self.assertEqual(
                    response.headers["Content-Type"], "application/json; charset=utf-8"
                )
                self.assertEqual(
                    [study["study_id"] for study in catalog["studies"]], ["caplab-study-001"]
                )
                self.assertEqual(catalog["comparison"]["status"], "unavailable")

            with urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-001") as response:
                self.assertEqual(json.loads(response.read())["primary"]["t_observed"], 8)

            head_request = urllib.request.Request(
                f"{base_url}/api/studies/caplab-study-001", method="HEAD"
            )
            with urllib.request.urlopen(head_request) as response:
                self.assertEqual(response.read(), b"")
                self.assertGreater(int(response.headers["Content-Length"]), 0)

            for method in ("POST", "PUT", "PATCH", "DELETE"):
                with self.subTest(method=method):
                    mutation_request = urllib.request.Request(
                        f"{base_url}/api/studies", data=b"{}", method=method
                    )
                    with self.assertRaises(urllib.error.HTTPError) as caught:
                        urllib.request.urlopen(mutation_request)
                    self.assertEqual(caught.exception.code, 405)
                    self.assertEqual(caught.exception.headers["Allow"], "GET, HEAD")

            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(f"{base_url}/not-found")
            self.assertEqual(caught.exception.code, 404)

    def test_ui_exposes_accessible_generic_review_controls(self) -> None:
        application_root = ROOT / "caplab" / "dashboard"
        html = (application_root / "index.html").read_text(encoding="utf-8")
        script = (application_root / "app.js").read_text(encoding="utf-8")

        for required_markup in (
            'for="study-select"',
            'id="study-select"',
            'for="trial-filter"',
            'id="trial-filter"',
            'aria-live="polite"',
            'id="primary-heading"',
            'id="primary-b-heading"',
            'id="primary-v-heading"',
            'id="blocks-heading"',
            'id="block-column-heading"',
            'id="ledger-heading"',
            'id="context-heading"',
            'id="context-why"',
            'id="context-question"',
            'id="context-arms"',
            'id="context-glossary"',
            'aria-label="B harmful-shipment rate"',
            'aria-label="V harmful-shipment rate"',
            "<table",
            "<noscript>",
        ):
            with self.subTest(required_markup=required_markup):
                self.assertIn(required_markup, html)
        for visible_surface in (
            "Study in plain English",
            "Status ledger",
            "Harmful shipment, B versus V",
            "Traffic and workspace observables",
            "Eight mutant B/V blocks",
            "Twenty frozen trial slots",
            "Bound identities",
            "What this result does not establish",
            "Capability-card proposal",
        ):
            with self.subTest(visible_surface=visible_surface):
                self.assertIn(visible_surface, html)
        self.assertIn("State kind", html)
        self.assertNotIn("Assertion type", html)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("document.write", script)
        self.assertIn('value === null ? "unavailable"', script)

    def test_catalog_discovers_new_studies_and_invalid_projection_fails_closed(self) -> None:
        checked_in = json.loads(
            (ROOT / "caplab/dashboard/studies/caplab-study-001.json").read_bytes()
        )
        with tempfile.TemporaryDirectory() as temporary:
            studies_dir = Path(temporary)
            first_bytes = (ROOT / "caplab/dashboard/studies/caplab-study-001.json").read_bytes()
            (studies_dir / "caplab-study-001.json").write_bytes(first_bytes)
            second = dict(checked_in)
            second["study_id"] = "caplab-study-002"
            second["display_id"] = "Study 002"
            second["title"] = "Fixture second projection"
            (studies_dir / "caplab-study-002.json").write_text(
                json.dumps(second, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (studies_dir / "caplab-study-broken.json").write_text("not json\n", encoding="utf-8")

            with running_dashboard(studies_dir) as base_url:
                with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                    catalog = json.loads(response.read())
                self.assertEqual(
                    [study["study_id"] for study in catalog["studies"]],
                    ["caplab-study-001", "caplab-study-002", "caplab-study-broken"],
                )
                self.assertEqual(catalog["comparison"]["study_count"], 3)
                with urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-002") as response:
                    self.assertEqual(json.loads(response.read())["display_id"], "Study 002")
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-broken")
                self.assertEqual(caught.exception.code, 503)
                self.assertNotIn(temporary, caught.exception.read().decode("utf-8"))

    def test_schema_shaped_malformed_projections_fail_closed(self) -> None:
        checked_in = json.loads(
            (ROOT / "caplab/dashboard/studies/caplab-study-001.json").read_bytes()
        )

        def missing_state_kind(projection):
            projection["claims"]["historical_execution"].pop("state_kind")

        def empty_paired_blocks(projection):
            projection["paired_blocks"] = []

        def malformed_trial(projection):
            projection["trials"] = [{}]

        def malformed_primary_arm(projection):
            projection["primary"]["b"] = {}

        def inconsistent_primary_count(projection):
            projection["primary"]["b"]["harmful_shipments"] = 7

        def missing_presentation(projection):
            projection.pop("presentation")

        def missing_study_context(projection):
            projection.pop("study_context")

        def duplicate_glossary_term(projection):
            projection["study_context"]["glossary"][1]["term"] = projection[
                "study_context"
            ]["glossary"][0]["term"]

        corruptions = {
            "claim missing state kind": missing_state_kind,
            "empty paired blocks": empty_paired_blocks,
            "malformed trial": malformed_trial,
            "malformed primary arm": malformed_primary_arm,
            "inconsistent primary count": inconsistent_primary_count,
            "missing presentation": missing_presentation,
            "missing study context": missing_study_context,
            "duplicate glossary term": duplicate_glossary_term,
        }

        for scenario, corrupt in corruptions.items():
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                studies_dir = Path(temporary)
                malformed = copy.deepcopy(checked_in)
                corrupt(malformed)
                (studies_dir / "caplab-study-001.json").write_text(
                    json.dumps(malformed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with running_dashboard(studies_dir) as base_url:
                    with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                        catalog = json.loads(response.read())
                    self.assertEqual(catalog["studies"][0]["availability"], "unavailable")
                    with self.assertRaises(urllib.error.HTTPError) as study_error:
                        urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-001")
                    self.assertEqual(study_error.exception.code, 503)
                    with self.assertRaises(urllib.error.HTTPError) as health_error:
                        urllib.request.urlopen(f"{base_url}/healthz")
                    self.assertEqual(health_error.exception.code, 503)

    def test_non_finite_json_numbers_fail_closed(self) -> None:
        checked_in = (ROOT / "caplab/dashboard/studies/caplab-study-001.json").read_text(
            encoding="utf-8"
        )
        finite_fragment = '"risk_difference": 1.0'
        self.assertIn(finite_fragment, checked_in)

        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), tempfile.TemporaryDirectory() as temporary:
                studies_dir = Path(temporary)
                malformed = checked_in.replace(
                    finite_fragment,
                    f'"risk_difference": {constant}',
                    1,
                )
                (studies_dir / "caplab-study-001.json").write_text(
                    malformed,
                    encoding="utf-8",
                )
                with running_dashboard(studies_dir) as base_url:
                    with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                        catalog = json.loads(response.read())
                    self.assertEqual(catalog["studies"][0]["availability"], "unavailable")
                    with self.assertRaises(urllib.error.HTTPError) as study_error:
                        urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-001")
                    self.assertEqual(study_error.exception.code, 503)

    def test_private_or_uncontracted_projection_content_fails_closed(self) -> None:
        checked_in = json.loads(
            (ROOT / "caplab/dashboard/studies/caplab-study-001.json").read_bytes()
        )
        prohibited_values = (
            "/var/tmp/private-run",
            "/tmp/raw-workspace",
            "preservation_root",
            '"prompt_text"',
            "trajectory.json",
            "workspace contents",
            '"decision_text"',
            "access_key",
            "secret_key",
            '"credentials"',
            "object locator",
            "object_store",
            "s3://private-bucket/key",
            "presigned_url",
            "x-amz-signature",
        )

        corruptions = [
            ("extra top-level field", None),
            *[(value, value) for value in prohibited_values],
        ]
        for scenario, prohibited in corruptions:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                studies_dir = Path(temporary)
                malformed = copy.deepcopy(checked_in)
                if prohibited is None:
                    malformed["private_payload"] = "must not be served"
                else:
                    malformed["title"] = prohibited
                (studies_dir / "caplab-study-001.json").write_text(
                    json.dumps(malformed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with running_dashboard(studies_dir) as base_url:
                    with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                        catalog = json.loads(response.read())
                    self.assertEqual(catalog["studies"][0]["availability"], "unavailable")


if __name__ == "__main__":
    unittest.main()
