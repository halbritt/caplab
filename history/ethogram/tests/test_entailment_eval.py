"""Hermetic tests for the claim-to-source entailment screening harness.

No real network: model calls go to an in-process ``http.server`` returning
canned OpenAI-style responses on the loopback interface.
"""

import hashlib
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "doctrine" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import entailment_eval  # noqa: E402


CHAPTER_TEXT = """# Chapter 1

Intro text outside the cited section.

## **<sup>2</sup>** Deep Modules

Deep modules provide powerful functionality behind simple interfaces.

### Sub-detail

Sub-detail body included in the section.

## Next Section

Excluded text after the section boundary.
"""

CANNED_VERDICT = {
    "verdict": "supported",
    "evidence_quote": "powerful functionality behind simple interfaces",
    "rationale": "The section states exactly that.",
}


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    chat_requests = []
    chat_content = (
        "Sure, here is my judgment after reading the section:\n"
        + json.dumps(CANNED_VERDICT)
        + "\nLet me know if you need anything else."
    )

    def _send(self, document):
        body = json.dumps(document).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/models"):
            self._send({"object": "list", "data": [{"id": "fake-judge-model"}]})
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        type(self).chat_requests.append(payload)
        self._send(
            {
                "model": "fake-judge-model",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "reasoning_content": "thinking tokens the harness must ignore",
                            "content": type(self).chat_content,
                        },
                    }
                ],
            }
        )

    def log_message(self, *args):
        pass


def write_synthetic_repo(root: Path, heading: str = "Deep Modules") -> Path:
    chapter = root / "books" / "fake-book" / "chapters" / "001-intro.md"
    chapter.parent.mkdir(parents=True)
    chapter.write_text(CHAPTER_TEXT, encoding="utf-8")
    concepts = root / "doctrine" / "concepts"
    concepts.mkdir(parents=True)
    document = {
        "schema_version": "agent-doctrine-concepts/1",
        "concepts": [
            {
                "id": "test-deep-modules",
                "claim": "Modules should hide complexity behind simple interfaces.",
                "source_support": [
                    {
                        "source_id": "SRC-FAKE",
                        "locator": f"books/fake-book/chapters/001-intro.md :: {heading}",
                        "contribution": "Defines deep modules as powerful functionality behind simple interfaces.",
                        "relationship": "direct_support",
                    }
                ],
            }
        ],
    }
    (concepts / "mini.yaml").write_text(json.dumps(document), encoding="utf-8")
    return chapter


class LocatorResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.chapter = write_synthetic_repo(self.root)

    def test_section_runs_until_next_same_or_higher_heading(self):
        resolution = entailment_eval.resolve_locator(
            self.root, "books/fake-book/chapters/001-intro.md :: Deep Modules"
        )
        self.assertIsNone(resolution.error)
        self.assertIn("powerful functionality", resolution.section_text)
        self.assertIn("Sub-detail body included", resolution.section_text)
        self.assertNotIn("Intro text", resolution.section_text)
        self.assertNotIn("Excluded text", resolution.section_text)
        self.assertEqual(
            hashlib.sha256(self.chapter.read_bytes()).hexdigest(),
            resolution.chapter_sha256,
        )

    def test_heading_markup_is_normalized_like_validate_doctrine(self):
        # The chapter heading carries converted superscript markup; the plain
        # locator heading must still resolve, matching the validator's rule.
        section = entailment_eval.extract_section(CHAPTER_TEXT, "Deep Modules")
        self.assertIsNotNone(section)

    def test_explicit_heading_occurrence_resolves_the_selected_section(self):
        chapter_text = (
            "# Chapter\n\n## Repeated\n\nFirst section.\n\n"
            "## Repeated\n\nSecond section.\n"
        )

        self.assertIsNone(entailment_eval.extract_section(chapter_text, "Repeated"))
        section = entailment_eval.extract_section(
            chapter_text, "Repeated @@ occurrence=2"
        )
        self.assertIn("Second section.", section)
        self.assertNotIn("First section.", section)

    def test_missing_heading_is_a_recorded_failure_not_a_crash(self):
        resolution = entailment_eval.resolve_locator(
            self.root, "books/fake-book/chapters/001-intro.md :: No Such Heading"
        )
        self.assertEqual("heading_not_found", resolution.error)
        self.assertIsNone(resolution.section_text)
        self.assertIsNotNone(resolution.chapter_sha256)

    def test_missing_file_and_malformed_locator(self):
        missing = entailment_eval.resolve_locator(self.root, "books/none.md :: X")
        self.assertEqual("file_missing", missing.error)
        malformed = entailment_eval.resolve_locator(self.root, "no separator here")
        self.assertEqual("malformed_locator", malformed.error)


