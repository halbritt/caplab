"""Trusted synthetic repair episodes; no native execution or study admission."""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from caplab.claude_capture_link import link_claude_root
from caplab.codex_capture_link import link_codex_final_message
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
import test_atomic_transfer_world as world


POLICY = Path(__file__).resolve().parents[1] / 'docs/product/contracts/native-agent-systems.json'
WITNESSES = (*world.REPAIRS, 'negatives/retry_only.py', 'negatives/false_success.py', None)
SESSION = '11111111-2222-4333-8444-555555555555'
CLAIM = 'Synthetic fixture claims repair complete. Café\u2028done.\n'
STDERR = b'synthetic diagnostic\x00\xff\r\n'
DIAGNOSTIC = b'synthetic private log\x00\xfe\n'
PRODUCER = '''import json, sys
from pathlib import Path
payload = json.loads(Path('/fixture/payload.json').read_bytes())
if payload['replacement'] is not None:
    Path('/work/transfer.py').write_bytes(bytes.fromhex(payload['replacement']))
for name, content in payload['artifacts'].items():
    path = Path('/episode') / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes.fromhex(content))
sys.stderr.buffer.write(bytes.fromhex(payload['stderr']))
sys.stdout.buffer.write(bytes.fromhex(payload['stdout']))
'''


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def jsonl(events):
    return ('\n'.join(json.dumps(e, ensure_ascii=False) for e in events) + '\n').encode()


def read_json(path):
    return json.loads(path.read_bytes())


def retained_file(attempt, phase, name):
    inventory = read_json(attempt / phase / 'inventory.json')
    entry, = [e for e in inventory['entries'] if e['path'] == name and e['kind'] == 'file']
    raw = (attempt / phase / entry['object']).read_bytes()
    assert (len(raw), digest(raw)) == (entry['bytes'], entry['sha256'])
    return raw


def run_fixture(root, harness, witness):
    """Run only enumerated authored witnesses; caller owns a fresh disposable root."""
    if harness not in ('codex', 'claude') or witness not in WITNESSES:
        raise ValueError('unknown synthetic fixture')
    root.mkdir(mode=0o700)
    task = root / 'task'; task.mkdir(mode=0o700)
    prepared = root / 'prepared'
    fixture = root / 'fixture'; fixture.mkdir(mode=0o700)
    task_bytes = (world.WORLD / 'TASK.md').read_bytes()
    parent = (world.WORLD / 'parent/transfer.py').read_bytes()
    replacement = None if witness is None else (world.WORLD / witness).read_bytes()
    (task / 'TASK.md').write_bytes(task_bytes)
    (task / 'transfer.py').write_bytes(parent)
    prompt = b'Synthetic capture integration fixture, not a native episode.\n' + task_bytes
    plan = build_native_capture_invocation(POLICY,
        'codex-terra-max' if harness == 'codex' else 'claude-fable-5-max',
        context=NativeCaptureContext('/work', '/episode', prompt, None if harness == 'codex' else SESSION))
    prep = prepare_native_runtime(POLICY, plan,
        expected_invocation_sha256=plan['invocation_sha256'], task_root=task, output_dir=prepared)
    runtime = prepared / 'runtime'
    sessions = Path(prep['capture_paths']['session_search_root']).relative_to(runtime)
    if harness == 'codex':
        stream = jsonl([{'type': 'thread.started', 'thread_id': 'fixture-root'},
            {'type': 'turn.started'},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'final', 'text': CLAIM}},
            {'type': 'turn.completed'}])
        transcript = jsonl([
            {'type': 'session_meta', 'payload': {'id': 'fixture-root', 'cli_version': 'synthetic-only'}},
            {'type': 'turn_context', 'payload': {'model': 'gpt-5.6-terra', 'effort': 'max'}},
            {'type': 'event_msg', 'payload': {'type': 'agent_message', 'message': CLAIM}}])
        session_path = sessions / 'rollout-2026-09-08T12-00-00-fixture-root.jsonl'
        diagnostic = Path(prep['capture_paths']['diagnostic_search_root']).relative_to(runtime) / 'fixture.log'
        artifacts = {'final-message.txt': CLAIM.encode()}
    else:
        stream = jsonl([{'type': 'system', 'subtype': 'init', 'session_id': SESSION},
            {'type': 'assistant', 'session_id': SESSION, 'parent_tool_use_id': None,
             'message': {'content': CLAIM}},
            {'type': 'result', 'session_id': SESSION, 'subtype': 'success', 'is_error': False}])
        transcript = jsonl([
            {'type': 'user', 'uuid': 'request', 'parentUuid': None, 'sessionId': SESSION,
             'message': {'role': 'user', 'content': prompt.decode()}},
            {'type': 'assistant', 'uuid': 'answer', 'parentUuid': 'request', 'sessionId': SESSION,
             'message': {'role': 'assistant', 'content': CLAIM}}])
        session_path = sessions / '-work' / (SESSION + '.jsonl')
        diagnostic = Path(prep['capture_paths']['diagnostic_file']).relative_to(runtime)
        artifacts = {}
    artifacts[str(session_path)] = transcript
    artifacts[str(diagnostic)] = DIAGNOSTIC
    # This producer is explicitly not the configured native command. The linker
    # must retain its existing executed_invocation_bound=False observation.
    payload = {'replacement': None if replacement is None else replacement.hex(),
               'stdout': stream.hex(), 'stderr': STDERR.hex(),
               'artifacts': {name: content.hex() for name, content in artifacts.items()}}
    (fixture / 'payload.json').write_text(json.dumps(payload), encoding='utf-8')
    (fixture / 'producer.py').write_text(PRODUCER, encoding='utf-8')
    command = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
        '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
        '--symlink', 'usr/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
        '--ro-bind', str(fixture), '/fixture', '--bind', str(task), '/work',
        '--bind', str(runtime), '/episode', '--chdir', '/work',
        '--setenv', 'PATH', '/usr/bin:/bin', '--', '/usr/bin/python3', '-B', '/fixture/producer.py']
    attempt = root / 'attempt'
    receipt = capture_task_attempt(command, task_root=task, environment={'PATH': '/usr/bin:/bin'},
        output_dir=attempt, limits=TaskCaptureLimits(100000, 100000, 100, 5))
    assert receipt['process']['return_code'] == 0, receipt['process']
    assert receipt['capture_complete'] is True
    collection = root / 'collection'
    collected = collect_native_outputs(POLICY, prepared,
        expected_preparation_sha256=digest((prepared / 'preparation.json').read_bytes()),
        output_dir=collection, max_receipt_bytes=100000, max_artifact_bytes=100000, max_entries=100)
    anchors = dict(expected_attempt_sha256=digest((attempt / 'attempt.json').read_bytes()),
                   expected_collection_sha256=digest((collection / 'collection.json').read_bytes()),
                   max_receipt_bytes=200000, max_identity_bytes=100000)
    linker = link_codex_final_message if harness == 'codex' else link_claude_root
    linked = linker(POLICY, attempt, collection, **anchors)
    # Cleanup is permitted only after collection and verification succeeded.
    for source in (task, prepared, fixture):
        shutil.rmtree(source)
    custody_before = {str(p.relative_to(root)): digest(p.read_bytes())
                      for p in root.rglob('*') if p.is_file()}
    assert linker(POLICY, attempt, collection, **anchors) == linked
    assert retained_file(attempt, 'before', 'transfer.py') == parent
    assert retained_file(attempt, 'before', 'TASK.md') == task_bytes
    assert retained_file(attempt, 'after', 'TASK.md') == task_bytes
    after = retained_file(attempt, 'after', 'transfer.py')
    assert after == (parent if replacement is None else replacement)
    assert (attempt / 'process/native.stdout').read_bytes() == stream
    assert (attempt / 'process/native.stderr').read_bytes() == STDERR
    invocation = read_json(collection / 'invocation.json')
    assert invocation['command'][-1].encode() == prompt
    retained_artifacts = {e['path']: (collection / 'objects' / e['object']).read_bytes()
                          for e in collected['entries'] if e['kind'] == 'file'}
    assert transcript in retained_artifacts.values()
    assert DIAGNOSTIC in retained_artifacts.values()
    # Only exact bytes of the allowlisted, authored witness execute here. This
    # is not a captured-code loader for untrusted attempts or a scoring API.
    namespace = {}
    exec(compile(after, '<retained-authored-transfer-fixture>', 'exec'), namespace)
    audit = world.oracle.audit(namespace['transfer'])
    assert custody_before == {str(p.relative_to(root)): digest(p.read_bytes())
                              for p in root.rglob('*') if p.is_file()}
    return {'schema': 'caplab.repair-capture-development-probe/v1', 'harness_layout': harness,
        'witness': witness, 'synthetic_only': True, 'native_execution': False, 'study_eligible': False,
        'sources_removed': True, 'anchors': anchors, 'link': linked, 'audit': audit,
        'changes': receipt['changes'], 'before_transfer_sha256': digest(parent),
        'after_transfer_sha256': digest(after), 'prompt_sha256': digest(prompt),
        'oracle_sha256': digest((world.WORLD / 'oracle.py').read_bytes()),
        'retained_task_bytes': receipt['retained_task_bytes'],
        'retained_artifact_bytes': sum(len(raw) for raw in retained_artifacts.values()),
        'process_stream_bytes': len(stream) + len(STDERR)}


