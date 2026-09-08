"""Exact session lookup in new synthetic trees; no native home access."""

import importlib.util
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from caplab.artifact_rater import CalibrationError
from caplab.ladder_subject import NativeSubjectError
import caplab.artifact_rater as rater


def load_script(name):
    path = Path(__file__).resolve().parents[1] / 'scripts' / (name + '.py')
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RATER = load_script('caplab-artifact-rater')
LADDER = load_script('caplab-ladder-subject')


class NativeSessionLookupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.sessions = self.home / '.codex/sessions'
        self.sessions.mkdir(parents=True)

    def candidate(self, thread='thread-123', *, day='08', name=None):
        path = self.sessions / day / (name or f'rollout-2026-09-{day}T10-20-30-{thread}.jsonl')
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b'synthetic bytes deliberately not parsed at lookup')
        return path

    def lookup(self, thread='thread-123', timeout=0):
        return rater.find_rollout(self.sessions, thread, timeout)

    def test_callers_reject_two_exact_candidates_instead_of_choosing_last(self):
        self.candidate(day='07')
        self.candidate(day='08')
        with patch.object(Path, 'home', return_value=self.home):
            for module, error in ((RATER, CalibrationError), (LADDER, NativeSubjectError)):
                with self.subTest(module=module.__name__), self.assertRaisesRegex(error, 'ambiguous'):
                    module._find_rollout('thread-123', 0)

    def test_callers_do_not_treat_ids_as_glob_patterns(self):
        self.candidate()
        with patch.object(Path, 'home', return_value=self.home):
            for module, error in ((RATER, CalibrationError), (LADDER, NativeSubjectError)):
                with self.subTest(module=module.__name__), self.assertRaises(error):
                    module._find_rollout('thread-12?', 0)

    def test_callers_reject_substring_session_matches(self):
        self.candidate('prefix-thread-123-suffix')
        with patch.object(Path, 'home', return_value=self.home):
            for module, error in ((RATER, CalibrationError), (LADDER, NativeSubjectError)):
                with self.subTest(module=module.__name__), self.assertRaises(error):
                    module._find_rollout('thread-123', 0)

    def test_exact_candidate_needs_no_body_read_and_preserves_source(self):
        expected = self.candidate()
        self.candidate('prefix-thread-123')
        self.candidate('thread-123-suffix')
        self.candidate(name='notes-thread-123.jsonl')
        before = expected.stat()
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('body read')):
            self.assertEqual(self.lookup(), expected)
        self.assertEqual(expected.stat().st_mtime_ns, before.st_mtime_ns)
        with patch.object(Path, 'home', return_value=self.home):
            self.assertEqual(RATER._find_rollout('thread-123', 0), expected)
            self.assertEqual(LADDER._find_rollout('thread-123', 0), expected)

    def test_missing_and_case_different_ids_do_not_match(self):
        self.candidate('THREAD-123')
        with self.assertRaisesRegex(CalibrationError, 'cannot locate'):
            self.lookup()

    def test_invalid_ids_and_deadlines_fail_before_traversal(self):
        for thread in ('', '*', '../x', 'x/y', 'x\\y', '[x]', '?', 'x\n', 'répo', None):
            with self.subTest(thread=thread), patch.object(os, 'walk') as walk:
                with self.assertRaises(CalibrationError):
                    self.lookup(thread)
                walk.assert_not_called()
        for timeout in (-1, True, float('inf'), float('nan'), '10'):
            with self.subTest(timeout=timeout), patch.object(os, 'walk') as walk:
                with self.assertRaises(CalibrationError):
                    self.lookup(timeout=timeout)
                walk.assert_not_called()

    def test_linked_candidate_is_not_opened_or_returned(self):
        expected = self.candidate()
        alias = expected.with_name(expected.name + '.original')
        expected.rename(alias)
        expected.symlink_to(alias)
        with self.assertRaisesRegex(CalibrationError, 'regular'):
            self.lookup()
        self.assertTrue(expected.is_symlink())

    def test_matching_directory_and_fifo_are_rejected_without_opening(self):
        expected = self.candidate()
        expected.unlink()
        expected.mkdir()
        with self.assertRaisesRegex(CalibrationError, 'regular'):
            self.lookup()
        expected.rmdir()
        os.mkfifo(expected)
        with self.assertRaisesRegex(CalibrationError, 'regular'):
            self.lookup()

    def test_linked_search_root_and_subdirectories_are_not_silently_skipped(self):
        expected = self.candidate()
        linked_root = self.home / 'linked'
        linked_root.symlink_to(self.sessions, target_is_directory=True)
        with self.assertRaisesRegex(CalibrationError, 'linked'):
            rater.find_rollout(linked_root, 'thread-123', 0)
        (self.sessions / 'alias').symlink_to(expected.parent, target_is_directory=True)
        with self.assertRaisesRegex(CalibrationError, 'linked'):
            self.lookup()

    def test_traversal_error_is_not_a_missing_session_or_valid_partial_search(self):
        def failed_walk(*args, **kwargs):
            kwargs['onerror'](PermissionError('fixture unreadable directory'))
            yield
        with patch.object(os, 'walk', side_effect=failed_walk):
            with self.assertRaisesRegex(CalibrationError, 'unreadable directory'):
                self.lookup()

    def test_root_metadata_failure_is_not_reported_as_a_valid_lookup(self):
        with patch.object(Path, 'resolve', side_effect=PermissionError('fixture root inaccessible')):
            with self.assertRaisesRegex(CalibrationError, 'root inaccessible'):
                self.lookup()

    def test_wait_can_observe_new_candidate_without_real_sleep(self):
        created = []
        def publish(_):
            created.append(self.candidate())
        with patch.object(rater.time, 'sleep', side_effect=publish):
            self.assertEqual(self.lookup(timeout=1), created[0])
        self.assertEqual(len(created), 1)


if __name__ == '__main__':
    unittest.main()
