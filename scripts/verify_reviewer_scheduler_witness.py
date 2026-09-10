"""Assess record validity and preservation of causal placement inputs."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

from reviewer_scheduler_witness import COMMITS, verify_inputs
from reviewer_timeout_witness import sha
from verify_reviewer_claim_interpretation import read


def instant(text):
    result = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('witness timestamp lacks timezone')
    return result


def observation_record(observation):
    classifier = observation['Classifier']
    return {'record_ref': observation['RecordRef'], 'record_hash': observation['RecordHash'], 'payload': {
        'observation_kind': 'recognized_exhaustion',
        'candidate': {'backend_id': observation['BackendID'], 'pass_id': observation['PassID']},
        'provenance': {'run_ref': observation['SourceRunRef'], 'dispatch_id': observation['DispatchID'],
                       'classification': 'recognized_account_exhaustion', 'signature_id': observation['SignatureID'],
                       'classifier': {'policy_id': classifier['PolicyID'], 'policy_version': classifier['PolicyVersion'],
                                      'content_hash': classifier['ContentHash']}},
        'observed_at': observation['ObservedAt'], 'ttl_seconds': observation['TTLSeconds'], 'expires_at': observation['ExpiresAt']}}


def assess(row, criteria):
    condition = row['condition']
    if condition == 'malformed-observation':
        return {'condition': condition, 'disposition': 'malformed-input-rejected' if row['evaluation_error'] else 'malformed-input-accepted'}
    if condition not in criteria['expected_selected']:
        raise ValueError('unknown condition')
    if row['evaluation_error']:
        return {'condition': condition, 'disposition': 'evaluation-failed', 'error': row['evaluation_error']}
    expected = criteria['expected_selected'][condition]
    placement_matches = row['selected'] == expected and not row['refusals']
    if condition == 'all-supervised-exhausted':
        placement_matches = placement_matches and len(row['deferrals']) == 1 and row['deferrals'][0]['Reason'] == 'capacity_starved'
    else:
        placement_matches = placement_matches and not row['deferrals']
    as_of = instant(row['input']['as_of'])
    active = [observation for observation in row['input'].get('capacity_observations', [])
              if instant(observation['ObservedAt']) <= as_of < instant(observation['ExpiresAt'])]
    expected_records = sorted([observation_record(o) for o in active], key=lambda x: x['record_ref'])
    retained = row['payload']['input_preimage'].get('capacity_observations', [])
    observations_retained = retained == expected_records
    version_agreement = row['stamp'] == row['evaluation_version']
    record_accepted = not row['stamped_record']['encode_error'] and not row['stamped_record']['decode_error']
    counterfactual = row['without_observations']
    selection_changed = None if counterfactual['error'] else counterfactual['selected'] != row['selected']
    return {'condition': condition, 'disposition': 'evaluated', 'expected_placement_matches': bool(placement_matches),
            'stamp': row['stamp'], 'evaluation_version': row['evaluation_version'], 'version_agreement': version_agreement,
            'stamped_record_accepted': record_accepted, 'active_observation_count': len(active),
            'active_observations_retained': observations_retained, 'selected': row['selected'],
            'selection_without_observations': counterfactual['selected'],
            'counterfactual_selection_changed': selection_changed,
            'accepted_record_omits_selection_input': bool(placement_matches and version_agreement and record_accepted
                                                         and active and not observations_retained and selection_changed is True)}


def check_process(slot):
    completion = read(slot / 'completion.json')
    for name in ('stdout', 'stderr'):
        if sha((slot / name).read_bytes()) != completion[name + '_sha256']:
            raise ValueError('captured process output drift')
    if completion['returncode'] or completion['timed_out']:
        raise ValueError('preparation or witness process failed: ' + slot.name)
    return completion


def verify(root):
    plan = read(root / 'plan.json')
    started, completion = read(root / 'run-started.json'), read(root / 'completion.json')
    plan_hash = sha((root / 'plan.json').read_bytes())
    if started['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('incomplete or changed witness administration')
    verify_inputs(root, plan)
    criteria = read(root / 'criteria.json')
    observations, executions = [], []
    for role in COMMITS:
        for phase in ('verify-modules', 'compile'):
            check_process(root / f'{role}-{phase}')
        binary = root / 'builds' / role
        if sha((binary / 'probe').read_bytes()) != read(binary / 'binary.json')['sha256']:
            raise ValueError('compiled witness drift')
        raw_runs = []
        for repetition in range(1, criteria['repetitions'] + 1):
            slot = root / f'{role}-execution-{repetition}'
            check_process(slot)
            result = read(slot / 'stdout')
            if result['schema'] != 'caplab.scheduler-witness-output/v1':
                raise ValueError('unexpected witness schema')
            rows = result['observations']
            if [row['condition'] for row in rows] != criteria['conditions']:
                raise ValueError('missing, reordered or repeated witness conditions')
            for row in rows:
                observations.append({'role': role, 'commit': COMMITS[role], 'repetition': repetition,
                                     **assess(row, criteria)})
            raw_runs.append((slot / 'stdout').read_bytes())
            executions.append({'slot': slot.name, 'stdout_sha256': sha(raw_runs[-1]),
                               'completion_sha256': sha((slot / 'completion.json').read_bytes())})
        if len(set(raw_runs)) != 1:
            raise ValueError('identical frozen inputs did not replay byte-for-byte')
    return {'schema': 'caplab.scheduler-witness-verification/v1', 'plan_sha256': plan_hash,
            'criteria_sha256': sha((root / 'criteria.json').read_bytes()),
            'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations,
            'executions': executions, 'identical_repetitions': True, 'ranking_eligible': False,
            'limits': ['Record serialization/decoding and original placement APIs only; no full live driver or graph recovery.',
                       'Observation removal is a counterfactual check, not a complete record-to-input replay.',
                       'Related revisions and repetitions belong to one failure family.',
                       'Scenario success is not a whole-patch clean label or scorer acceptance.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