@unittest.skipUnless(Path('/usr/bin/bwrap').is_file(), 'Bubblewrap required for contained fixture')
class RepairCaptureIntegrationTests(unittest.TestCase):
    def test_retained_repairs_and_negative_edits_remain_discriminating(self):
        with tempfile.TemporaryDirectory() as temporary:
            for harness in ('codex', 'claude'):
                for index, witness in enumerate(WITNESSES[:-1]):
                    with self.subTest(harness=harness, witness=witness):
                        report = run_fixture(Path(temporary) / f'{harness}-{index}', harness, witness)
                        self.assertEqual([c['path'] for c in report['changes']], ['transfer.py'])
                        checks = report['audit']['checks']
                        self.assertEqual(checks['fresh']['status'], 'passed')
                        if witness in world.REPAIRS:
                            self.assertTrue(all(c['status'] == 'passed' for c in checks.values()), checks)
                        else:
                            self.assertEqual(checks['retry']['status'], 'passed')
                            self.assertEqual(checks['before_statement_failure']['status'], 'failed')
                        root = report['link'].get('root_link', report['link'])
                        self.assertFalse(root['executed_invocation_bound'])
                        self.assertIsNone(root['native_capture_complete'])
                        self.assertFalse(report['audit']['study_eligible'])

    def test_completion_text_without_writes_keeps_unchanged_parent_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            for harness in ('codex', 'claude'):
                with self.subTest(harness=harness):
                    report = run_fixture(Path(temporary) / harness, harness, None)
                    self.assertEqual(report['changes'], [])
                    self.assertEqual(report['before_transfer_sha256'], report['after_transfer_sha256'])
                    checks = report['audit']['checks']
                    self.assertEqual(checks['fresh']['status'], 'passed')
                    self.assertEqual(checks['retry']['status'], 'failed')
                    self.assertEqual(checks['before_statement_failure']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
