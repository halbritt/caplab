"""Shared-catalog discovery and prospective-preparation integration.

Discovery and refusals run against the installed Quartermaster command (skipped when it is
absent). A process-boundary double covers the argv seam and the success path; one end-to-end
test needs a Quartermaster source that accepts a null native home (CAPLAB_TEST_QUARTERMASTER_SRC).
"""

from __future__ import annotations

import copy
import dataclasses
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import catalog_support as support
import test_revbench as rb
from catalog_support import FakeQuartermaster

from caplab.catalog import CatalogSelectionError, load_projection, select_entry, validate_against_spec
from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.runtime.canonical import canonical_json, sha256_hex

ENVIRONMENT = dict(os.environ, PYTHONPATH=support.SOURCE)


def run(arguments, cwd, **options):
    return subprocess.run([sys.executable, *arguments], cwd=cwd, env=options.pop("env", ENVIRONMENT),
                          capture_output=True, check=False, **options)


def error_code(completed) -> str:
    return json.loads(completed.stderr.splitlines()[-1])["code"]


def publish(directory: Path, source: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    source_path = support.write_json(directory / "catalog-source.json", source)
    completed = subprocess.run(
        [support.INSTALLED, "catalog", "publish", str(source_path), "--releases", str(directory / "releases"),
         "--publisher", "fixture-publisher"], capture_output=True, check=True, cwd=directory)
    return Path(json.loads(completed.stdout)["path"])


def discover(release: Path, overlay: Path, cwd: Path, *extra, argv=None):
    return run(["-m", "caplab", "catalog", "discover", "--release", str(release), "--overlay", str(overlay),
                "--quartermaster-argv", json.dumps(argv or [support.INSTALLED]), *extra], cwd)


@unittest.skipUnless(support.INSTALLED, "the installed quartermaster command is not available")
class InstalledQuartermasterDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.root = Path(self._directory.name)
        self.overlay = support.write_json(self.root / "overlay.json", support.overlay())
        self.release = publish(self.root, support.catalog_source())

    def entries(self, completed):
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        document = json.loads(completed.stdout)
        return document, {e["declaration_id"]: e for e in document["entries"]}

    def test_discovery_reports_policy_status_without_any_authority_from_an_unrelated_cwd(self):
        sweep = support.write_json(self.root / "sweep-config.json", {
            "population": {"supervised_only_runtimes": ["claude-code", "codex"]}})
        sweep_bytes = sweep.read_bytes()
        before = support.tree_snapshot(self.root)

        completed = discover(self.release, self.overlay, self.root, "--native-policy", str(support.POLICY),
                             "--sweep-config", str(sweep))
        document, entries = self.entries(completed)

        self.assertEqual(completed.stdout, canonical_json(document) + b"\n")
        self.assertEqual((document["status"], set(document["authority"].values())), ("proposal", {False}))
        self.assertEqual(document["catalog"]["release_id"], json.loads(self.release.read_bytes())["release_id"])
        self.assertEqual(document["catalog"]["release_file_sha256"], sha256_hex(self.release.read_bytes()))
        # The one tuple the digest-pinned policy lists is admitted; a model only the catalog knows is not.
        self.assertEqual(entries["terra-codex-main-max"]["native"]["status"], "admitted")
        self.assertEqual(entries["sol-codex-main-high"]["native"]["status"], "not_admitted")
        alt = entries["sol-codex-alt-high"]["native"]
        self.assertEqual((alt["status"], alt["reason"]), ("not_native_eligible", "config_home_not_canonical"))
        # Declaration IDs are advisory names; discovery never mints or shows public binding identities.
        self.assertNotIn(b"bnd-", completed.stdout)
        self.assertEqual(document["population"]["applied"], False)
        self.assertIn("codex-harm", document["population"]["supervised_only_runtimes"])
        self.assertEqual(sweep.read_bytes(), sweep_bytes)
        self.assertEqual(support.tree_snapshot(self.root), before)  # no ledger, custody or output appeared

    def test_a_dropped_supervised_runtime_is_warned_about_and_nothing_is_rewritten(self):
        sweep = support.write_json(self.root / "sweep-config.json", {
            "population": {"supervised_only_runtimes": ["codex", "historic-runtime"]}})

        document, _ = self.entries(discover(self.release, self.overlay, self.root, "--sweep-config", str(sweep)))

        warning = next(w for w in document["warnings"] if w["code"] == "population_would_drop_supervised_runtime")
        self.assertIn("historic-runtime", warning["detail"])
        self.assertEqual(document["population"]["applied"], False)

    def test_a_model_added_only_to_the_catalog_appears_with_no_code_or_overlay_edit(self):
        later = publish(self.root / "later", support.catalog_source(
            support.route("terra-next", "gpt-5.7-terra", efforts=("max",))))
        _, before = self.entries(discover(self.release, self.overlay, self.root))
        _, after = self.entries(discover(later, self.overlay, self.root, "--native-policy", str(support.POLICY)))

        added = set(after) - set(before)
        self.assertEqual(added, {"terra-next-codex-main-max"})
        new = after["terra-next-codex-main-max"]
        self.assertEqual((new["origin"], new["enabled"], new["model"]), ("discovered", False, "gpt-5.7-terra"))
        self.assertEqual(new["native"]["status"], "not_admitted")  # the closed policy is not expanded
        for key, entry in before.items():
            unchanged = {k: v for k, v in entry.items() if k != "native"}
            self.assertEqual(unchanged, {k: v for k, v in after[key].items() if k != "native"})

    def test_preparation_refuses_unrelated_or_ineligible_entries_before_any_ledger_change(self):
        ledger, spec_path = self.prepared_ledger()
        before = support.tree_snapshot(ledger)
        for entry, code in (("sol-codex-main-high", "catalog_model_mismatch"),
                            ("sol-codex-alt-high", "catalog_entry_not_native_eligible"),
                            ("no-such-entry", "catalog_entry_unknown")):
            with self.subTest(entry=entry):
                output = self.root / f"{entry}.json"
                completed = self.prepare(spec_path, ledger, output, self.release, self.overlay, entry)
                self.assertEqual((completed.returncode, completed.stdout, error_code(completed)), (2, b"", code))
                self.assertFalse(output.exists())
                self.assertEqual(support.tree_snapshot(ledger), before)

    def prepared_ledger(self):
        ledger = self.root / "ledger"
        spec_path = self.root / "spec.json"
        spec_path.write_bytes(canonical_json(rb.make_spec(rb.LedgerRegistrar(ledger))))
        return ledger, spec_path

    def prepare(self, spec_path, ledger, output, release, overlay, entry, *, argv=None, extra=()):
        return run(["-m", "caplab.revbench", "prepare", "--spec", str(spec_path), "--ledger", str(ledger),
                    "--output", str(output), "--catalog-release", str(release), "--catalog-overlay", str(overlay),
                    "--catalog-entry", entry, "--quartermaster-argv", json.dumps(argv or [support.INSTALLED]),
                    *extra], self.root)


class ProcessSeamTests(unittest.TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.root = Path(self._directory.name)
        (self.root / "bin").mkdir()
        self.fake = FakeQuartermaster(self.root / "bin")
        self.release = support.write_json(self.root / "release.json", support.fixture_release())
        self.overlay = support.write_json(self.root / "overlay.json", {"consumer": "caplab"})

    def load(self, **options):
        return load_projection(self.release, self.overlay, [str(self.fake.path)], **options)

    def test_the_seam_passes_the_exact_bytes_through_one_documented_argv(self):
        self.fake.serve(support.canned_projection("ignored"))

        projection = self.load()

        call = self.fake.recorded()[0]
        self.assertEqual((call["args"], call["count"], call["names"]), (["catalog", "project"], 4,
                                                                          ["release.json", "overlay.json"]))
        self.assertEqual(call["sha256"], [sha256_hex(self.release.read_bytes()), sha256_hex(self.overlay.read_bytes())])
        self.assertTrue(call["cwd_is_temporary"])
        self.assertEqual(projection.release_bytes, self.release.read_bytes())
        self.assertEqual(projection.document["entries"][0]["key"], "fixture-static-fixed")

    def test_every_failure_of_the_seam_is_a_stable_code(self):
        canned = support.canned_projection("__RELEASE_ID__")
        wrong_release = support.canned_projection("qcr-" + "0" * 64)
        broken_form = copy.deepcopy(canned)
        broken_form["parts"][2]["form"] = "document"
        missing_part = copy.deepcopy(canned)
        del missing_part["parts"][2]
        wrong_consumer = {**canned, "consumer": "surveyor"}
        cases = [
            ({"exit": 2, "stdout": ""}, "catalog_projection_failed"),
            ({"stdout": "not json"}, "catalog_projection_invalid"),
            ({"stdout": wrong_consumer}, "catalog_projection_consumer_mismatch"),
            ({"stdout": wrong_release}, "catalog_release_mismatch"),
            ({"stdout": {**canned, "document": "other/1"}}, "catalog_projection_invalid"),
            ({"stdout": broken_form}, "catalog_projection_invalid"),
            ({"stdout": missing_part}, "catalog_projection_invalid"),
        ]
        for behavior, code in cases:
            with self.subTest(code=code, behavior=str(behavior)[:40]):
                self.fake.set(behavior)
                with self.assertRaisesRegex(CatalogSelectionError, f"^{code}$"):
                    self.load()
        self.fake.set({"sleep": 3, "stdout": "{}"})
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_projection_failed$"):
            self.load(timeout=0.3)

    def test_unusable_commands_and_inputs_are_stable_codes(self):
        missing = [str(self.root / "no-such-command")]
        for argv, code in ((missing, "catalog_quartermaster_unavailable"), ([], "catalog_quartermaster_argv_invalid")):
            with self.subTest(code=code), self.assertRaisesRegex(CatalogSelectionError, f"^{code}$"):
                load_projection(self.release, self.overlay, argv)
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_input_unreadable$"):
            load_projection(self.root / "absent.json", self.overlay, [str(self.fake.path)])
        (self.root / "bad.json").write_text("[1]")
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_release_invalid$"):
            load_projection(self.root / "bad.json", self.overlay, [str(self.fake.path)])


class PreparationTests(unittest.TestCase):
    """The complete local-fixture spec is the existing eligible subject; the catalog only has to agree."""

    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.root = Path(self._directory.name)
        (self.root / "bin").mkdir()
        self.fake = FakeQuartermaster(self.root / "bin")
        self.fake.serve(support.canned_projection("ignored"))
        self.release = support.write_json(self.root / "release.json", support.fixture_release())
        self.overlay = support.write_json(self.root / "overlay.json", {"consumer": "caplab"})

    def ledger_with_spec(self, name):
        ledger, spec_path = self.root / name, self.root / f"{name}-spec.json"
        spec_path.write_bytes(canonical_json(rb.make_spec(rb.LedgerRegistrar(ledger))))
        return ledger, spec_path

    def prepare(self, name, *extra, entry="fixture-static-fixed", catalog=True):
        ledger, spec_path = self.root / name, self.root / f"{name}-spec.json"
        arguments = ["-m", "caplab.revbench", "prepare", "--spec", str(spec_path), "--ledger", str(ledger),
                     "--output", str(self.root / f"{name}-manifest.json")]
        if catalog:
            arguments += ["--catalog-release", str(self.release), "--catalog-overlay", str(self.overlay),
                          "--catalog-entry", entry, "--quartermaster-argv", json.dumps([str(self.fake.path)])]
        return run([*arguments, *extra], self.root)

    def test_catalog_selection_leaves_manifest_identity_alone_and_retains_exact_provenance(self):
        plain_ledger, _ = self.ledger_with_spec("plain")
        catalog_ledger, _ = self.ledger_with_spec("catalog")
        reference = self.root / "receipt-ref.json"

        baseline = self.prepare("plain", catalog=False)
        selected = self.prepare("catalog", "--catalog-reference-output", str(reference))

        self.assertEqual((baseline.returncode, selected.returncode), (0, 0), selected.stderr.decode())
        self.assertEqual(selected.stdout, baseline.stdout)  # historical manifest bytes and IDs are unchanged
        self.assertEqual((self.root / "catalog-manifest.json").read_bytes(), (self.root / "plain-manifest.json").read_bytes())
        self.assertFalse({"catalog-release", "catalog-selection"} & set(support.ledger_kinds(plain_ledger)))
        kinds = support.ledger_kinds(catalog_ledger)
        self.assertLess(kinds.index("catalog-selection"), kinds.index("revbench-manifest"))  # provenance first
        ledger = FilesystemQualificationLedger(catalog_ledger)
        receipt = json.loads(ledger.resolve(json.loads(reference.read_bytes())))
        self.assertEqual(ledger.resolve(receipt["sources"]["release_ref"]), self.release.read_bytes())
        self.assertEqual(ledger.resolve(receipt["sources"]["overlay_ref"]), self.overlay.read_bytes())
        projection = json.loads(ledger.resolve(receipt["sources"]["projection_ref"]))
        self.assertEqual(projection["projection_id"], receipt["projection"]["projection_id"])
        manifest = json.loads(baseline.stdout)
        self.assertEqual(receipt["manifest"], {"experiment_id": manifest["experiment_id"]})
        self.assertEqual(receipt["validated"]["binding_id"], manifest["binding"]["binding_id"])
        self.assertEqual(receipt["entry"]["declaration_id"], "fixture-static-fixed")
        self.assertEqual(receipt["configured_route"], {"resolution": "configured-route", "observed_at": None})
        self.assertEqual(set(receipt["disclosures"].values()), {False})
        self.assertEqual(receipt["projection"]["release_id"], json.loads(self.release.read_bytes())["release_id"])

    def test_each_disagreement_between_entry_and_spec_is_refused_before_any_ledger_change(self):
        cases = [
            ({"model_id": "other/model"}, "catalog_model_mismatch"),
            ({"native_harness_id": "other-harness"}, "catalog_harness_mismatch"),
            ({"effort": "other"}, "catalog_effort_mismatch"),
            ({"required_command_tokens": ["review", "--extra"]}, "catalog_native_tuple_not_admitted"),
            ({"executable": "/usr/bin/false"}, "catalog_native_tuple_not_admitted"),
        ]
        ledger, _ = self.ledger_with_spec("refused")
        before = support.tree_snapshot(ledger)
        for overrides, code in cases:
            with self.subTest(code=code, overrides=overrides):
                self.fake.serve(support.canned_projection("ignored", tuple_overrides=overrides))
                completed = self.prepare("refused")
                self.assertEqual((completed.returncode, completed.stdout, error_code(completed)), (2, b"", code))
                self.assertFalse((self.root / "refused-manifest.json").exists())
                self.assertEqual(support.tree_snapshot(ledger), before)

    def test_command_version_and_home_disagreements_are_named_when_the_policy_admits_the_tuple(self):
        registrar = rb.MemoryRegistrar()
        spec = rb.make_spec(registrar)
        projection = load_projection(self.release, self.overlay, [str(self.fake.path)])
        selection = select_entry(projection, "fixture-static-fixed")

        def policy_admitting(changes):
            document = json.loads(registrar.resolve(spec["native_system_contract_ref"]))
            document["systems"][rb.LOCAL_FIXTURE_TUPLE].update(changes)
            return {**spec, "native_system_contract_ref": rb.registered(
                registrar, f"policy-{sorted(changes)}", document, kind="native-agent-systems-contract",
                schema="caplab.native-agent-systems/v1")}

        validated = validate_against_spec(selection, spec, registrar)
        self.assertEqual((validated["model_id"], validated["profile_config_home"]), (rb.LOCAL_FIXTURE_MODEL, None))
        changed = {"required_command_tokens": ["review", "--extra"]}
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_command_mismatch$"):
            validate_against_spec(dataclasses.replace(selection, native={**selection.native, **changed}),
                                  policy_admitting(changed), registrar)
        changed = {"version_command": ["/usr/bin/true", "--version", "--extra"]}
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_version_command_mismatch$"):
            validate_against_spec(dataclasses.replace(selection, native={**selection.native, **changed}),
                                  policy_admitting(changed), registrar)
        with_home = dataclasses.replace(selection, profile={**selection.profile, "config_home": "/fixture/home"})
        with self.assertRaisesRegex(CatalogSelectionError, "^catalog_profile_home_mismatch$"):
            validate_against_spec(with_home, spec, registrar)

    def test_a_tuple_the_closed_policy_does_not_list_still_refuses_with_catalog_options_present(self):
        ledger, spec_path = self.root / "closed", self.root / "closed-spec.json"
        registrar = rb.LedgerRegistrar(ledger)
        binding, contract_ref = rb.make_executable_binding(registrar, Path("/usr/bin/true"))
        policy = json.loads(registrar.ledger.resolve(contract_ref))
        policy["systems"][rb.LOCAL_FIXTURE_TUPLE]["model_id"] = "someone-else/model"  # the binding's tuple is unlisted
        unlisted = rb.registered(rb.LedgerRegistrar(ledger), "closed-policy", policy,
                                 kind="native-agent-systems-contract", schema="caplab.native-agent-systems/v1")
        spec_path.write_bytes(canonical_json(rb.make_spec(registrar, binding=binding, native_system_contract_ref=unlisted)))
        before = support.tree_snapshot(ledger)

        completed = self.prepare("closed")

        self.assertEqual((completed.returncode, completed.stdout), (2, b""))
        self.assertIn("native_system_contract_ref", json.loads(completed.stderr)["message"])  # prepare's own refusal
        self.assertFalse((self.root / "closed-manifest.json").exists())
        self.assertEqual(support.tree_snapshot(ledger), before)

    def test_incomplete_catalog_arguments_and_a_missing_ledger_change_nothing(self):
        _, spec_path = self.ledger_with_spec("partial")
        partial = run(["-m", "caplab.revbench", "prepare", "--spec", str(spec_path), "--ledger",
                       str(self.root / "partial"), "--output", str(self.root / "out.json"),
                       "--catalog-release", str(self.release)], self.root)
        self.assertEqual((partial.returncode, error_code(partial)), (2, "catalog_arguments_incomplete"))

        absent = self.root / "no-ledger"
        (self.root / "no-ledger-spec.json").write_bytes(spec_path.read_bytes())
        completed = self.prepare("no-ledger")
        self.assertEqual((completed.returncode, error_code(completed)), (2, "catalog_ledger_missing"))
        self.assertFalse(absent.exists())  # refusing did not create a ledger
        self.assertEqual(self.fake.recorded(), [])  # and never reached Quartermaster

    def test_a_failing_quartermaster_changes_nothing_in_the_ledger(self):
        self.fake.set({"exit": 3})
        ledger, _ = self.ledger_with_spec("refused-seam")
        before = support.tree_snapshot(ledger)

        completed = self.prepare("refused-seam")

        self.assertEqual((completed.returncode, error_code(completed)), (2, "catalog_projection_failed"))
        self.assertEqual(support.tree_snapshot(ledger), before)


class LiveSourceBoundaryTests(unittest.TestCase):
    def test_the_pinned_live_source_invocation_does_not_accept_catalog_options(self):
        from contextlib import redirect_stderr
        from io import BytesIO, TextIOWrapper

        from caplab.revbench.__main__ import main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "spec.json").write_text("{}")
            raw = BytesIO()
            stderr = TextIOWrapper(raw, encoding="utf-8")
            with redirect_stderr(stderr):
                code = main(["prepare", "--spec", str(root / "spec.json"), "--ledger", str(root / "ledger"),
                             "--output", str(root / "out.json"), "--catalog-release", str(root / "r.json"),
                             "--catalog-overlay", str(root / "o.json"), "--catalog-entry", "e",
                             "--quartermaster-argv", '["quartermaster"]'], live_source=True)
            stderr.flush()
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(raw.getvalue())["code"], "catalog_selection_unavailable_in_live_source_invocation")
            self.assertFalse((root / "ledger").exists())


