"""Hermetic tests for the doctrine adjudication web server.

Runs the server in-process against a temporary mini-repository with a fake
gold-queue builder; no network beyond loopback and no dependence on the
tailnet or the real evaluation files.
"""

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import adjudication_server  # noqa: E402
import entailment_eval  # noqa: E402

SECTION_BODY = (
    "The module owns its own decisions. **Deep modules** hide complexity "
    "behind a small interface, and the caller never repeats that knowledge."
)
CHAPTER_TEXT = "# Chapter One\n\n## The Section\n\n" + SECTION_BODY + "\n"
CONCEPT_ID = "mini-concept"
LOCATOR = "books/mini/chapters/001-intro.md :: The Section"
CONTRIBUTION = "Says the thing about deep modules."


def concept_formulation_id() -> str:
    digest = hashlib.sha256(
        "\0".join((CONCEPT_ID, LOCATOR, CONTRIBUTION)).encode()
    ).hexdigest()[:12]
    return f"F-CONCEPT-MINI-{digest}"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def existing_disposition() -> dict:
    return {
        "candidate_id": "gold-agent-role-review-agent",
        "adjudicator": {"kind": "human", "id": "fixture-human"},
        "adjudicated_at": "2026-07-10T00:00:00+00:00",
        "verdict": "abstention",
        "rationale": "Fixture scenario left the decision unowned.",
        "evidence_reviewed": ["doctrine/authority-model.yaml#role_defaults.review-agent"],
        "uncertainty": "Fixture-scale scenario only.",
    }


def candidate(identifier: str, kind: str, mode: str, references: list) -> dict:
    coverage = {
        "source_ids": [],
        "edge_relations": [],
        "support_relationships": [],
        "agent_roles": [],
        "risk_classes": [],
        "authority_transitions": [],
        "outcomes": [],
    }
    return {
        "schema_version": "doctrine-gold-candidate/1",
        "id": identifier,
        "candidate": {
            "generated_only": True,
            "kind": kind,
            "adjudication_mode": mode,
            "question": f"Fixture question for {identifier}?",
            "target": {
                "kind": references[0]["kind"],
                "id": references[0]["id"],
                "references": references,
            },
            "coverage": coverage,
        },
        "machine_screening": {"status": "not-run", "references": []},
        "human_disposition": {"status": "pending-human", "reference": None},
    }


def flagged_result_v1() -> dict:
    return {
        "schema_version": "entailment-eval/2",
        "prompt_version": entailment_eval.PROMPT_VERSION,
        "key": "a" * 64,
        "concept_id": CONCEPT_ID,
        "source_id": "SRC-MINI",
        "locator": LOCATOR,
        "relationship": "direct_support",
        "contribution": CONTRIBUTION,
        "claim": "Behavior belongs with the owner of its knowledge.",
        "chapter_sha256": "b" * 64,
        "resolution_error": None,
        "truncated": False,
        "section_chars": len(SECTION_BODY),
        "section_char_budget": 24000,
        "endpoint": "http://localhost:8081/v1",
        "request_params": {"model_alias": "fixture-model", "max_tokens": 4096},
        "judged_at": "2026-07-11T00:00:00+00:00",
        "model": "fixture-model",
        "verdict": "not_supported",
        "evidence_quote": "Deep modules hide complexity behind a small interface",
        "rationale": "Fixture screening rationale.",
        "error": None,
        "finish_reason": "stop",
        "latency_seconds": 1.25,
    }


