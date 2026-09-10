"""Development assessment of reported claims against one verified scenario.

This is intentionally not a general scorer. The outer verifier accepts only
the frozen calibration documents and exact source/witness identities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from verify_reviewer_claim_interpretation import read, sha
from codex_rollout_projection import verify_projection


def verify_capture(root: Path, plan: dict, completion: dict) -> None:
    seen = set()
    rollouts = []
    for entry in completion['entries']:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or str(relative) in seen:
            raise ValueError('invalid or duplicate capture path')
        seen.add(str(relative))
        path = root / 'capture' / relative
        if entry['disposition'] not in ('retained', 'projected-retained') or sha(path) != entry['sha256']:
            raise ValueError('incomplete or changed capture')
        is_rollout = relative.match('codex/sessions/*/*/*/rollout-*.jsonl')
        if is_rollout:
            rollouts.append(path)
        if entry['disposition'] == 'projected-retained':
            policy = plan.get('readable_capture_projection', {})
            if not is_rollout or policy.get('schema') != 'caplab.codex-readable-rollout-projection/v1':
                raise ValueError('unplanned capture projection')
            receipt_relative = Path(entry['projection_receipt'])
            if receipt_relative != Path('projection-receipts') / relative.with_suffix('.receipt.json'):
                raise ValueError('unexpected projection receipt path')
            receipt_path = root / receipt_relative
            if sha(receipt_path) != entry['projection_receipt_sha256']:
                raise ValueError('projection receipt drift')
            receipt = read(receipt_path)
            if (receipt['source_path'] != str(relative) or receipt['plan_sha256'] != sha(root / 'plan.json')
                    or receipt['implementation_sha256'] != policy['implementation_sha256']
                    or sha(root / 'projection.py') != policy['implementation_sha256']):
                raise ValueError('projection custody mismatch')
            verify_projection(path.read_bytes(), receipt)
        elif is_rollout and plan.get('readable_capture_projection'):
            raise ValueError('planned rollout projection missing')
    if not {'stdout', 'stderr', 'final-message.txt'} <= seen or not rollouts:
        raise ValueError('required native capture missing')


def compare_reported(inputs: dict, expected: dict, output: dict) -> dict:
    if not isinstance(output, dict) or set(output) != {'entries'} or not isinstance(output['entries'], list):
        raise ValueError('entries array required')
    documents = {row['document_id']: row['text'] for row in inputs['documents']}
    hypotheses = {row['hypothesis_id'] for row in inputs['hypotheses']}
    expectations = {row['document_id']: row for row in expected['entries']}
    seen, observations = set(), []
    for row in output['entries']:
        if not isinstance(row, dict) or set(row) != {'document_id', 'assertions', 'unmapped_claims', 'locations'}:
            raise ValueError('unexpected entry fields')
        identity = row['document_id']
        if not isinstance(identity, str) or identity not in documents or identity in seen:
            raise ValueError('unknown or duplicate document')
        seen.add(identity)
        source = documents[identity]
        if not all(isinstance(row[key], list) for key in ('assertions', 'unmapped_claims', 'locations')):
            raise ValueError('entry arrays required')
        mappings = {}
        for assertion in row['assertions']:
            if not isinstance(assertion, dict) or set(assertion) != {'hypothesis_id', 'stance'}:
                raise ValueError('unexpected assertion fields')
            hypothesis = assertion['hypothesis_id']
            if not isinstance(hypothesis, str) or hypothesis not in hypotheses or hypothesis in mappings:
                raise ValueError('unknown or duplicate hypothesis')
            if assertion['stance'] not in ('asserted', 'uncertain', 'rejected'):
                raise ValueError('unknown stance')
            mappings[hypothesis] = assertion['stance']
        for value in row['unmapped_claims'] + row['locations']:
            if not isinstance(value, str) or not value or value not in source:
                raise ValueError('location or unknown-claim quote not in source')
        target = expectations[identity]
        checks = {'reported_stances_match': mappings == target['assertions'],
                  'unknown_presence_matches': bool(row['unmapped_claims']) == target['unmapped_required'],
                  'locations_match': sorted(row['locations']) == sorted(target['locations'])}
        observations.append({'document_id': identity, 'case': expected['cases'][identity],
            'full_source_text': source, 'full_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'expected_stances': target['assertions'], 'reported_stances': mappings,
            'checks': checks, 'matches_frozen_expectation': all(checks.values()),
            'unmapped_claims': row['unmapped_claims'], 'locations': row['locations']})
    if seen != set(documents):
        raise ValueError('missing documents')
    return {'observations': sorted(observations, key=lambda row: row['document_id']),
            'matching_documents': sum(row['matches_frozen_expectation'] for row in observations),
            'documents': len(observations), 'all_match': all(row['matches_frozen_expectation'] for row in observations)}


def assess_lifetime(report: dict, fact: dict, hypothesis: str) -> dict:
    claims = {row['hypothesis_id']: row['stance'] for row in report['assertions']}
    stance = claims.get(hypothesis)
    if type(fact['delayed_body_property_satisfied']) is not bool:
        raise ValueError('verified scenario outcome required')
    violation = not fact['delayed_body_property_satisfied']
    anchor_supported = False
    # Aggregate locations cannot be assigned to one of several reported claims.
    locations = report['locations'] if len(report['assertions']) == 1 and not report['unmapped_claims'] else []
    for location in locations:
        match = re.fullmatch(r'([^:]+):(\d+)(?:-(\d+))?', location)
        if match and match[1] == fact['source_file']:
            first, last = int(match[2]), int(match[3] or match[2])
            lower, upper = fact['causal_region']
            if lower <= first <= last <= upper:
                anchor_supported = True
    if stance is None:
        disposition = 'known-defect-not-reported' if violation else 'no-target-claim'
    elif stance == 'uncertain':
        disposition = 'uncertain-report'
    elif stance == 'rejected':
        # Withdrawal of a report is not necessarily a denial that a bug exists.
        disposition = 'retracted-or-rejected-report'
    elif stance != 'asserted':
        raise ValueError('unknown reported stance')
    elif not violation:
        disposition = 'refuted-scenario'
    elif not anchor_supported:
        disposition = 'causal-attribution-unresolved'
    elif fact['lineage'] == 'introduced-module':
        disposition = 'confirmed-introduced-defect'
    elif fact['lineage'] == 'unchanged-module-and-only-codex-adapter-change':
        disposition = 'inherited-behavior'
    else:
        disposition = 'causal-attribution-unresolved'
    return {'disposition': disposition, 'scenario_violation_observed': violation,
            'reported_stance': stance, 'causal_anchor_supported': anchor_supported,
            'introduced_defect_credit': disposition == 'confirmed-introduced-defect',
            'unresolved_assertions': [row for row in report['assertions']
                                      if row['hypothesis_id'] != hypothesis and row['stance'] in ('asserted', 'uncertain')],
            'unmapped_claims': report['unmapped_claims'],
            'scope': 'Only the frozen 300 ms timeout / two-second body scenario; no whole-patch clean label.'}


def verify(root: Path) -> dict:
    fixture, plan, launch, completion = (read(root / name) for name in
                                       ('fixture-plan.json', 'plan.json', 'launch.json', 'completion.json'))
    for name, key in (('task/inputs.json', 'input_sha256'), ('expected.json', 'expected_sha256'),
                      ('prompt.txt', 'prompt_sha256'), ('assessment-cases.json', 'assessment_cases_sha256')):
        if sha(root / name) != fixture[key]:
            raise ValueError('frozen input drift: ' + name)
    if sha(root / 'fixture-plan.json') != plan['fixture_plan_sha256'] or sha(root / 'plan.json') != launch['plan_sha256']:
        raise ValueError('native plan mismatch')
    if sha(root / 'outcome-plan.json') != plan['outcome_plan_sha256']:
        raise ValueError('outcome plan drift')
    if completion['returncode'] != 0 or completion['termination'] != 'exit':
        raise ValueError('interpretation did not complete')
    verify_capture(root, plan, completion)
    output = read(root / 'capture/final-message.txt')
    comparison = compare_reported(read(root / 'task/inputs.json'), read(root / 'expected.json'), output)
    result = {'schema': 'caplab.review-outcome-development-verification/v1', 'interpretation': comparison,
              'assessment': None, 'native_development_observation': None,
              'fixture_plan_sha256': sha(root / 'fixture-plan.json'), 'plan_sha256': sha(root / 'plan.json'),
              'outcome_plan_sha256': sha(root / 'outcome-plan.json'), 'verifier_sha256': sha(Path(__file__)),
              'ranking_eligible': False}
    if not comparison['all_match']:
        result['assessment_withheld_reason'] = 'reported-stance calibration did not meet the frozen all-document criterion'
        return result
    facts = read(root / 'outcome-plan.json')
    witness = root.parent / 'timeout-witness-1'
    for name, key in (('verification.json', 'timeout_verification_sha256'), ('plan.json', 'timeout_plan_sha256'),
                      ('criteria.json', 'timeout_criteria_sha256')):
        if sha(witness / name) != facts[key]:
            raise ValueError('independent witness drift')
    observations = read(witness / 'verification.json')['observations']
    for role, fact in facts['roles'].items():
        if sha(Path(fact['runtime_path'])) != fact['runtime_sha256']:
            raise ValueError('original source drift')
        matches = [row for row in observations if row['role'] == role and row['condition'] == 'delayed-body']
        if len(matches) != 3 or not all(row['commit'] == fact['commit'] and
                                      row['property_satisfied'] == fact['delayed_body_property_satisfied'] for row in matches):
            raise ValueError('scenario evidence disagrees with outcome plan')
    reports = {row['document_id']: row for row in output['entries']}
    cases = read(root / 'assessment-cases.json')['cases']
    assessed = []
    for case in cases:
        observation = assess_lifetime(reports[case['document_id']], facts['roles'][case['revision_role']], facts['hypothesis_id'])
        assessed.append({**case, **observation, 'matches_expected_disposition': observation['disposition'] == case['expected_disposition'],
                         'source_commit': facts['roles'][case['revision_role']]['commit'],
                         'family': facts['family'], 'constructed_scorer_challenge': True})
    result['assessment'] = assessed
    native = assess_lifetime(reports[facts['native_development_document']], facts['roles']['introduction'], facts['hypothesis_id'])
    # The original native probe remains unscored; retain diagnostic observations.
    native.pop('introduced_defect_credit')
    result['native_development_observation'] = native
    result['limitations'] = ['Authored semantic expectations and a closed hypothesis vocabulary do not establish broad semantic accuracy.',
                            'Full source context preserves qualifications but is not proof of semantic support.',
                            'Location outside the known causal region remains unresolved; alternative valid causal explanations need investigation.',
                            'Repair refutation is limited to the frozen concrete scenario, not universal absence of a defect.',
                            'Synthetic reports are scorer checks, not native reviewer measurements.']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
