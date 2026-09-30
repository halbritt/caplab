"""Durable retrieval run evidence: custody, accounting, interruption and tamper detection."""
from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from caplab.retrieval import artifacts, contracts, metrics
from caplab.retrieval.artifacts import ArtifactError, ArtifactIntegrityError, RunArtifacts, verify_run

from retrieval_evidence_support import attempt, make_spec, write_run


def writable(path: Path) -> Path:
    os.chmod(path, stat.S_IMODE(path.stat().st_mode) | 0o600)
    return path


class RunFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def copy_of(self, source: Path, name="copy") -> Path:
        target = self.root / name
        shutil.copytree(source, target)
        return target

    def objects(self, run: Path) -> list[Path]:
        return sorted((run / "ledger" / "objects").rglob("*") if (run / "ledger" / "objects").exists() else [])


class RecordingTests(RunFixture):
    def test_complete_run_is_sealed_verified_and_matches_recomputed_metrics(self):
        run, result = write_run(self.root, provenance={"runner": "fixture", "sources": [{"path": "/x", "sha256": "0" * 64}]})
        self.assertEqual((result["status"], result["complete"]), ("complete", True))
        self.assertEqual(sorted(p.name for p in run.output.iterdir()),
                         ["attempts.jsonl", "evidence.jsonl", "ledger", "manifest.json", "plan.json", "report.json"])
        verified = verify_run(run.output)
        self.assertTrue(verified["finished"])
        self.assertEqual(verified["manifest_sha256"], result["manifest_sha256"])
        self.assertEqual(len(verified["attempts"]), 12)  # 2 arms x 3 queries x 2 seeds
        self.assertEqual(verified["report"]["summary"], metrics.summarize(verified["spec"], verified["attempts"]))
        self.assertEqual(verified["verification"]["raw_artifacts_verified"], 36)
        self.assertEqual(verified["verification"]["unexpected_files"], [])
        for name in ("plan.json", "attempts.jsonl", "evidence.jsonl", "report.json", "manifest.json"):
            self.assertFalse(os.stat(run.output / name).st_mode & 0o222, f"{name} stays writable")

    def test_plan_is_sealed_before_any_retrieval_with_the_full_roster_and_pins(self):
        run = RunArtifacts(self.root / "run", make_spec(), provenance={"spec_source": {"sha256": "ab" * 32}})
        plan = json.loads((run.output / "plan.json").read_text())
        self.assertEqual(plan["schema_version"], "caplab-retrieval-plan/1")
        self.assertEqual(plan["roster"], contracts.assignments(run.spec))
        self.assertEqual(len(plan["roster"]), 12)
        self.assertEqual(plan["pins"]["spec_sha256"], contracts.spec_digest(run.spec))
        self.assertEqual(plan["provenance"], {"spec_source": {"sha256": "ab" * 32}})
        self.assertEqual((run.output / "attempts.jsonl").read_bytes(), b"")
        self.assertEqual(len(run.pending_assignments()), 12)

    def test_raw_bytes_are_kept_exactly_including_floats_and_invalid_utf8(self):
        run = RunArtifacts(self.root / "run", make_spec(arms=("good",), seeds=(0,)))
        row = run.pending_assignments()[0]
        weird = b'{"seconds": 1.50, "n": 1e400}\xff\xfe\x00 trailing'
        stored = run.record_attempt(attempt(row, ranked=["n1"]), raw={"response": weird, "stdout": b""})
        self.assertEqual(set(stored), {"assignment_id", "arm", "query_id", "seed", "status", "ranked_ids",
                                       "delivered_ids", "latency_ns", "error", "observation"})
        for row in run.pending_assignments():
            run.record_attempt(attempt(row, ranked=[]))
        run.finish()
        loaded = verify_run(run.output)
        entry = next(e for e in map(json.loads, (run.output / "evidence.jsonl").read_text().splitlines())
                     if e["kind"] == "attempt" and e["raw"])
        from caplab.qualification.ledger import FilesystemQualificationLedger
        ledger = FilesystemQualificationLedger(run.output / "ledger")
        self.assertEqual(ledger.resolve(entry["raw"]["response"]), weird)
        self.assertEqual(ledger.resolve(entry["raw"]["stdout"]), b"")
        self.assertEqual(loaded["report"]["references"]["raw_artifacts"][0]["role"], "response")

    def test_named_artifacts_are_idempotent_and_conflicts_are_refused(self):
        run = RunArtifacts(self.root / "run", make_spec())
        first = run.register_bytes("binary-identity", b'{"sha256": "00", "score": 0.5}', media_type="application/json")
        again = run.register_bytes("binary-identity", b'{"sha256": "00", "score": 0.5}', media_type="application/json")
        self.assertEqual(first, again)
        self.assertEqual(first["declared_media_type"], "application/json")
        with self.assertRaises(ArtifactError) as caught:
            run.register_bytes("binary-identity", b"other")
        self.assertEqual(caught.exception.code, "ARTIFACT_NAME_CONFLICT")
        self.assertEqual(run.register_bytes("arm." + "a" * 128 + ".stdout", b"long but valid")["byte_count"], 14)
        for bad_name in ("", "has space", "../escape", "x" * 300):
            with self.assertRaises(ArtifactError) as caught:
                run.register_bytes(bad_name, b"x")
            self.assertEqual(caught.exception.code, "NAME_INVALID")
        with self.assertRaises(ArtifactError) as caught:
            run.register_bytes("text", "not bytes")  # type: ignore[arg-type]
        self.assertEqual(caught.exception.code, "PAYLOAD_NOT_BYTES")

    def test_invalid_input_is_refused_before_anything_is_written(self):
        run = RunArtifacts(self.root / "run", make_spec())
        row = run.pending_assignments()[0]
        before = (run.output / "attempts.jsonl").read_bytes(), (run.output / "evidence.jsonl").read_bytes()
        bad_attempts = [
            attempt(row, ranked=["n1", "n1"]),                      # duplicate ranked id
            attempt(row, ranked=["n99"]),                           # unknown corpus id
            {**attempt(row, ranked=["n1"]), "gold": ["n1"]},        # gold labels never appear in attempts
            {**attempt(row, ranked=["n1"]), "seed": 99},            # unknown seed
            {**attempt(row, status="error"), "error": None},        # failure needs a structured error
        ]
        for bad in bad_attempts:
            with self.assertRaises(contracts.ContractError):
                run.record_attempt(bad)
        with self.assertRaises(ArtifactError) as caught:
            run.record_attempt(attempt(row, ranked=["n1"]), raw={"bad role!": b"x"})
        self.assertEqual(caught.exception.code, "NAME_INVALID")
        with self.assertRaises(ArtifactError) as caught:
            run.record_attempt(attempt(row, ranked=["n1"]), raw={"response": "text"})  # type: ignore[dict-item]
        self.assertEqual(caught.exception.code, "PAYLOAD_NOT_BYTES")
        self.assertEqual(before, ((run.output / "attempts.jsonl").read_bytes(), (run.output / "evidence.jsonl").read_bytes()))
        self.assertEqual(len(run.pending_assignments()), 12)

    def test_second_attempt_for_an_assignment_is_refused_not_overwritten(self):
        run = RunArtifacts(self.root / "run", make_spec())
        row = run.pending_assignments()[0]
        run.record_attempt(attempt(row, ranked=["n1"]))
        with self.assertRaises(ArtifactError) as caught:
            run.record_attempt(attempt(row, ranked=["n4"]))
        self.assertEqual(caught.exception.code, "DUPLICATE_ATTEMPT")
        self.assertEqual(len((run.output / "attempts.jsonl").read_text().splitlines()), 1)

    def test_an_existing_directory_or_link_is_refused_and_left_untouched(self):
        empty, filled, target = self.root / "empty", self.root / "filled", self.root / "target"
        for directory in (empty, filled, target):
            directory.mkdir()
        (filled / "keep.txt").write_text("precious")
        (self.root / "link").symlink_to(target, target_is_directory=True)
        (self.root / "dangling").symlink_to(self.root / "nowhere", target_is_directory=True)
        (self.root / "file").write_text("a file")
        for path in (empty, filled, self.root / "link", self.root / "dangling", self.root / "file"):
            with self.subTest(path=path.name), self.assertRaises(ArtifactError) as caught:
                RunArtifacts(path, make_spec())
            self.assertEqual(caught.exception.code, "OUTPUT_EXISTS")
        self.assertEqual(list(empty.iterdir()), [])
        self.assertEqual([p.name for p in filled.iterdir()], ["keep.txt"])
        self.assertEqual((filled / "keep.txt").read_text(), "precious")
        self.assertEqual(list(target.iterdir()), [])
        self.assertTrue((self.root / "dangling").is_symlink() and not (self.root / "nowhere").exists())
        self.assertEqual((self.root / "file").read_text(), "a file")

    def test_racing_creators_get_exactly_one_run(self):
        outcomes, barrier = [], threading.Barrier(4)

        def create():
            barrier.wait()
            try:
                RunArtifacts(self.root / "contested", make_spec())
                outcomes.append("created")
            except ArtifactError as error:
                outcomes.append(error.code)

        threads = [threading.Thread(target=create) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(outcomes), ["OUTPUT_EXISTS"] * 3 + ["created"])

    def test_output_must_be_new_and_provenance_must_be_finite_json(self):
        with self.assertRaises(ArtifactError) as caught:
            RunArtifacts(self.root / "missing-parent" / "run", make_spec())
        self.assertEqual(caught.exception.code, "OUTPUT_PARENT_MISSING")
        for provenance in ({"x": float("nan")}, {"x": object()}, ["not", "an", "object"]):
            with self.assertRaises(ArtifactError) as caught:
                RunArtifacts(self.root / "provenance", make_spec(), provenance=provenance)  # type: ignore[arg-type]
            self.assertEqual(caught.exception.code, "PROVENANCE_INVALID")
            self.assertFalse((self.root / "provenance").exists(), "a refused run must not leave a directory")
        bad_spec = make_spec()
        bad_spec["queries"][0]["relevant_ids"] = ["n99"]
        with self.assertRaises(contracts.ContractError):
            RunArtifacts(self.root / "spec", bad_spec)
        self.assertFalse((self.root / "spec").exists())

    def test_a_finished_run_accepts_no_more_evidence(self):
        run, _ = write_run(self.root)
        row = {"assignment_id": "good:q1:0", "arm": "good", "query_id": "q1", "seed": 0}
        with self.assertRaises(ArtifactError) as caught:
            run.record_attempt(attempt(row, ranked=[]))
        self.assertEqual(caught.exception.code, "RUN_FINISHED")
        for call in (run.finish, lambda: run.register_bytes("late", b"x")):
            with self.assertRaises(ArtifactError) as caught:
                call()
            self.assertEqual(caught.exception.code, "RUN_FINISHED")

    def test_concurrent_recording_keeps_one_valid_chain(self):
        run = RunArtifacts(self.root / "run", make_spec())
        rows = run.pending_assignments()
        errors = []

        def work(chunk):
            try:
                for row in chunk:
                    run.record_attempt(attempt(row, ranked=["n1"]), raw={"response": row["assignment_id"].encode()})
            except Exception as error:  # noqa: BLE001 - surfaced by the assertion below
                errors.append(error)

        threads = [threading.Thread(target=work, args=(rows[i::4],)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        run.finish()
        verified = verify_run(run.output)
        self.assertEqual(sorted(a["assignment_id"] for a in verified["attempts"]),
                         sorted(row["assignment_id"] for row in rows))


class AccountingTests(RunFixture):
    def test_missing_assignments_are_reported_not_turned_into_successes(self):
        skipped = {"good:q1:0", "good:q2:1", "bad:q3:0"}
        run, result = write_run(self.root, skip=skipped)
        self.assertEqual((result["status"], result["complete"]), ("incomplete", False))
        report = verify_run(run.output)["report"]
        self.assertEqual(set(report["run"]["missing_assignments"]), skipped)
        self.assertEqual((report["run"]["planned"], report["run"]["recorded"], report["run"]["missing"]), (12, 9, 3))
        coverage = report["denominators"]
        self.assertEqual((coverage["good"]["planned"], coverage["good"]["missing"], coverage["good"]["scorable"]), (6, 2, 4))
        self.assertEqual(coverage["bad"]["missing"], 1)
        controls = report["summary"]["arms"]["bad"]["cutoffs"]["3"]["controls"]
        self.assertEqual(controls["clean_all_assignments"]["denominator"], 2)  # planned controls, not just scored ones
        self.assertTrue(any("missing" in text for text in report["limitations"]))

    def test_failures_are_visible_and_are_never_clean_abstentions(self):
        run, result = write_run(self.root, spec=make_spec(arms=("good", "failing")))
        self.assertEqual(result["status"], "completed_with_failures")
        report = verify_run(run.output)["report"]
        self.assertEqual(report["run"]["failed_or_not_started"], 6)
        self.assertEqual({f["error_code"] for f in report["run"]["failures"]}, {"timeout"})
        failing = report["summary"]["arms"]["failing"]
        self.assertEqual(failing["coverage"]["scorable"], 0)
        controls = failing["cutoffs"]["3"]["controls"]
        self.assertEqual(controls["clean_all_assignments"]["numerator"], 0)
        self.assertEqual(controls["clean_all_assignments"]["denominator"], 2)

    def test_interrupted_and_not_started_work_is_accounted_for(self):
        overrides = {("good", "q1", 0): {"status": "interrupted"}, ("good", "q1", 1): {"status": "not_started"}}
        run, result = write_run(self.root, spec=make_spec(arms=("good",)), overrides=overrides)
        self.assertEqual(result["status"], "completed_with_failures")
        report = verify_run(run.output)["report"]
        by_status = report["run"]["by_status"]
        self.assertEqual((by_status["ok"], by_status["interrupted"], by_status["not_started"]), (4, 1, 1))
        self.assertEqual(report["denominators"]["good"]["not_started"], 1)

    def test_an_interrupted_run_keeps_its_plan_and_attempts_and_needs_explicit_consent_to_report(self):
        run, _ = write_run(self.root, finish=False, skip={"good:q3:1", "bad:q3:1"})
        with self.assertRaises(ArtifactIntegrityError) as caught:
            verify_run(run.output)
        self.assertEqual(caught.exception.code, "RUN_NOT_FINISHED")
        partial = verify_run(run.output, allow_unfinished=True)
        self.assertFalse(partial["finished"])
        self.assertIsNone(partial["manifest"])
        self.assertFalse(partial["report"]["run"]["finished"])
        self.assertEqual(partial["report"]["run"]["missing"], 2)
        self.assertEqual(partial["report"]["run"]["status"], "incomplete")
        self.assertTrue(any("not finished" in text for text in partial["report"]["limitations"]))
        self.assertFalse((run.output / "report.json").exists())

    def test_a_crash_between_evidence_and_attempt_leaves_orphan_evidence_not_a_phantom_attempt(self):
        run = RunArtifacts(self.root / "run", make_spec(arms=("good",), seeds=(0,)))
        rows = run.pending_assignments()
        real_append = artifacts._append

        def crash_on_attempts(path, data):
            if Path(path).name == "attempts.jsonl":
                raise OSError("disk vanished")
            real_append(path, data)

        with mock.patch.object(artifacts, "_append", crash_on_attempts):
            with self.assertRaises(OSError):
                run.record_attempt(attempt(rows[0], ranked=["n1"]), raw={"response": b"lost"})
        partial = verify_run(run.output, allow_unfinished=True)
        self.assertEqual(partial["verification"]["orphan_attempt_entries"], 1)
        self.assertEqual(partial["attempts"], [])
        self.assertEqual(partial["report"]["run"]["missing"], 3)
        for row in rows:  # the runner may retry; the orphan stays visible
            run.record_attempt(attempt(row, ranked=["n1"]))
        run.finish()
        final = verify_run(run.output)
        self.assertEqual(final["report"]["references"]["evidence"]["orphan_attempt_entries"], 1)
        self.assertEqual(final["report"]["run"]["status"], "complete")


class TamperTests(RunFixture):
    def setUp(self):
        super().setUp()
        run, _ = write_run(self.root, "original")
        self.original = run.output
        self.run = self.copy_of(self.original)

    def assertRejected(self, *codes):
        with self.assertRaises(ArtifactIntegrityError) as caught:
            verify_run(self.run)
        self.assertIn(caught.exception.code, codes, str(caught.exception))

    def edit(self, name, transform):
        path = writable(self.run / name)
        path.write_bytes(transform(path.read_bytes()))

    def test_the_untouched_copy_verifies(self):
        self.assertTrue(verify_run(self.run)["finished"])

    def test_an_edited_attempt_is_rejected(self):
        self.edit("attempts.jsonl", lambda data: data.replace(b'"ranked_ids":["n1","n4"]', b'"ranked_ids":["n4","n1"]', 1))
        self.assertRejected("ATTEMPT_WITHOUT_EVIDENCE")

    def test_a_removed_attempt_is_rejected(self):
        self.edit("attempts.jsonl", lambda data: b"\n".join(data.split(b"\n")[1:]))
        self.assertRejected("MANIFEST_MISMATCH")

    def test_a_duplicated_attempt_is_rejected(self):
        self.edit("attempts.jsonl", lambda data: data + data.split(b"\n")[0] + b"\n")
        self.assertRejected("ATTEMPT_DUPLICATE")

    def test_a_partial_last_line_is_rejected(self):
        self.edit("attempts.jsonl", lambda data: data + b'{"assignment_id":"good')
        self.assertRejected("ATTEMPTS_TRUNCATED")

    def test_an_attempt_that_no_longer_satisfies_the_contract_is_rejected(self):
        self.edit("attempts.jsonl", lambda data: data.replace(b'"ranked_ids":["n1","n4"]', b'"ranked_ids":["n1","n1"]', 1))
        self.assertRejected("ATTEMPT_INVALID")

    def test_a_modified_raw_object_is_rejected(self):
        target = next(path for path in self.objects(self.run) if path.is_file() and b"seconds" in path.read_bytes())
        writable(target.parent)
        writable(target).write_bytes(b'{"ranked_ids": [], "seconds": 9.99}')
        self.assertRejected("RAW_ARTIFACT_TAMPERED")

    def test_a_deleted_raw_object_is_rejected(self):
        target = next(path for path in self.objects(self.run) if path.is_file())
        writable(target.parent)
        target.unlink()
        self.assertRejected("RAW_ARTIFACT_TAMPERED")

    def test_a_dropped_or_reordered_evidence_entry_is_rejected(self):
        self.edit("evidence.jsonl", lambda data: b"\n".join(data.split(b"\n")[1:]))
        self.assertRejected("EVIDENCE_CHAIN_BROKEN")
        self.run = self.copy_of(self.original, "swap")
        self.edit("evidence.jsonl", lambda data: b"\n".join(reversed(data.rstrip(b"\n").split(b"\n"))) + b"\n")
        self.assertRejected("EVIDENCE_CHAIN_BROKEN")

    def test_a_rechained_index_with_malformed_entries_is_rejected_cleanly(self):
        # Even a forger who recomputes the whole hash chain gets a typed error, not a crash.
        entries = [json.loads(line) for line in (self.run / "evidence.jsonl").read_text().splitlines()]
        for change in (lambda e: e.pop("assignment_id"), lambda e: e.update(raw=["not", "a", "mapping"]),
                       lambda e: e.update(kind="artifact", ref={}), lambda e: e.update(raw={"response": "text"})):
            run = self.copy_of(self.original, f"rechained-{id(change)}")
            forged, previous = [], artifacts._GENESIS
            for index, original in enumerate(entries):
                body = {k: v for k, v in original.items() if k not in ("entry_sha256", "prev", "sequence")}
                if index == 0:
                    change(body)
                entry, line = artifacts._entry(previous, index, body.pop("kind"), body)
                forged.append(line)
                previous = entry["entry_sha256"]
            writable(run / "evidence.jsonl").write_bytes(b"".join(forged))
            with self.assertRaises(ArtifactIntegrityError) as caught:
                verify_run(run)
            self.assertIn(caught.exception.code, ("EVIDENCE_CHAIN_BROKEN", "RAW_ARTIFACT_TAMPERED", "RUN_MALFORMED"))

    def test_an_edited_evidence_reference_is_rejected(self):
        self.edit("evidence.jsonl", lambda data: data.replace(b'"byte_count":', b'"byte_count":1', 1))
        self.assertRejected("EVIDENCE_CHAIN_BROKEN")

    def test_an_edited_report_is_rejected(self):
        self.edit("report.json", lambda data: data.replace(b'"ok": 12', b'"ok": 13', 1))
        self.assertRejected("MANIFEST_MISMATCH", "REPORT_MISMATCH")

    def test_a_fully_reforged_report_that_disagrees_with_the_attempts_is_rejected(self):
        # The forger also re-registers the forged bytes and rewrites the manifest: only recomputing the
        # metrics from the retained attempts can expose this.
        from caplab.qualification.ledger import FilesystemQualificationLedger
        report = json.loads((self.run / "report.json").read_text())
        report["summary"]["arms"]["good"]["coverage"]["scorable"] = 0
        forged = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode()
        self.edit("report.json", lambda _: forged)
        ref = FilesystemQualificationLedger(self.run / "ledger").register_bytes(
            forged, kind="retrieval-report", schema="caplab-retrieval-raw/1")
        manifest = json.loads((self.run / "manifest.json").read_text())
        manifest["files"]["report.json"].update(sha256=artifacts.sha256_hex(forged), byte_count=len(forged), ledger=ref)
        self.edit("manifest.json", lambda _: (json.dumps(manifest, indent=2) + "\n").encode())
        self.assertRejected("REPORT_MISMATCH")

    def test_an_edited_plan_label_or_pin_is_rejected(self):
        self.edit("plan.json", lambda data: data.replace(b'"relevant_ids": [\n          "n1"\n        ]',
                                                            b'"relevant_ids": [\n          "n4"\n        ]', 1))
        self.assertNotEqual((self.run / "plan.json").read_bytes(), (self.original / "plan.json").read_bytes())
        self.assertRejected("PLAN_MISMATCH")

    def test_an_invalid_retained_spec_is_rejected(self):
        plan = json.loads((self.run / "plan.json").read_text())
        plan["spec"]["cutoffs"] = [0]
        self.edit("plan.json", lambda _: json.dumps(plan).encode())
        self.assertRejected("SPEC_INVALID")

    def test_an_edited_manifest_is_rejected(self):
        self.edit("manifest.json", lambda data: data.replace(b'"status": "complete"', b'"status": "incomplete"', 1))
        self.assertRejected("MANIFEST_MISMATCH")

    def test_a_missing_manifest_reads_as_an_unfinished_run_and_a_stray_report_is_flagged(self):
        (self.run / "manifest.json").unlink()
        self.assertRejected("RUN_NOT_FINISHED")
        with self.assertRaises(ArtifactIntegrityError) as caught:
            verify_run(self.run, allow_unfinished=True)
        self.assertEqual(caught.exception.code, "REPORT_WITHOUT_MANIFEST")

    def test_missing_files_and_directories_are_rejected_with_clear_codes(self):
        shutil.rmtree(self.run / "ledger")
        self.assertRejected("LEDGER_MISSING")
        self.run = self.copy_of(self.original, "no-plan")
        (self.run / "plan.json").unlink()
        self.assertRejected("FILE_MISSING")
        with self.assertRaises(ArtifactIntegrityError) as caught:
            verify_run(self.root / "does-not-exist")
        self.assertEqual(caught.exception.code, "RUN_MISSING")

    def test_a_symlinked_run_root_verifies_but_a_symlinked_member_file_does_not(self):
        link = self.root / "latest"
        link.symlink_to(self.run, target_is_directory=True)
        self.assertTrue(verify_run(link)["finished"])
        plan = self.run / "plan.json"
        moved = self.root / "elsewhere.json"
        shutil.copy(plan, moved)
        plan.unlink()
        plan.symlink_to(moved)
        self.assertRejected("FILE_MISSING")

    def test_unexpected_files_are_reported_without_failing(self):
        (self.run / "notes.txt").write_text("stray")
        self.assertEqual(verify_run(self.run)["verification"]["unexpected_files"], ["notes.txt"])


class HelperTests(unittest.TestCase):
    def test_structural_comparison_tolerates_only_float_noise(self):
        same = artifacts._same
        self.assertTrue(same({"a": [1, 2.0, {"b": "x"}]}, {"a": [1, 2.0 + 1e-13, {"b": "x"}]}))
        self.assertFalse(same({"a": 1}, {"a": 2}))
        self.assertFalse(same({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(same([1, 2], [1, 2, 3]))
        self.assertFalse(same(True, 1))
        self.assertFalse(same(0.5, 0.5001))
        self.assertFalse(same("1", 1))

    def test_file_identity_hashes_exact_bytes_and_reports_unreadable_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "binary"
            path.write_bytes(b"\x00\x01binary")
            identity = artifacts.file_identity(path)
            self.assertEqual(identity, {"path": str(path.resolve()), "sha256": artifacts.sha256_hex(b"\x00\x01binary"),
                                        "byte_count": 8})
            with self.assertRaises(ArtifactError) as caught:
                artifacts.file_identity(Path(directory) / "missing")
            self.assertEqual(caught.exception.code, "SOURCE_UNREADABLE")


if __name__ == "__main__":
    unittest.main()
