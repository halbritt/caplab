"""Verify natural-review administration without assigning reviewer scores."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reviewer_outcome_assessment import verify_capture
from reviewer_scheduler_witness import inventory
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    preparation, plan, launch, completion = [read(root / name) for name in
        ('preparation.json', 'plan.json', 'launch.json', 'completion.json')]
    if (sha(root / 'preparation.json') != plan['preparation_sha256']
            or sha(root / 'plan.json') != launch['plan_sha256']
            or sha(root / 'runner.py') != plan['runner_sha256']
            or sha(root / 'assessment-obligations.json') != plan['assessment_obligations_sha256']):
        raise ValueError('administration identity mismatch')
    if completion['returncode'] != 0 or completion['termination'] != 'exit':
        raise ValueError('native review did not complete')
    if inventory(root / 'task') != preparation['task'] or inventory(root / 'dependencies') != preparation['dependencies']:
        raise ValueError('task or dependency drift')
    for row in preparation['support'] + preparation['runtime']:
        if sha(Path(row['path'])) != row['sha256']:
            raise ValueError('support or runtime drift')
    package = Path(plan['binary']).parent.parent
    for row in plan['package_files']:
        if sha(package / row['path']) != row['sha256']:
            raise ValueError('native package drift')
    if sha(Path('/home/halbritt/.codex/auth.json')) != plan['credential_pins']['expected_source_sha256']:
        raise ValueError('owner authentication cache changed')
    verify_capture(root, plan, completion)
    capture_paths = {row['path'] for row in inventory(root / 'capture')}
    if capture_paths != {row['path'] for row in completion['entries']}:
        raise ValueError('unaccounted capture membership')
    rollouts = list((root / 'capture').glob('codex/sessions/*/*/*/rollout-*.jsonl'))
    if len(rollouts) != 1:
        raise ValueError('unexpected native session count')
    rows = [json.loads(line) for line in rollouts[0].read_text().splitlines()]
    metas = [row['payload'] for row in rows if row['type'] == 'session_meta']
    contexts = [row['payload'] for row in rows if row['type'] == 'turn_context']
    if len(metas) != 1 or metas[0]['cli_version'] != '0.153.4':
        raise ValueError('unexpected native harness identity')
    if not contexts or any(row['model'] != 'gpt-5.6-terra' or row['effort'] != 'max' for row in contexts):
        raise ValueError('unexpected observed model or effort')
    stream = [json.loads(line) for line in (root / 'capture/stdout').read_text().splitlines()]
    if [row['thread_id'] for row in stream if row['type'] == 'thread.started'] != [metas[0]['id']]:
        raise ValueError('native stream and rollout disagree')
    if not stream or stream[-1]['type'] != 'turn.completed':
        raise ValueError('native turn did not finish')
    messages = [row['item']['text'] for row in stream
                if row['type'] == 'item.completed' and row['item']['type'] == 'agent_message']
    if not messages or messages[-1].encode() != (root / 'capture/final-message.txt').read_bytes():
        raise ValueError('final review differs from native output')
    commands = [row['item']['command'] for row in stream
                if row['type'] == 'item.completed' and row['item']['type'] == 'command_execution']
    tools = [row['payload'] for row in rows if row['type'] == 'response_item'
             and row['payload'].get('type') in ('function_call', 'custom_tool_call')]
    projections = [read(root / row['projection_receipt']) for row in completion['entries']
                   if row['disposition'] == 'projected-retained']
    readiness = []
    for role in ('base', 'current'):
        check_process(root / ('readiness-' + role))
        readiness.append({'role': role, 'completion_sha256': sha(root / ('readiness-' + role) / 'completion.json'),
                          'stdout_sha256': sha(root / ('readiness-' + role) / 'stdout'),
                          'tests_xml_sha256': sha(root / ('readiness-' + role + '-capture') / 'tests.xml')})
    return {'schema': 'caplab.natural-review-administration/v1', 'thread_id': metas[0]['id'],
        'observed_cli_version': metas[0]['cli_version'], 'observed_model': 'gpt-5.6-terra', 'observed_effort': 'max',
        'plan_sha256': sha(root / 'plan.json'), 'preparation_sha256': sha(root / 'preparation.json'),
        'verifier_sha256': sha(Path(__file__)), 'final_sha256': sha(root / 'capture/final-message.txt'),
        'rollout_sha256': sha(rollouts[0]), 'elapsed_seconds': completion['elapsed_seconds'],
        'captured_files': len(completion['entries']), 'complete_readable_capture': True,
        'original_raw_capture_complete': False, 'projected_rollouts': len(projections),
        'opaque_fields_omitted': sum(len(row['omissions']) for row in projections),
        'native_package_unchanged': True, 'owner_auth_cache_unchanged': True,
        'task_and_dependencies_unchanged': True, 'final_matches_native_message': True,
        'recorded_commands': commands, 'recorded_tools': [{'name': row['name'], 'type': row['type']} for row in tools],
        'readiness': readiness, 'readiness_inherited_from': preparation.get('readiness_inherited_from'),
        'usage': stream[-1].get('usage'), 'ranking_eligible': False,
        'limits': ['Authentic complete readable output establishes administration, not correctness of findings.',
                   'Recorded native tools are not a complete kernel network/process trace.',
                   'Opaque ciphertext was discarded before guarding, with hashes and omission receipts.',
                   'One selected development review supplies no comparative ranking or scorer acceptance.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