def build_fixture(root: Path) -> Path:
    formulation_id = concept_formulation_id()
    write(root / "books/mini/chapters/001-intro.md", CHAPTER_TEXT)
    write(
        root / "doctrine/sources.yaml",
        "schema_version: fixture/1\n"
        "sources:\n"
        "  - id: SRC-MINI\n"
        "    title: Mini Book\n"
        "    corpus_path: books/mini\n",
    )
    write(
        root / "doctrine/graph/nodes.yaml",
        "schema_version: fixture/1\n"
        "nodes:\n"
        f"  - id: {CONCEPT_ID}\n"
        "    kind: principle\n"
        "    label: Mini concept\n"
        "    definition: Fixture node definition.\n",
    )
    write(
        root / "doctrine/graph/edges.yaml",
        "schema_version: fixture/1\nedges: []\n",
    )
    write(
        root / "doctrine/graph/formulations.yaml",
        "schema_version: fixture/1\n"
        "formulations:\n"
        f"  - id: {formulation_id}\n"
        "    source_id: SRC-MINI\n"
        f"    locator: 'books/mini/chapters/001-intro.md#The Section'\n"
        "    mappings:\n"
        f"      - node_id: {CONCEPT_ID}\n"
        "        relationship_to_canonical: direct_support\n"
        f"    paraphrase: {CONTRIBUTION}\n",
    )
    write(
        root / "doctrine/authority-model.yaml",
        "schema_version: fixture/1\n"
        "levels:\n"
        "  - id: observe\n"
        "    definition: Look without changing anything.\n"
        "  - id: diagnose\n"
        "    definition: Explain the observations.\n"
        "transitions:\n"
        "  - from: observe\n"
        "    to: diagnose\n"
        "    requires:\n"
        "      - a bounded question\n"
        "role_defaults:\n"
        "  review-agent:\n"
        "    usual_ceiling: recommend\n"
        "    constraints:\n"
        "      - do not self-accept\n",
    )
    write(
        root / "doctrine/context-lenses.yaml",
        "schema_version: fixture/1\n"
        "lenses:\n"
        "  - id: lens-mini\n"
        "    title: Mini lens\n"
        "    routing:\n"
        "      risk_classes: [regression]\n",
    )
    write(
        root / "doctrine/routing-index.yaml",
        "schema_version: fixture/1\n"
        "risk_routes:\n"
        "  - risk_class: regression\n"
        f"    concepts: [{CONCEPT_ID}]\n",
    )
    write(
        root / "doctrine/role-doctrine.md",
        "# Role Doctrine\n\n## Review agents\n\nFixture review-agent doctrine body.\n",
    )
    write(
        root / "doctrine/concepts/mini.yaml",
        "schema_version: fixture/1\n"
        "concepts:\n"
        f"  - id: {CONCEPT_ID}\n"
        "    claim: Behavior belongs with the owner of its knowledge.\n"
        "    decision_rule: Place behavior with its knowledge owner.\n"
        "    source_support:\n"
        "      - source_id: SRC-MINI\n"
        f"        locator: '{LOCATOR}'\n"
        f"        contribution: {CONTRIBUTION}\n"
        "        relationship: direct_support\n",
    )

    gold = root / "doctrine/evaluations/gold"
    for name in ("queue.schema.json", "human-dispositions.schema.json"):
        gold.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "doctrine/evaluations/gold" / name, gold / name)
    queue = {
        "schema_version": "doctrine-gold-queue/1",
        "generation": {
            "tool": "doctrine/tools/build_gold_queue.py",
            "tool_sha256": "0" * 64,
            "algorithm_version": "gold-queue-stratification/1",
            "input_sha256": {},
        },
        "records": [
            candidate(
                "gold-source-src-mini",
                "source-support",
                "direct-evidence-review",
                [
                    {"kind": "source", "id": "SRC-MINI"},
                    {"kind": "formulation", "id": formulation_id},
                    {"kind": "node", "id": CONCEPT_ID},
                ],
            ),
            candidate(
                "gold-agent-role-review-agent",
                "agent-role",
                "scenario-construction-and-review",
                [{"kind": "role", "id": "review-agent"}],
            ),
            candidate(
                "gold-risk-class-regression",
                "risk-class",
                "scenario-construction-and-review",
                [
                    {"kind": "risk-class", "id": "regression"},
                    {"kind": "lens", "id": "lens-mini"},
                ],
            ),
        ],
    }
    write(gold / "queue.json", json.dumps(queue, indent=2) + "\n")
    write(
        gold / "human-dispositions.json",
        json.dumps(
            {
                "schema_version": "doctrine-gold-human-dispositions/1",
                "dispositions": [existing_disposition()],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / "doctrine/evaluations/entailment/results.jsonl",
        json.dumps(flagged_result_v1())
        + "\n"
        + json.dumps(
            {
                **flagged_result_v1(),
                "schema_version": "entailment-eval/1",
                "prompt_version": None,
                "key": "c" * 64,
            }
        )
        + "\n",
    )
    write(
        root / "doctrine/evaluations/entailment/frontier-review.jsonl",
        json.dumps(
            {
                "schema_version": "frontier-review/1",
                "key": "a" * 64,
                "concept_id": CONCEPT_ID,
                "finding": "citation-defective",
                "confidence": "high",
                "rationale": "Fixture frontier rationale.",
                "evidence_quote": "",
                "proposed_fix": {
                    "relationship": "refinement",
                    "contribution": "Fixture corrected contribution.",
                },
                "local_verdict_assessment": "correct",
                "reviewer": {"kind": "model", "id": "fixture-frontier"},
                "reviewed_at": "2026-07-11T00:00:00+00:00",
            }
        )
        + "\n",
    )

    fake_builder = root / "fake_builder.py"
    write(
        fake_builder,
        "import json, sys\n"
        "from pathlib import Path\n"
        "log = Path(__file__).with_name('builder-calls.jsonl')\n"
        "with log.open('a', encoding='utf-8') as handle:\n"
        "    handle.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "print('fake builder ok')\n",
    )
    return fake_builder


class AccessGuardTests(unittest.TestCase):
    def test_loopback_and_tailnet_allowed_others_rejected(self) -> None:
        allowed = [
            "127.0.0.1",
            "127.8.9.10",
            "::1",
            "100.64.0.1",
            "100.85.100.81",
            "100.127.255.255",
            "::ffff:100.85.100.81",
            "::ffff:127.0.0.1",
        ]
        rejected = [
            "192.168.1.50",
            "10.0.0.5",
            "8.8.8.8",
            "100.63.255.255",
            "100.128.0.1",
            "fe80::1",
            "2001:db8::1",
            "::ffff:192.168.1.50",
            "not-an-address",
            "",
        ]
        for address in allowed:
            self.assertTrue(
                adjudication_server.client_allowed(address), f"should allow {address}"
            )
        for address in rejected:
            self.assertFalse(
                adjudication_server.client_allowed(address), f"should reject {address}"
            )


class ServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self.fake_builder = build_fixture(self.root)
        self.server = adjudication_server.AdjudicationServer(
            ("127.0.0.1", 0),
            adjudication_server.AdjudicationHandler,
            repo_root=self.root,
            builder_cmd=[sys.executable, str(self.fake_builder)],
        )
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self._tmp.cleanup()

    def request(self, method: str, path: str, body: dict | None = None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            payload = error.read().decode("utf-8")
            try:
                return error.code, json.loads(payload)
            except json.JSONDecodeError:
                return error.code, {"raw": payload}

    def disposition_body(self, candidate_id: str = "gold-source-src-mini") -> dict:
        return {
            "candidate_id": candidate_id,
            "verdict": "supported",
            "rationale": "The cited section states the mapped contribution directly.",
            "uncertainty": "Single-section reading; chapter context not re-read.",
            "evidence_reviewed": [LOCATOR, "doctrine/sources.yaml#SRC-MINI"],
            "adjudicator_id": "test-human",
        }

    def builder_calls(self) -> list:
        log = self.root / "builder-calls.jsonl"
        if not log.is_file():
            return []
        return [
            json.loads(line)
            for line in log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_ui_served_at_root(self) -> None:
        url = f"http://127.0.0.1:{self.port}/"
        with urllib.request.urlopen(url, timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("text/html", response.headers.get("Content-Type", ""))
            self.assertIn(b"Doctrine adjudication bench", response.read())

    def test_state_joins_and_resolves(self) -> None:
        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(
            state["progress"],
            {
                "queue_total": 3,
                "queue_adjudicated": 1,
                "flags_total": 1,
                "flags_audited": 0,
                "flags_stale_hidden": 1,
            },
        )

        by_id = {item["id"]: item for item in state["queue"]}
        source_candidate = by_id["gold-source-src-mini"]
        references = {ref["kind"]: ref for ref in source_candidate["references"]}
        self.assertTrue(references["source"]["resolved"])
        self.assertEqual(references["source"]["record"]["title"], "Mini Book")
        self.assertTrue(references["formulation"]["resolved"])
        self.assertIn(
            "Deep modules", references["formulation"]["section"]["text"]
        )
        self.assertTrue(references["node"]["resolved"])
        self.assertEqual(
            references["node"]["concept"]["claim"],
            "Behavior belongs with the owner of its knowledge.",
        )
        # Both generations of the fixture judgment match the formulation;
        # screening history is not generation-filtered (flags are).
        self.assertEqual(len(source_candidate["screening"]), 2)
        self.assertEqual(
            source_candidate["screening"][0]["match_basis"], "formulation-id"
        )

        role_candidate = by_id["gold-agent-role-review-agent"]
        self.assertIsNotNone(role_candidate["disposition"])
        role_ref = role_candidate["references"][0]
        self.assertTrue(role_ref["resolved"])
        self.assertIn("Fixture review-agent", role_ref["doctrine_section"]["text"])

        risk_candidate = by_id["gold-risk-class-regression"]
        risk_ref = risk_candidate["references"][0]
        self.assertTrue(risk_ref["resolved"])
        self.assertEqual(
            risk_ref["record"]["routed_by_lenses"][0]["id"], "lens-mini"
        )

        self.assertEqual(len(state["flags"]), 1)
        flag = state["flags"][0]
        self.assertEqual(flag["verdict"], "not_supported")
        self.assertIn("Deep modules", flag["section"]["text"])
        self.assertIn("directly supporting", flag["relationship_meaning"])
        self.assertIsNone(flag["audit"])
        self.assertEqual(flag["frontier"]["finding"], "citation-defective")
        self.assertEqual(flag["frontier"]["reviewer"]["kind"], "model")
        self.assertEqual(
            flag["frontier"]["proposed_fix"]["contribution"],
            "Fixture corrected contribution.",
        )

    def test_state_reports_unresolved_reference_instead_of_dropping_it(self) -> None:
        queue_path = self.root / "doctrine/evaluations/gold/queue.json"
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        queue["records"][0]["candidate"]["target"]["references"].append(
            {"kind": "node", "id": "no-such-node"}
        )
        queue_path.write_text(json.dumps(queue), encoding="utf-8")
        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        references = state["queue"][0]["references"]
        ghost = [ref for ref in references if ref["id"] == "no-such-node"]
        self.assertEqual(len(ghost), 1)
        self.assertFalse(ghost[0]["resolved"])
        self.assertIn("not present", ghost[0]["unresolved_reason"])
        self.assertEqual(ghost[0]["raw"], {"kind": "node", "id": "no-such-node"})

    def test_disposition_happy_path(self) -> None:
        status, payload = self.request(
            "POST", "/api/disposition", self.disposition_body()
        )
        self.assertEqual(status, 200, payload)
        self.assertTrue(payload["recorded"])
        self.assertEqual(payload["builder_write"]["returncode"], 0)
        self.assertEqual(payload["builder_check"]["returncode"], 0)
        self.assertEqual(
            payload["disposition"]["adjudicator"], {"kind": "human", "id": "test-human"}
        )
        self.assertIn("adjudicated_at", payload["disposition"])

        self.assertEqual(self.builder_calls(), [["--write"], ["--check"]])

        document = json.loads(
            (self.root / "doctrine/evaluations/gold/human-dispositions.json").read_text(
                encoding="utf-8"
            )
        )
        schema = json.loads(
            (
                self.root / "doctrine/evaluations/gold/human-dispositions.schema.json"
            ).read_text(encoding="utf-8")
        )
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors(document)), [])
        recorded = {item["candidate_id"] for item in document["dispositions"]}
        self.assertEqual(
            recorded, {"gold-source-src-mini", "gold-agent-role-review-agent"}
        )

        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(state["progress"]["queue_adjudicated"], 2)

    def test_disposition_duplicate_is_conflict(self) -> None:
        status, payload = self.request(
            "POST",
            "/api/disposition",
            self.disposition_body("gold-agent-role-review-agent"),
        )
        self.assertEqual(status, 409)
        self.assertIn("already has a human disposition", payload["error"])
        self.assertEqual(self.builder_calls(), [])

    def test_disposition_missing_rationale_is_rejected(self) -> None:
        body = self.disposition_body()
        body["rationale"] = "   "
        status, payload = self.request("POST", "/api/disposition", body)
        self.assertEqual(status, 400)
        self.assertIn("rationale", payload["error"])
        self.assertEqual(self.builder_calls(), [])

    def test_disposition_invalid_verdict_is_rejected(self) -> None:
        body = self.disposition_body()
        body["verdict"] = "definitely-fine"
        status, payload = self.request("POST", "/api/disposition", body)
        self.assertEqual(status, 400)
        self.assertIn("verdict", payload["error"])

    def test_disposition_unknown_candidate_is_not_found(self) -> None:
        status, payload = self.request(
            "POST", "/api/disposition", self.disposition_body("gold-no-such-candidate")
        )
        self.assertEqual(status, 404)
        self.assertIn("unknown candidate_id", payload["error"])

    def test_disposition_leaves_no_temp_litter(self) -> None:
        status, _ = self.request("POST", "/api/disposition", self.disposition_body())
        self.assertEqual(status, 200)
        gold = self.root / "doctrine/evaluations/gold"
        litter = [
            path.name for path in gold.iterdir() if ".tmp-" in path.name
        ]
        self.assertEqual(litter, [])

    def test_flag_audit_appends_and_reloads(self) -> None:
        body = {
            "key": "a" * 64,
            "finding": "citation-defective",
            "note": "Section describes interfaces, not the claimed contribution.",
            "reviewed_by": "test-human",
        }
        status, payload = self.request("POST", "/api/flag-audit", body)
        self.assertEqual(status, 200, payload)
        audit = payload["audit"]
        self.assertEqual(audit["schema_version"], "entailment-human-audit/1")
        self.assertEqual(audit["concept_id"], CONCEPT_ID)
        self.assertEqual(audit["locator"], LOCATOR)
        self.assertIn("reviewed_at", audit)

        audit_path = (
            self.root / "doctrine/evaluations/entailment/human-audit.jsonl"
        )
        lines = [
            json.loads(line)
            for line in audit_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["finding"], "citation-defective")

        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(state["progress"]["flags_audited"], 1)
        self.assertEqual(
            state["flags"][0]["audit"]["finding"], "citation-defective"
        )

        # multiple audits per key are allowed; the latest wins for display
        body["finding"] = "citation-holds"
        status, _ = self.request("POST", "/api/flag-audit", body)
        self.assertEqual(status, 200)
        status, state = self.request("GET", "/api/state")
        self.assertEqual(state["flags"][0]["audit"]["finding"], "citation-holds")
        self.assertEqual(state["flags"][0]["audit_count"], 2)

    def test_flag_audit_rejects_bad_finding_and_unknown_key(self) -> None:
        status, payload = self.request(
            "POST",
            "/api/flag-audit",
            {"key": "a" * 64, "finding": "looks-fine", "reviewed_by": "x"},
        )
        self.assertEqual(status, 400)
        self.assertIn("finding", payload["error"])

        status, payload = self.request(
            "POST",
            "/api/flag-audit",
            {"key": "f" * 64, "finding": "citation-holds", "reviewed_by": "x"},
        )
        self.assertEqual(status, 404)
        self.assertIn("not present", payload["error"])


if __name__ == "__main__":
    unittest.main()