@unittest.skipUnless(support.INSTALLED and support.FIXED_SOURCE and Path(support.FIXED_SOURCE or ".").is_dir(),
                     "needs CAPLAB_TEST_QUARTERMASTER_SRC: a Quartermaster source with a null native home")
class NullNativeHomeEndToEndTests(unittest.TestCase):
    def test_the_envless_subject_is_selected_through_real_quartermaster_and_prepared(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = support.catalog_source(
                {**support.route("fixture-static", rb.LOCAL_FIXTURE_MODEL, harness="static-fixture", efforts=("fixed",),
                                 accounts=("fixture-account",), provider="caplab-local-fixture")})
            source["accounts"].append({"id": "fixture-account", "provider": "caplab-local-fixture",
                                       "billing": "subscription", "quota_pool_ids": []})
            source["profiles"].append({"id": "caplab-fixture", "host": "fixture-host", "consumer": "caplab",
                                       "account_id": "fixture-account", "config_home": None, "credential_ref": None})
            overlay = support.overlay()
            overlay["harnesses"]["static-fixture"] = {"efforts": ["fixed"], "native": {
                "native_harness_id": rb.LOCAL_FIXTURE_HARNESS, "executable": "/usr/bin/true",
                "version_command": ["/usr/bin/true", "--version"], "required_command_tokens": ["review"],
                "config_home": None}}
            overlay["accounts"]["fixture-account"] = {"runtime_id": "fixture", "population": "supervised-only"}
            release = publish(root, source)
            overlay_path = support.write_json(root / "overlay.json", overlay)
            ledger = root / "ledger"
            spec_path = root / "spec.json"
            spec_path.write_bytes(canonical_json(rb.make_spec(rb.LedgerRegistrar(ledger))))
            environment = dict(ENVIRONMENT, PYTHONPATH=os.pathsep.join([support.SOURCE, support.FIXED_SOURCE]))

            completed = subprocess.run(
                [sys.executable, "-m", "caplab.revbench", "prepare", "--spec", str(spec_path), "--ledger", str(ledger),
                 "--output", str(root / "manifest.json"), "--catalog-release", str(release),
                 "--catalog-overlay", str(overlay_path), "--catalog-entry", "fixture-static-fixture-account-fixed",
                 "--quartermaster-argv", json.dumps([sys.executable, "-m", "quartermaster"]),
                 "--catalog-reference-output", str(root / "receipt.json")],
                cwd=root, env=environment, capture_output=True, check=False)

            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            receipt = json.loads(FilesystemQualificationLedger(ledger).resolve(json.loads((root / "receipt.json").read_bytes())))
            self.assertEqual(receipt["entry"]["route_id"], "fixture-static")
            self.assertEqual(receipt["validated"]["profile_config_home"], None)


if __name__ == "__main__":
    unittest.main()
