"""Structural native-completion contracts independent of answer scoring."""

import json
import unittest

from caplab.codex_events import CodexEventError, codex_thread_id, require_completed_codex_turn


THREAD = {"type": "thread.started", "thread_id": "thread-1"}
START = {"type": "turn.started"}
COMPLETE = {"type": "turn.completed"}


def stream(*events):
    return "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events)


class CodexEventTests(unittest.TestCase):
    def test_valid_turn_allows_tool_events_and_unicode_text(self):
        capture = stream(THREAD, START, {"type": "item.completed", "item": {
            "type": "agent_message", "text": "café\u2028still one JSON line",
        }}, COMPLETE)
        for value in (capture, capture.encode(), capture.replace("\n", "\r\n").encode()):
            with self.subTest(value=value):
                self.assertEqual(require_completed_codex_turn(value), "thread-1")

    def test_partial_identity_is_not_a_completion_claim(self):
        for capture in (stream(THREAD), stream(THREAD, START)):
            self.assertEqual(codex_thread_id(capture), "thread-1")
            with self.assertRaises(CodexEventError):
                require_completed_codex_turn(capture)

    def test_identity_checks_the_whole_supplied_capture(self):
        for capture in (
            stream(THREAD, THREAD),
            stream(THREAD, {"type": "thread.started", "thread_id": "other"}),
            stream(THREAD) + '{"type":',
            stream({"type": "notice"}, THREAD),
            stream({"type": "thread.started", "thread_id": " "}),
        ):
            with self.subTest(capture=capture):
                with self.assertRaises(CodexEventError):
                    codex_thread_id(capture)

    def test_completion_requires_exact_lifecycle_and_terminal_boundary(self):
        for capture in (
            "", stream(START, COMPLETE), stream(THREAD, COMPLETE),
            stream(THREAD, START, START, COMPLETE),
            stream(THREAD, START, COMPLETE, COMPLETE),
            stream(THREAD, START, COMPLETE, {"type": "item.started"}),
            stream(THREAD, START, COMPLETE).rstrip("\n"),
            stream(THREAD, START, COMPLETE) + "\n",
        ):
            with self.subTest(capture=capture):
                with self.assertRaises(CodexEventError):
                    require_completed_codex_turn(capture)

    def test_later_completion_does_not_erase_failures(self):
        failures = [{"type": kind} for kind in ("error", "turn.failed", "thread.error")]
        failures.append({"type": "notice", "rate_limit_info": {"status": "rejected"}})
        for failure in failures:
            with self.subTest(failure=failure):
                with self.assertRaises(CodexEventError):
                    require_completed_codex_turn(stream(THREAD, START, failure, COMPLETE))

    def test_json_ambiguity_and_nonobjects_cannot_supply_evidence(self):
        for invalid in ('null', '[]', '{}', '{"type":1}',
                        '{"type":"turn.failed","type":"turn.completed"}',
                        '{"type":"notice","item":{"x":1,"x":2}}',
                        '{"type":"notice","value":NaN}', 'not-json'):
            with self.subTest(invalid=invalid):
                capture = stream(THREAD, START) + invalid + "\n" + stream(COMPLETE)
                with self.assertRaises(CodexEventError):
                    require_completed_codex_turn(capture)


if __name__ == "__main__":
    unittest.main()
