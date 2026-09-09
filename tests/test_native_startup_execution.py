"""Sealed startup selections choose the strength of retained execution inspection."""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_launch_configuration import NativeLaunchContext, build_native_launch_configuration
from test_exec_trace import string, array

REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / 'docs/product/contracts/native-agent-systems.json'


class NativeStartupExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPO / 'scripts'))
        try:
            spec = importlib.util.spec_from_file_location('startup_execution', REPO / 'scripts/probe_native_capture_startup.py')
            cls.startup = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.startup)
        finally:
            sys.path.pop(0)

    def fixture(self, *, launch=True, requirement='absent', terminal=b''):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plan = build_native_capture_invocation(POLICY, 'codex-terra-max',
            context=NativeCaptureContext('/work', '/episode', 'Fixed café diagnostic.\n'.encode(), None))
        selected = {'harness': 'codex', 'plan': plan}
        if launch:
            selected['launch_configuration'] = build_native_launch_configuration(POLICY, plan,
                expected_invocation_sha256=plan['invocation_sha256'], context=NativeLaunchContext('canonical-native/v1'))
        if requirement != 'absent':
            selected['entrypoint_termination_required'] = requirement
        raw = ('73 execve(' + string('/toolbin/codex') + ', ' + array(plan['command']) + ', ' +
               array([k + '=' + v for k, v in plan['environment'].items()]) + ') = 0\n').encode() + terminal
        (root / 'codex-exec.trace').write_bytes(raw)
        (root / 'selections.json').write_text(json.dumps([selected]))
        (root / 'intent.json').write_text(json.dumps({'selections_sha256': self.startup.digest(root / 'selections.json')}))
        report = {'harness': 'codex', 'anchors': {'exec_trace_sha256': hashlib.sha256(raw).hexdigest()},
                  'handoff': {'peer_pid': 73, 'peer_checks': {'host_trace_path_exposed': False,
                      'tracer_namespaces': {'pid': {'supervisor': 'pid:[1]', 'peer': 'pid:[2]'}}}}}
        native = {'invocation_sha256': plan['invocation_sha256']}
        return root, report, native

    def test_legacy_selections_keep_exec_only_reports_without_terminal_evidence(self):
        for launch in (False, True):
            with self.subTest(launch=launch):
                root, report, native = self.fixture(launch=launch)
                before = deepcopy((report, native))
                result = self.startup.inspect_execution(root, report, native)
                self.assertTrue(result['exec_trace']['successful_execve_agrees'])
                self.assertNotIn('entrypoint_termination', result.get('launch_configuration', {}))
                if launch:
                    self.assertEqual(result['launch_configuration']['schema'], 'caplab.native-launch-exec-link/v1')
                self.assertEqual((report, native), before)
        report['anchors'] = {}
        self.assertEqual(self.startup.inspect_execution(root, report, native), {})
        root, report, native = self.fixture(requirement=False)
        self.assertNotIn('entrypoint_termination', self.startup.inspect_execution(root, report, native)['launch_configuration'])

    def test_shared_custody_caller_needs_no_startup_selection_without_execution_anchors(self):
        root, report, native = self.fixture()
        report['anchors'] = {}
        (root / 'selections.json').unlink(); (root / 'intent.json').unlink()
        before = {p.name: p.read_bytes() for p in root.iterdir()}
        self.assertEqual(self.startup.inspect_execution(root, report, native), {})
        self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)

    def test_new_selection_reports_entrypoint_outcome_despite_wrapper_failure(self):
        root, report, native = self.fixture(requirement=True,
            terminal=b'73 +++ exited with 0 +++\n72 +++ exited with 1 +++\n')
        result = self.startup.inspect_execution(root, report, native,
            expected_selections_sha256=self.startup.digest(root / 'selections.json'))
        outcome = result['launch_configuration']['entrypoint_termination']
        self.assertEqual(outcome['termination']['exit_code'], 0)
        self.assertFalse(outcome['task_success_verified'])
        self.assertFalse(result['launch_configuration']['study_eligible'])
        self.assertEqual(result['exec_trace'], outcome['exec_trace'])

    def test_requirement_cannot_fall_back_through_a_legacy_selection(self):
        for value in (True, None, 0, 1, 'true', [], {}):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                root, report, native = self.fixture(launch=False, requirement=value)
                self.startup.inspect_execution(root, report, native)

    def test_required_selection_cannot_omit_trace_or_selected_pid_termination(self):
        for terminal in (b'', b'74 +++ exited with 0 +++\n', b'73 +++ exited with 0 +++\n'*2):
            with self.subTest(terminal=terminal), self.assertRaises(ValueError):
                root, report, native = self.fixture(requirement=True, terminal=terminal)
                self.startup.inspect_execution(root, report, native)
        root, report, native = self.fixture(requirement=True)
        selection_anchor = self.startup.digest(root / 'selections.json')
        report['anchors'] = {}
        with self.assertRaisesRegex(RuntimeError, 'required termination needs an exec trace'):
            self.startup.inspect_execution(root, report, native, expected_selections_sha256=selection_anchor)
        (root / 'selections.json').unlink()
        with self.assertRaises(FileNotFoundError):
            self.startup.inspect_execution(root, report, native, expected_selections_sha256=selection_anchor)

    def test_wrong_or_malformed_selection_anchor_cannot_be_ignored(self):
        root, report, native = self.fixture(requirement=True, terminal=b'73 +++ exited with 0 +++\n')
        for anchor in ('0'*64, '', True, 0, [], {}, 'A'*64, '1'*63):
            with self.subTest(anchor=anchor), self.assertRaisesRegex(RuntimeError, 'selection anchor'):
                self.startup.inspect_execution(root, report, native, expected_selections_sha256=anchor)

    def test_independent_anchor_rejects_a_resealed_weaker_selection(self):
        root, report, native = self.fixture(requirement=True)
        expected = self.startup.digest(root / 'selections.json')
        selected = json.loads((root / 'selections.json').read_bytes())
        selected[0]['entrypoint_termination_required'] = False
        (root / 'selections.json').write_text(json.dumps(selected))
        (root / 'intent.json').write_text(json.dumps({'selections_sha256': self.startup.digest(root / 'selections.json')}))
        report['anchors'] = {}
        with self.assertRaisesRegex(RuntimeError, 'selection anchor differs'):
            self.startup.inspect_execution(root, report, native, expected_selections_sha256=expected)

    def test_selection_tamper_and_custody_contradiction_prevent_stronger_report(self):
        root, report, native = self.fixture(requirement=True, terminal=b'73 +++ exited with 0 +++\n')
        selected = json.loads((root / 'selections.json').read_bytes())
        del selected[0]['entrypoint_termination_required']
        (root / 'selections.json').write_text(json.dumps(selected))
        with self.assertRaisesRegex(RuntimeError, 'sealed intent'):
            self.startup.inspect_execution(root, report, native)
        root, report, native = self.fixture(requirement=True, terminal=b'73 +++ exited with 0 +++\n')
        report['handoff']['peer_checks']['host_trace_path_exposed'] = True
        with self.assertRaisesRegex(RuntimeError, 'custody isolation'):
            self.startup.inspect_execution(root, report, native)
        root, report, native = self.fixture(requirement=True, terminal=b'73 +++ exited with 0 +++\n')
        report['handoff']['peer_checks']['exec_tracer'] = {}
        with self.assertRaises(ValueError):
            self.startup.inspect_execution(root, report, native)