class JsonExtractionTests(unittest.TestCase):
    def test_json_object_extracted_from_surrounding_prose(self):
        content = (
            "Let me think. The verdict follows:\n"
            '{"verdict": "partially_supported", "evidence_quote": "a {quoted} brace", '
            '"rationale": "Covers part of it."}\nHope that helps!'
        )
        parsed = entailment_eval.extract_json_object(content)
        self.assertEqual("partially_supported", parsed["verdict"])
        self.assertEqual("a {quoted} brace", parsed["evidence_quote"])

    def test_no_json_returns_none(self):
        self.assertIsNone(entailment_eval.extract_json_object("no json here"))


class JudgmentIdentityTests(unittest.TestCase):
    def judgment_key(self, **overrides):
        target = {
            "concept_id": "test-concept",
            "locator": "books/test.md :: Section",
            "claim": "Original claim.",
            "contribution": "Original contribution.",
            "relationship": "direct_support",
            "chapter_sha256": "chapter-sha",
            "section_sha256": "section-sha",
            "prompt_version": entailment_eval.PROMPT_VERSION,
            "model_alias": "judge-a",
            "served_model_id": "judge-a-build-1",
            "endpoint": "http://localhost:8081/v1",
            "max_tokens": 4096,
            "sampler_overrides": {},
        }
        target.update(overrides)
        return entailment_eval.record_key(**target)

    def test_key_binds_claim_relationship_prompt_model_and_request(self):
        baseline = self.judgment_key()

        for field, value in (
            ("claim", "Changed claim."),
            ("relationship", "refinement"),
            ("prompt_version", "prompt/next"),
            ("model_alias", "judge-b"),
            ("served_model_id", "judge-a-build-2"),
            ("endpoint", "http://other-host:8081/v1"),
            ("max_tokens", 2048),
            ("sampler_overrides", {"temperature": 0}),
        ):
            with self.subTest(field=field):
                self.assertNotEqual(baseline, self.judgment_key(**{field: value}))


