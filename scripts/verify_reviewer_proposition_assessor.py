"""Verify the frozen v2 administration and inspect proposition representation.

The v1 verifier remains immutable. Shared capture validation supplies guarded
custody checks; this method adds the distinct v2 output interpretation.
"""
import importlib.metadata
import json
from pathlib import Path
import sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'src'), str(Path(__file__).resolve().parent)]
from caplab.codex_events import parse_native_json
from reviewer_outcome_assessment import verify_capture
from reviewer_proposition_assessment import inspect_assessment
from reviewer_reddit_recovery_witness import runtime
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha

ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/proposition-assessor-1')
FIXTURE_SHA = '59bc7f1bb471b02bb3fc882bd57c30afc814e76025b5a2ee14f6f27d08f863b3'


def read(path):
    return parse_native_json(path.read_text())


def verify_administration():
    fixture, plan, launch, completion = [read(ROOT / name) for name in
        ('fixture-plan.json', 'plan.json', 'launch.json', 'completion.json')]
    if sha((ROOT / 'fixture-plan.json').read_bytes()) != FIXTURE_SHA or plan['fixture_plan_sha256'] != FIXTURE_SHA:
        raise ValueError('fixture drift')
    if sha((ROOT / 'plan.json').read_bytes()) != launch['plan_sha256']:
        raise ValueError('launch plan drift')
    if sha((ROOT / 'runner.py').read_bytes()) != plan['runner_sha256']:
        raise ValueError('executor drift')
    if launch['command'][-len(plan['actual_command']):] != plan['actual_command']:
        raise ValueError('effective native command mismatch')
    if completion['returncode'] != 0 or completion['termination'] != 'exit':
        raise ValueError('native attempt did not complete successfully')
    if inventory(ROOT / 'task') != fixture['task'] or runtime() != plan['runtime']:
        raise ValueError('input/runtime drift')
    for name, key in [('expected.json', 'expected_sha256'), ('prompt.txt', 'prompt_sha256')]:
        if sha((ROOT / name).read_bytes()) != fixture[key]:
            raise ValueError('expectations/prompt drift')
    for entry in plan['support']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('support drift')
    vendor = Path(plan['binary']).parent.parent
    for entry in plan['package_files']:
        if sha((vendor / entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('native package drift')
    verify_capture(ROOT, plan, completion)
    if {e['path'] for e in inventory(ROOT / 'capture')} != {e['path'] for e in completion['entries']}:
        raise ValueError('capture membership mismatch')
    return fixture, plan, completion


def inspect_native(completion):
    rollouts = list((ROOT / 'capture').glob('codex/sessions/*/*/*/rollout-*.jsonl'))
    if len(rollouts) != 1:
        raise ValueError('native session count mismatch')
    rows = [parse_native_json(line) for line in rollouts[0].read_text().splitlines()]
    metas = [r['payload'] for r in rows if r['type'] == 'session_meta']
    contexts = [r['payload'] for r in rows if r['type'] == 'turn_context']
    if len(metas) != 1 or metas[0]['cli_version'] != '0.153.4':
        raise ValueError('native harness mismatch')
    if not contexts or any(r['model'] != 'gpt-5.6-terra' or r['effort'] != 'max' for r in contexts):
        raise ValueError('native model/effort mismatch')
    stream = [parse_native_json(line) for line in (ROOT / 'capture/stdout').read_text().splitlines()]
    if [r['thread_id'] for r in stream if r['type'] == 'thread.started'] != [metas[0]['id']] or stream[-1]['type'] != 'turn.completed':
        raise ValueError('native stream/session mismatch')
    messages = [r['item']['text'] for r in stream if r['type'] == 'item.completed' and r['item']['type'] == 'agent_message']
    raw = (ROOT / 'capture/final-message.txt').read_bytes()
    if not messages or messages[-1].encode() != raw:
        raise ValueError('final detached from native stream')
    receipts = [read(ROOT / e['projection_receipt']) for e in completion['entries'] if e['disposition'] == 'projected-retained']
    native = {'thread_id': metas[0]['id'], 'observed_harness_version': metas[0]['cli_version'],
        'observed_model': contexts[0]['model'], 'observed_effort': contexts[0]['effort'],
        'captured_files': len(completion['entries']), 'opaque_fields_omitted': sum(len(r['omissions']) for r in receipts),
        'elapsed_seconds': completion['elapsed_seconds'], 'usage': stream[-1].get('usage'),
        'final_sha256': sha(raw), 'recorded_commands': [r['item']['command'] for r in stream
            if r['type'] == 'item.completed' and r['item']['type'] == 'command_execution'],
        'session_event_types': sorted({r['payload']['type'] for r in rows if r['type'] == 'event_msg'})}
    return raw, native


def verify():
    fixture, plan, completion = verify_administration()
    raw, native = inspect_native(completion)
    inspection = inspect_assessment(read(ROOT / 'task/reviews.json'), raw, ROOT / 'task', fixture['task'])
    return {'schema': 'caplab.proposition-assessor-development-verification/v1',
        'fixture_plan_sha256': FIXTURE_SHA, 'plan_sha256': sha((ROOT / 'plan.json').read_bytes()),
        'verifier_sha256': sha(Path(__file__).read_bytes()), 'jsonschema_version': importlib.metadata.version('jsonschema'),
        'native': native, 'inspection': inspection, 'expected_sha256': fixture['expected_sha256'],
        'semantic_support_verified': False, 'scorer_accepted': False, 'ranking_eligible': False,
        'limits': ['Representation checks and literal evidence identity do not establish complete or correct semantic decomposition.',
                   'Content inspection against the frozen expectations remains necessary.',
                   'Known regression cases from one exposed change do not establish generalization.']}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
