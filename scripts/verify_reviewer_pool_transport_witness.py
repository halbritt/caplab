"""Check delivered bytes and original score denominators against endpoint receipts."""
from __future__ import annotations

import json
from pathlib import Path

from reviewer_pool_transport_witness import ROOT, COMMITS, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process

VERDICTS = {'accept', 'accept_with_findings', 'needs_revision', 'reject'}


def read(path):
    return json.loads(path.read_text())


def assess(observation, config, events):
    condition = observation['condition']
    expected = config['expected_bodies']
    delivered = [event['arm'] for event in events if event['arm'] is not None]
    if len(delivered) != len(set(delivered)):
        raise ValueError('duplicate endpoint invocation for one arm')
    for event in events:
        if event['arm'] is not None and event['body_sha256'] != expected[event['arm']]:
            raise ValueError('endpoint body identity mismatch')
        if event['arm'] is None and event['delivery'] != 'absent':
            raise ValueError('unrecognized delivered body')
    all_delivered = set(delivered) == set(expected)
    valid = []
    for event in events:
        response = event.get('response')
        if response is not None and response != '':
            doc = json.loads(response)
            if isinstance(doc, dict) and doc.get('verdict') in VERDICTS and isinstance(doc.get('findings'), list):
                valid.append(event['arm'])
    result = {'condition': condition, 'invocations': len(events), 'all_body_bytes_delivered': all_delivered,
              'valid_response_arms': sorted(arm for arm in valid if arm is not None),
              'deliveries': sorted(event['delivery'] for event in events)}
    if observation['kind'] == 'invoke':
        row = observation['result']
        refused = not events and row.get('error') == 'prompt exceeds transport capacity' and row['exit_code'] is None
        return {**result, 'transport': row['transport'], 'explicit_prelaunch_refusal': refused,
                'delivery_or_refusal': bool(all_delivered or refused),
                'silently_undelivered': bool(events and not all_delivered and not row.get('error'))}
    if len(events) != 2:
        raise ValueError('pool execution lacks two endpoint receipts')
    row, summary = observation['row'], observation['summary']
    usable = row['usable']
    if summary['pairs_usable'] != int(usable) or summary['pairs_discarded'] != int(not usable):
        raise ValueError('original row and summary disagree about denominator')
    if not usable and (summary['catch_rate'] is not None or summary['false_alarm_rate'] is not None):
        raise ValueError('empty score denominator has a numeric rate')
    valid_pair = all_delivered and set(valid) == set(expected)
    return {**result, 'usable': usable, 'pairs_usable': summary['pairs_usable'],
            'pairs_discarded': summary['pairs_discarded'], 'catch_rate': summary['catch_rate'],
            'false_alarm_rate': summary['false_alarm_rate'], 'independently_valid_response_pair': valid_pair,
            'invalid_response_enters_denominator': bool(usable and not valid_pair),
            'row_control_verdict': row.get('control_verdict'), 'row_mutant_verdict': row.get('mutant_verdict'),
            'mutant_timeout_recorded': row.get('mutant_timed_out') is True,
            'error': row.get('error')}


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    start, completion = read(ROOT / 'run-started.json'), read(ROOT / 'completion.json')
    if start['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('incomplete or changed administration')
    verify_inputs(plan)
    criteria = read(ROOT / 'witness/criteria.json')
    observations, executions = [], []
    for role in COMMITS:
        repetitions = []
        for repetition in range(1, plan['repetitions'] + 1):
            name = f'{role}-{repetition}'
            check_process(ROOT / name)
            capture = ROOT / (name + '-capture')
            entries = inventory(capture)
            if entries != read(ROOT / (name + '-inventory.json')):
                raise ValueError('captured delivery or pool evidence drift')
            if {p.name for p in capture.iterdir()} != set(criteria['conditions']) | {'loaded-source.json'}:
                raise ValueError('missing or unexpected scenario capture')
            source = {row['path']: row['sha256'] for row in plan['snapshots'][role]['files']}
            modules = read(capture / 'loaded-source.json')
            if not modules:
                raise ValueError('missing original module capture')
            for module in modules:
                if source.get(module['path'].removeprefix('/source/')) != module['sha256']:
                    raise ValueError('loaded module was not the original source')
            results = []
            for condition in criteria['conditions']:
                directory = capture / condition
                config = read(directory / 'config.json')
                events = []
                for event_dir in sorted((directory / 'events').glob('*')):
                    event = read(event_dir / 'received.json')
                    prompt, body = (event_dir / 'prompt.txt').read_bytes(), (event_dir / 'body.txt').read_bytes()
                    if len(prompt) != event['prompt_bytes'] or len(body) != event['body_bytes'] or sha(body) != event['body_sha256']:
                        raise ValueError('endpoint receipt disagrees with actual bytes')
                    response = event_dir / 'response.txt'
                    if not response.exists() and event['behavior'] != 'timeout':
                        raise ValueError('endpoint did not finish its configured non-timeout behavior')
                    event['response'] = response.read_text() if response.exists() else None
                    events.append(event)
                observation = read(directory / 'observation.json')
                if observation['condition'] != condition:
                    raise ValueError('misfiled condition')
                if observation['kind'] == 'pool':
                    if observation['summary'] != read(directory / 'pool/summary.json'):
                        raise ValueError('summary capture mismatch')
                    rows = [json.loads(line) for line in (directory / 'pool/results.jsonl').read_text().splitlines()]
                    if rows != [observation['row']]:
                        raise ValueError('row capture mismatch')
                result = assess(observation, config, events)
                observations.append({'role': role, 'repetition': repetition, **result})
                results.append(result)
            repetitions.append(results)
            executions.append({'slot': name, 'captured_files': len(entries),
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
        if any(rows != repetitions[0] for rows in repetitions[1:]):
            raise ValueError('semantic observations differ between repetitions')
    return {'schema': 'caplab.pool-transport-verification/v1', 'plan_sha256': plan_hash,
            'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations,
            'executions': executions, 'semantic_repetitions_match': True, 'ranking_eligible': False,
            'limits': criteria['limits']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
