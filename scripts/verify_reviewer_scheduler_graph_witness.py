"""Assess graph reachability separately from completeness of decision evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reviewer_scheduler_graph_witness import verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process, instant, observation_record


def read(path):
    return json.loads(path.read_text())


def assess(row, criteria):
    condition = row['condition']
    if condition not in criteria['conditions']:
        raise ValueError('unknown condition')
    if row.get('schema') != 'caplab.scheduler-graph-output/v1':
        raise ValueError('unexpected witness schema')
    if row.get('adapter_dispatches') != 0 or row.get('capture_error') or row.get('final_records_error') != '':
        raise ValueError('effect or capture boundary failed')
    if row['phase'] not in ('completed', 'decision-refused'):
        raise ValueError('fixture or measured path incomplete')
    if condition != 'ordinary' and row.get('source_drain_error') != '':
        raise ValueError('original submission drain failed')
    observations = row['input'].get('capacity_observations', [])
    as_of = instant(row['input']['as_of'])
    if any(not (instant(o['ObservedAt']) <= as_of < instant(o['ExpiresAt'])) for o in observations):
        raise ValueError('Driver supplied inactive observation')
    if (len(observations) != criteria['expected_active_observations'][condition]
            or len(row['folded_capacity_observations'] or []) != criteria['expected_folded_observations'][condition]):
        raise ValueError('observation setup does not match frozen condition')
    records = row['records']
    # The input observation must correspond to a real decoded graph record.
    for observation in observations:
        expected = observation_record(observation)
        matching = [r for r in records if r['Seq'] == expected['record_ref']]
        if len(matching) != 1 or matching[0]['Type'] != 'capacity_observation' or matching[0]['Payload'] != expected['payload']:
            raise ValueError('observation lacks matching graph provenance')
    result = {'condition': condition, 'phase': row['phase'], 'active_observation_count': len(observations),
              'folded_observation_count': len(row['folded_capacity_observations'] or []), 'adapter_dispatches': 0}
    if row['phase'] == 'decision-refused':
        if not row['decision_error'] or row['decision_created'] or len(records) != row['records_before']:
            raise ValueError('refusal evidence is inconsistent')
        return {**result, 'decision_error': row['decision_error'], 'graph_accepted_missing_causal_input': False}
    required_empty = ['decision_error', 'binding_preimage_error', 'binding_error', 'reopen_error',
                      'repeat_decision_error', 'repeat_binding_error', 'counterfactual_clock_error', 'counterfactual_error']
    if any(row.get(key) != '' for key in required_empty):
        raise ValueError('measured path or counterfactual failed')
    if row['outcome'] != 'binding' or not row['decision_created'] or not row['binding_created']:
        raise ValueError('new placement was not created')
    decision = row['decision']
    matching = [r for r in records if r['Seq'] == decision['Seq']]
    if (len(matching) != 1 or matching[0]['Type'] != 'scheduling_decision'
            or matching[0]['SchemaVersion'] != decision['SchemaVersion'] or matching[0]['Payload'] != decision['Payload']
            or decision['InvalidReason'] or row['reopened_decisions'] != [decision]):
        raise ValueError('decision not preserved through original graph fold')
    selected = row['selected']['backend_id']
    if (row['reopened_run']['BackendID'] != selected
            or row['reopened_run']['DispatchID'] != row['selected']['dispatch_id']):
        raise ValueError('binding changed or missing after reopen')
    idempotent = (row['repeat_decision_created'] is False and row['repeat_binding_created'] is False
                  and row['repeat_added_records'] == 0)
    expected_observations = sorted([observation_record(o) for o in observations], key=lambda o: o['record_ref'])
    retained = decision['Payload']['input_preimage'].get('capacity_observations', [])
    complete = retained == expected_observations
    counterfactual = [binding['BackendID'] for binding in row['counterfactual_bindings']]
    effect = counterfactual != [selected]
    placement_matches = selected == criteria['expected_selected'][condition]
    return {**result, 'decision_version': decision['SchemaVersion'], 'selected': selected,
            'expected_placement_matches': placement_matches, 'idempotent_reopen': idempotent,
            'active_observations_retained': complete, 'selection_without_observations': counterfactual,
            'counterfactual_selection_changed': effect,
            'graph_accepted_missing_causal_input': bool(placement_matches and idempotent and observations and not complete and effect)}


def verify(root):
    plan = read(root / 'plan.json')
    plan_hash = sha((root / 'plan.json').read_bytes())
    start, completion = read(root / 'run-started.json'), read(root / 'completion.json')
    if start['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('incomplete administration or changed plan')
    verify_inputs(root, plan)
    criteria = read(root / 'criteria.json')
    observations, executions = [], []
    for role in plan['roles']:
        check_process(root / (role + '-compile'))
        binary = root / 'builds' / role
        if sha((binary / 'probe').read_bytes()) != read(binary / 'binary.json')['sha256']:
            raise ValueError('binary drift')
        repetitions = []
        for repetition in range(1, plan['repetitions'] + 1):
            slot = root / f'{role}-execution-{repetition}'
            check_process(slot)
            capture = root / (slot.name + '-capture')
            entries = inventory(capture)
            if entries != read(root / (slot.name + '-inventory.json')):
                raise ValueError('captured graph or observation drift')
            if {p.name for p in capture.iterdir()} != set(criteria['conditions']):
                raise ValueError('missing or extra condition capture')
            results = []
            for condition in criteria['conditions']:
                row = read(capture / condition / 'result.json')
                if row['condition'] != condition:
                    raise ValueError('misfiled condition')
                if not inventory(capture / condition / 'data') or not inventory(capture / condition / 'repo'):
                    raise ValueError('missing graph or repository identity custody')
                result = assess(row, criteria)
                results.append(result)
                observations.append({'role': role, 'repetition': repetition, **result})
            repetitions.append(results)
            executions.append({'slot': slot.name, 'captured_files': len(entries),
                               'inventory_sha256': sha((root / (slot.name + '-inventory.json')).read_bytes())})
        if any(result != repetitions[0] for result in repetitions[1:]):
            raise ValueError('semantic observations differ between repetitions')
    return {'schema': 'caplab.scheduler-graph-verification/v1', 'plan_sha256': plan_hash,
            'criteria_sha256': plan['criteria_sha256'], 'verifier_sha256': sha(Path(__file__).read_bytes()),
            'observations': observations, 'executions': executions, 'semantic_repetitions_match': True,
            'ranking_eligible': False, 'limits': criteria['limits']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
