"""Behavior tests for the standalone read-only dashboard."""

import copy
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from caplab.dashboard.server import DashboardStore, create_server


ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def running_dashboard(studies_dir: Path | None = None):
    application_root = ROOT / "src/caplab/dashboard"
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


class DashboardStoreTests(unittest.TestCase):
    def test_standalone_catalog_serves_the_imported_study_projection(self) -> None:
        store = DashboardStore(ROOT / "src/caplab/dashboard/studies")

        catalog = json.loads(store.catalog_bytes)
        self.assertEqual(catalog["comparison"]["study_count"], 1)
        self.assertEqual(catalog["studies"][0]["study_id"], "caplab-study-001")
        self.assertEqual(catalog["studies"][0]["availability"], "available")

    def test_same_origin_service_is_read_only_and_hardened(self) -> None:
        with running_dashboard() as base_url:
            with urllib.request.urlopen(f"{base_url}/") as response:
                self.assertIn(b"CAPLAB Study Results", response.read())
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                self.assertIn(
                    "default-src 'none'", response.headers["Content-Security-Policy"]
                )
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
                self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")
                self.assertEqual(response.headers["X-Robots-Tag"], "noindex, nofollow")

            with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                catalog = json.loads(response.read())
                self.assertEqual(
                    [study["study_id"] for study in catalog["studies"]],
                    ["caplab-study-001"],
                )

            for method in ("POST", "PUT", "PATCH", "DELETE"):
                with self.subTest(method=method):
                    request = urllib.request.Request(
                        f"{base_url}/api/studies", data=b"{}", method=method
                    )
                    with self.assertRaises(urllib.error.HTTPError) as caught:
                        urllib.request.urlopen(request)
                    self.assertEqual(caught.exception.code, 405)
                    self.assertEqual(caught.exception.headers["Allow"], "GET, HEAD")

    def test_ui_exposes_accessible_review_controls_without_html_injection(self) -> None:
        application_root = ROOT / "src/caplab/dashboard"
        html = (application_root / "index.html").read_text(encoding="utf-8")
        script = (application_root / "app.js").read_text(encoding="utf-8")

        for required_markup in (
            'for="study-select"',
            'id="study-select"',
            'for="trial-filter"',
            'id="trial-filter"',
            'aria-live="polite"',
            "<table",
            "<noscript>",
        ):
            with self.subTest(required_markup=required_markup):
                self.assertIn(required_markup, html)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("document.write", script)
        self.assertIn('value === null ? "unavailable"', script)

    def test_catalog_discovers_valid_studies_and_fails_closed_on_invalid_json(self) -> None:
        checked_in_path = (
            ROOT / "src/caplab/dashboard/studies/caplab-study-001.json"
        )
        checked_in = json.loads(checked_in_path.read_bytes())
        with tempfile.TemporaryDirectory() as temporary:
            studies_dir = Path(temporary)
            (studies_dir / "caplab-study-001.json").write_bytes(
                checked_in_path.read_bytes()
            )
            second = dict(checked_in)
            second["study_id"] = "caplab-study-002"
            second["display_id"] = "Study 002"
            second["title"] = "Fixture second projection"
            (studies_dir / "caplab-study-002.json").write_text(
                json.dumps(second, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (studies_dir / "caplab-study-broken.json").write_text(
                "not json\n", encoding="utf-8"
            )

            with running_dashboard(studies_dir) as base_url:
                with urllib.request.urlopen(f"{base_url}/api/studies") as response:
                    catalog = json.loads(response.read())
                self.assertEqual(
                    [study["study_id"] for study in catalog["studies"]],
                    ["caplab-study-001", "caplab-study-002", "caplab-study-broken"],
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(f"{base_url}/api/studies/caplab-study-broken")
                self.assertEqual(caught.exception.code, 503)
                self.assertNotIn(temporary, caught.exception.read().decode("utf-8"))

    def test_schema_shaped_projection_corruption_fails_closed(self) -> None:
        checked_in = json.loads(
            (ROOT / "src/caplab/dashboard/studies/caplab-study-001.json").read_bytes()
        )

        def missing_state_kind(projection):
            projection["claims"]["historical_execution"].pop("state_kind")

        def inconsistent_primary_count(projection):
            projection["primary"]["b"]["harmful_shipments"] = 7

        def malformed_trial(projection):
            projection["trials"] = [{}]

        corruptions = {
            "claim missing state kind": missing_state_kind,
            "inconsistent primary count": inconsistent_primary_count,
            "malformed trial": malformed_trial,
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

                store = DashboardStore(studies_dir)
                self.assertEqual(list(store.study_bytes), [])
                self.assertIn("caplab-study-001", store.unavailable)

    def test_non_finite_numbers_fail_closed(self) -> None:
        checked_in = (
            ROOT / "src/caplab/dashboard/studies/caplab-study-001.json"
        ).read_text(encoding="utf-8")
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
                    malformed, encoding="utf-8"
                )

                store = DashboardStore(studies_dir)
                self.assertIn("caplab-study-001", store.unavailable)

    def test_private_or_uncontracted_projection_content_fails_closed(self) -> None:
        checked_in = json.loads(
            (ROOT / "src/caplab/dashboard/studies/caplab-study-001.json").read_bytes()
        )
        prohibited_values = (
            "/var/tmp/private-run",
            "/tmp/raw-workspace",
            "trajectory.json",
            "access_key",
            "secret_key",
            "s3://private-bucket/key",
            "presigned_url",
        )

        for prohibited in prohibited_values:
            with self.subTest(prohibited=prohibited), tempfile.TemporaryDirectory() as temporary:
                studies_dir = Path(temporary)
                malformed = copy.deepcopy(checked_in)
                malformed["title"] = prohibited
                (studies_dir / "caplab-study-001.json").write_text(
                    json.dumps(malformed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                store = DashboardStore(studies_dir)
                self.assertIn("caplab-study-001", store.unavailable)

        with tempfile.TemporaryDirectory() as temporary:
            studies_dir = Path(temporary)
            malformed = copy.deepcopy(checked_in)
            malformed["private_payload"] = "must not be served"
            (studies_dir / "caplab-study-001.json").write_text(
                json.dumps(malformed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            store = DashboardStore(studies_dir)
            self.assertIn("caplab-study-001", store.unavailable)


if __name__ == "__main__":
    unittest.main()
