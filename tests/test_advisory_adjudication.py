"""Judgments must cross the same validation boundary on every ingress."""
import json
from pathlib import Path
import tempfile
import unittest

from caplab.advisory.adjudication import Adjudications, append, build_adjudication


def judgment(**changes):
    return {"record": "caplab-control-adjudication/1", "dispatch_id": "control-a",
            "disposition": "sound", "basis": "Examined the declared control.",
            "basis_kind": "human-adjudication", "adjudicated_by": "principal:test",
            "as_of": "2026-09-08T12:00:00+00:00", "evidence": [], "notes": [],
            **changes}


class AdjudicationReadTest(unittest.TestCase):
    def test_malformed_judgment_cannot_enter_through_constructor_or_file(self):
        invalid = [
            {"dispatch_id": "control-a", "disposition": "sound"},
            judgment(record="foreign-record/1"), judgment(disposition="trusted"),
            judgment(basis_kind="model-opinion"), judgment(adjudicated_by="  "),
            judgment(basis=""), judgment(dispatch_id=""), judgment(as_of=""),
            judgment(basis_kind="mechanical-oracle", evidence=[]),
            judgment(evidence=["not an evidence object"]), judgment(notes=[1]),
            judgment(evidence=[{"value": float("nan")}]),
        ]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"judgments.jsonl"
            for record in invalid:
                with self.subTest(record=record):
                    with self.assertRaises(ValueError):
                        Adjudications([record])
                    path.write_text(json.dumps(record)+"\n")
                    with self.assertRaises(ValueError):
                        Adjudications.load(str(path))

    def test_duplicate_json_disposition_is_not_last_key_wins(self):
        raw = json.dumps(judgment()).replace('"disposition": "sound"',
                '"disposition": "defective", "disposition": "sound"')
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"judgments.jsonl"
            path.write_text(raw+"\n")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                Adjudications.load(str(path))

    def test_caller_mutation_cannot_change_loaded_or_aliased_judgment(self):
        record = judgment()
        loaded = Adjudications([record])
        loaded.alias("control-a", "substrate-a")
        record["disposition"] = "defective"
        self.assertEqual(loaded.disposition("control-a"), "sound")
        self.assertEqual(loaded.disposition("substrate-a"), "sound")

    def test_invalid_later_record_leaves_entire_append_batch_unwritten(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"judgments.jsonl"
            append(str(path), [judgment()])
            before = path.read_bytes()
            invalid = [judgment(dispatch_id="control-c", adjudicated_by=""),
                       judgment(dispatch_id="control-c", notes=["\ud800"]),
                       judgment(dispatch_id="control-c", evidence=[{"mixed": {1: "a", "b": "c"}}])]
            for bad in invalid:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    append(str(path), [judgment(dispatch_id="control-b"), bad])
                self.assertEqual(path.read_bytes(), before)
            absent = Path(root)/"new"/"judgments.jsonl"
            with self.assertRaises(ValueError):
                append(str(absent), [judgment(adjudicated_by="")])
            self.assertFalse(absent.parent.exists())

    def test_existing_principal_ruling_and_duplicate_precedence_are_preserved(self):
        first = judgment(disposition="defective")
        ruled = judgment(basis_kind="principal-ruling", basis="Décision: contrôle vérifié.")
        direct = judgment(dispatch_id="alias", disposition="unadjudicated",
                          basis="", adjudicated_by="")
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/"judgments.jsonl"
            path.write_text("\n".join(map(json.dumps, [first, ruled, direct]))+"\n")
            loaded = Adjudications.load(str(path))
            loaded.alias("control-a", "alias")
            self.assertEqual(loaded.disposition("control-a"), "sound")
            self.assertEqual(loaded.disposition("alias"), "unadjudicated")
            before = path.read_bytes()
            self.assertEqual(append(str(path), [first]), {"added": 0, "skipped_existing": 1})
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(Adjudications.load(str(Path(root)/"absent"))), 0)

    def test_builder_validates_and_owns_nested_evidence(self):
        fields = judgment(basis_kind="mechanical-oracle", evidence=[{"path": "check.py"}])
        fields.pop("record")
        built = build_adjudication(**fields)
        fields["evidence"][0]["path"] = "changed.py"
        self.assertEqual(built["evidence"], [{"path": "check.py"}])
        for update in ({"adjudicated_by": " "}, {"basis": ""}, {"notes": [False]}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                build_adjudication(**(fields | update))