class HarnessRunTests(unittest.TestCase):
    def setUp(self):
        FakeOpenAIHandler.chat_requests = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.endpoint = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.results = self.root / "results.jsonl"

    def run_harness(self, *extra):
        argv = [
            "--repo-root",
            str(self.root),
            "--results",
            str(self.results),
            "--endpoint",
            self.endpoint,
            *extra,
        ]
        return entailment_eval.main(argv)

    def read_records(self):
        return [
            json.loads(line)
            for line in self.results.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_record_carries_full_provenance(self):
        chapter = write_synthetic_repo(self.root)
        self.assertEqual(0, self.run_harness())
        records = self.read_records()
        self.assertEqual(1, len(records))
        record = records[0]
        chapter_sha = hashlib.sha256(chapter.read_bytes()).hexdigest()
        self.assertEqual("entailment-eval/2", record["schema_version"])
        self.assertEqual("test-deep-modules", record["concept_id"])
        self.assertEqual("SRC-FAKE", record["source_id"])
        self.assertEqual(chapter_sha, record["chapter_sha256"])
        self.assertEqual("direct_support", record["relationship"])
        self.assertIn("Defines deep modules", record["contribution"])
        self.assertFalse(record["truncated"])
        self.assertEqual("supported", record["verdict"])
        self.assertEqual(CANNED_VERDICT["evidence_quote"], record["evidence_quote"])
        self.assertEqual(CANNED_VERDICT["rationale"], record["rationale"])
        self.assertEqual("fake-judge-model", record["model"])
        self.assertEqual(self.endpoint, record["endpoint"])
        self.assertEqual(
            entailment_eval.MODEL_ALIAS, record["request_params"]["model_alias"]
        )
        self.assertEqual(
            entailment_eval.DEFAULT_MAX_TOKENS, record["request_params"]["max_tokens"]
        )
        self.assertGreaterEqual(record["latency_seconds"], 0.0)
        expected_key = entailment_eval.record_key(
            concept_id=record["concept_id"],
            locator=record["locator"],
            claim=record["claim"],
            contribution=record["contribution"],
            relationship=record["relationship"],
            chapter_sha256=chapter_sha,
            section_sha256=record["section_sha256"],
            prompt_version=record["prompt_version"],
            model_alias=record["request_params"]["model_alias"],
            served_model_id=record["request_params"]["served_model_id"],
            endpoint=record["endpoint"],
            max_tokens=record["request_params"]["max_tokens"],
            sampler_overrides=record["request_params"]["sampler_overrides"],
        )
        self.assertEqual(expected_key, record["key"])
        # The judged prompt contains the section, claim, contribution, and
        # relationship, and the request used the documented model alias.
        request = FakeOpenAIHandler.chat_requests[0]
        self.assertEqual(entailment_eval.MODEL_ALIAS, request["model"])
        prompt = request["messages"][0]["content"]
        self.assertIn("powerful functionality", prompt)
        self.assertIn("hide complexity behind simple interfaces", prompt)
        self.assertIn("direct_support", prompt)

    def test_source_inputs_and_screening_outputs_use_separate_roots(self):
        write_synthetic_repo(self.root)
        caplab_root = self.root / "caplab-output"
        results = (
            caplab_root
            / "doctrine"
            / "evaluations"
            / "entailment"
            / "results.jsonl"
        )

        completed = entailment_eval.main(
            [
                "--repo-root",
                str(caplab_root),
                "--pincite-root",
                str(self.root),
                "--endpoint",
                self.endpoint,
            ]
        )

        self.assertEqual(completed, 0)
        self.assertTrue(results.is_file())
        self.assertFalse(
            (self.root / "doctrine" / "evaluations" / "entailment").exists()
        )

    def test_resume_skips_existing_key_and_redo_rejudges(self):
        write_synthetic_repo(self.root)
        self.assertEqual(0, self.run_harness())
        self.assertEqual(1, len(FakeOpenAIHandler.chat_requests))
        self.assertEqual(0, self.run_harness())
        self.assertEqual(1, len(FakeOpenAIHandler.chat_requests))
        self.assertEqual(1, len(self.read_records()))
        self.assertEqual(0, self.run_harness("--redo"))
        self.assertEqual(2, len(FakeOpenAIHandler.chat_requests))
        records = self.read_records()
        self.assertEqual(2, len(records))
        self.assertEqual(records[0]["key"], records[1]["key"])

    def test_different_model_alias_has_distinct_resume_identity(self):
        write_synthetic_repo(self.root)
        self.assertEqual(0, self.run_harness("--model", "judge-a"))
        self.assertEqual(0, self.run_harness("--model", "judge-b"))

        records = self.read_records()
        self.assertEqual(2, len(records))
        self.assertNotEqual(records[0]["key"], records[1]["key"])

    def test_truncated_section_is_insufficient_context_without_model_call(self):
        chapter = write_synthetic_repo(self.root)
        chapter.write_text(
            "# Chapter 1\n\n## Deep Modules\n\n"
            + ("Relevant evidence appears throughout. " * 2000)
            + "\n\n## Next Section\n",
            encoding="utf-8",
        )

        self.assertEqual(0, self.run_harness())

        self.assertEqual([], FakeOpenAIHandler.chat_requests)
        record = self.read_records()[0]
        self.assertTrue(record["truncated"])
        self.assertEqual("insufficient_context", record["verdict"])
        self.assertEqual("section_exceeds_context_budget", record["error"])

    def test_evidence_quote_must_occur_in_the_complete_section(self):
        original = FakeOpenAIHandler.chat_content
        FakeOpenAIHandler.chat_content = json.dumps(
            {
                "verdict": "supported",
                "evidence_quote": "words the source never contains",
                "rationale": "Purported support.",
            }
        )
        self.addCleanup(setattr, FakeOpenAIHandler, "chat_content", original)
        write_synthetic_repo(self.root)

        self.assertEqual(0, self.run_harness())

        record = self.read_records()[0]
        self.assertEqual("quote_not_found", record["verdict"])
        self.assertEqual("supported", record["model_verdict"])
        self.assertEqual("evidence_quote_not_found_in_section", record["error"])

    def test_resolution_failure_is_recorded_without_model_call(self):
        write_synthetic_repo(self.root, heading="Heading That Does Not Exist")
        self.assertEqual(0, self.run_harness())
        self.assertEqual(0, len(FakeOpenAIHandler.chat_requests))
        records = self.read_records()
        self.assertEqual(1, len(records))
        self.assertEqual("resolution_failed", records[0]["verdict"])
        self.assertEqual("heading_not_found", records[0]["resolution_error"])
        self.assertIsNotNone(records[0]["chapter_sha256"])

    def test_dry_run_makes_no_requests_and_writes_nothing(self):
        write_synthetic_repo(self.root)
        self.assertEqual(0, self.run_harness("--dry-run"))
        self.assertEqual(0, len(FakeOpenAIHandler.chat_requests))
        self.assertFalse(self.results.exists())

    def test_summarize_writes_deterministic_summary(self):
        write_synthetic_repo(self.root)
        self.assertEqual(0, self.run_harness())
        self.assertEqual(0, self.run_harness("--summarize"))
        summary_path = self.results.parent / "summary.md"
        first = summary_path.read_text(encoding="utf-8")
        self.assertEqual(0, self.run_harness("--summarize"))
        self.assertEqual(first, summary_path.read_text(encoding="utf-8"))
        self.assertIn("| supported | 1 |", first)
        self.assertIn("SRC-FAKE", first)


class UnparseableContentTests(unittest.TestCase):
    def test_unparseable_content_retries_once_then_records_raw(self):
        FakeOpenAIHandler.chat_requests = []
        original = FakeOpenAIHandler.chat_content
        FakeOpenAIHandler.chat_content = "I refuse to emit JSON."
        self.addCleanup(setattr, FakeOpenAIHandler, "chat_content", original)
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        client = entailment_eval.OpenAIClient(
            f"http://127.0.0.1:{server.server_address[1]}/v1", 10.0, 64
        )
        outcome = entailment_eval.judge(client, "prompt")
        self.assertEqual("unparseable", outcome["verdict"])
        self.assertEqual("I refuse to emit JSON.", outcome["raw_content"])
        self.assertEqual(2, len(FakeOpenAIHandler.chat_requests))

    def test_transport_error_is_recorded_not_raised(self):
        # Port from a closed listener: connection refused on both attempts.
        probe = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
        port = probe.server_address[1]
        probe.server_close()
        client = entailment_eval.OpenAIClient(f"http://127.0.0.1:{port}/v1", 2.0, 64)
        outcome = entailment_eval.judge(client, "prompt")
        self.assertEqual("transport_error", outcome["verdict"])
        self.assertTrue(outcome["error"])


if __name__ == "__main__":
    unittest.main()
