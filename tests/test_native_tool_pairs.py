import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.native_tool_pairs import build_native_tool_pair_report


def encoded(events):
    return b"".join((json.dumps(e, ensure_ascii=False) + "\n").encode() for e in events)


def claude(kind, **fields):
    return {"type": kind, "session_id": "root", "parent_tool_use_id": None, **fields}


def request(native_id="call", **scope):
    return claude("assistant", message={"content": [
        {"type": "tool_use", "id": native_id, "name": "Bash", "input": {"command": "check café"}}]}, **scope)


def result(native_id="call", **scope):
    return claude("user", message={"content": [
        {"type": "tool_result", "tool_use_id": native_id, "content": "failed", "is_error": True}]}, **scope)


def item(phase, native_id="call", kind="command_execution", **fields):
    return {"type": "item." + phase, "item": {"id": native_id, "type": kind, **fields}}


class NativeToolPairTests(unittest.TestCase):
    def report(self, events, format="claude-stream-jsonl"):
        content = encoded(events)
        return build_native_tool_pair_report(content, format=format,
            expected_sha256=hashlib.sha256(content).hexdigest(), expected_root_id="root", max_bytes=len(content))

    def test_claude_partial_input_is_not_a_second_call_or_execution_success(self):
        events = [claude("system", subtype="init"),
            claude("stream_event", event={"type": "content_block_start", "content_block":
                   {"type": "tool_use", "id": "call", "name": "Bash", "input": {}}}),
            request(), result(), claude("result", subtype="success")]
        report = self.report(events)
        self.assertEqual(report["status_counts"], {"paired": 1})
        group = report["groups"][0]
        self.assertEqual([r["line"] for r in group["partials"]], [2])
        self.assertEqual([r["line"] for r in group["requests"]], [3])
        self.assertTrue(group["results"][0]["reported_outcome"]["is_error"])
        self.assertIsNone(report["work_correctness"])
        self.assertIsNone(report["capture_complete"])
        self.assertFalse(report["native_execution_linked"])
        raw_lines = encoded(events).splitlines(keepends=True)
        for locator, raw in zip(report["events"], raw_lines):
            self.assertEqual(locator["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(encoded(events)[locator["byte_offset"]:locator["byte_offset"] + locator["bytes"]], raw)

    def test_codex_interleaved_items_pair_by_id_and_retain_failed_exit(self):
        events = [{"type": "thread.started", "thread_id": "root"},
            item("started", "a"), item("started", "b"), item("updated", "a"),
            item("completed", "b", status="failed", exit_code=7),
            item("completed", "a", status="completed", exit_code=0),
            {"type": "turn.completed"}]
        report = self.report(events, "codex-exec-jsonl")
        self.assertEqual(report["status_counts"], {"paired": 2})
        groups = {g["native_id"]: g for g in report["groups"]}
        self.assertEqual(groups["a"]["results"][0]["line"], 6)
        self.assertEqual(groups["b"]["results"][0]["reported_outcome"], {"status": "failed", "exit_code": 7})
        self.assertEqual(len(groups["a"]["updates"]), 1)
        self.assertIsNone(report["work_correctness"])

    def test_final_prose_does_not_complete_partial_or_pending_calls(self):
        events = [claude("system", subtype="init"), request("pending"),
            claude("stream_event", event={"type": "content_block_start", "content_block":
                   {"type": "tool_use", "id": "partial", "name": "Edit"}}),
            claude("assistant", message={"content": [{"type": "text", "text": "All tests passed."}]}),
            claude("result", subtype="success")]
        report = self.report(events)
        self.assertEqual(report["status_counts"], {"request_without_result": 1, "partial_or_update_only": 1})
        self.assertEqual(len(report["outcome_records"]), 1)

    def test_child_scope_cannot_supply_a_root_result(self):
        for scope in ({"parent_tool_use_id": "parent"},
                      {"parent_tool_use_id": "parent", "session_id": "child"}):
            with self.subTest(scope=scope):
                report = self.report([claude("system", subtype="init"), request(), result(**scope)])
                self.assertEqual(report["status_counts"], {"request_without_result": 1, "result_without_request": 1})

    def test_repeated_or_reordered_records_remain_ambiguous(self):
        for sequence, issue in (([request(), request(), result()], "duplicate_request"),
                                ([request(), result(), result()], "duplicate_result"),
                                ([result(), request()], "result_not_after_request")):
            with self.subTest(issue=issue):
                report = self.report([claude("system", subtype="init"), *sequence])
                self.assertEqual(report["status_counts"], {"ambiguous": 1})
                self.assertIn(issue, report["groups"][0]["issues"])
        report = self.report([{"type": "thread.started", "thread_id": "root"},
            item("started"), item("completed", kind="file_change")], "codex-exec-jsonl")
        self.assertIn("conflicting_identity", report["groups"][0]["issues"])

    def test_unclassified_events_and_blocks_remain_locatable(self):
        report = self.report([claude("system", subtype="init"),
            claude("assistant", message={"content": [{"type": "future_tool"}]}),
            claude("stream_event", event={"type": "content_block_stop", "index": 0}),
            claude("system", subtype="compact_boundary"), claude("future_event")])
        self.assertEqual([r["line"] for r in report["unclassified"]], [2, 3, 5])
        self.assertEqual(report["compaction_records"], [{"line": 4, "pointer": ""}])
        self.assertEqual(len(report["events"]), 5)
        self.assertEqual(report["status_counts"], {})

    def test_invalid_framing_identity_and_tool_shapes_fail_closed(self):
        good = encoded([claude("system", subtype="init")])
        bad_bytes = [good[:-1], good + b"\n", good + b"\xff\n", good + b'{"type":"x","type":"y"}\n']
        bad_events = [[claude("system", subtype="init"), claude("system", subtype="init")],
            [claude("system", subtype="init", parent_tool_use_id="child")],
            [claude("system", subtype="init"), request(session_id="other")],
            [claude("system", subtype="init"), claude("assistant", message={"content": [
                {"type": "tool_use", "id": "x", "name": "Bash", "input": "not-an-object"}]})],
            [{"type": "thread.started", "thread_id": "other"}]]
        for content in bad_bytes + [encoded(e) for e in bad_events]:
            with self.subTest(content=content), self.assertRaises(ValueError):
                build_native_tool_pair_report(content, format="claude-stream-jsonl",
                    expected_sha256=hashlib.sha256(content).hexdigest(), expected_root_id="root", max_bytes=len(content))
        for digest, bound in (("0" * 64, len(good)), (hashlib.sha256(good).hexdigest(), len(good) - 1)):
            with self.subTest(digest=digest, bound=bound), self.assertRaises(ValueError):
                build_native_tool_pair_report(good, format="claude-stream-jsonl", expected_sha256=digest,
                                             expected_root_id="root", max_bytes=bound)
        with self.assertRaises(ValueError):
            self.report([{"type": "thread.started", "thread_id": "root"},
                         {**item("started"), "thread_id": "other"}], "codex-exec-jsonl")

    def test_cli_requires_the_anchored_bounded_source_and_emits_only_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root, "stdout.jsonl")
            content = encoded([claude("system", subtype="init"), request(), result()])
            path.write_bytes(content)
            cmd = [sys.executable, "scripts/native_tool_pairs.py", str(path), "--format", "claude-stream-jsonl",
                   "--expected-sha256", hashlib.sha256(content).hexdigest(), "--expected-root-id", "root", "--max-bytes"]
            done = subprocess.run(cmd + [str(len(content))], capture_output=True, check=True)
            report = json.loads(done.stdout)
            self.assertEqual(report["status_counts"], {"paired": 1})
            self.assertNotIn(b"check caf", done.stdout)
            rejected = subprocess.run(cmd + [str(len(content) - 1)], capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout, b"")
