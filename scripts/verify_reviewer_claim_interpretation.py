"""Compare a captured interpretation with frozen development expectations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path: Path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def compare(inputs: dict, expected: dict, output: dict) -> dict:
    if set(output) != {'entries'} or not isinstance(output['entries'], list):
        raise ValueError('output must contain only an entries array')
    documents = {row['document_id']: row['text'] for row in inputs['documents']}
    hypotheses = {row['hypothesis_id'] for row in inputs['hypotheses']}
    expectations = {row['document_id']: row for row in expected['entries']}
    seen = set()
    observations = []
    for row in output['entries']:
        if not isinstance(row, dict) or set(row) != {'document_id', 'assertions', 'unmapped_claims', 'locations'}:
            raise ValueError('invalid interpretation entry fields')
        identity = row['document_id']
        if not isinstance(identity, str) or identity not in documents or identity in seen:
            raise ValueError('unknown or duplicate document identity')
        seen.add(identity)
        source = documents[identity]
        mappings, quotations = {}, []
        if not all(isinstance(row[field], list) for field in ('assertions', 'unmapped_claims', 'locations')):
            raise ValueError('entry arrays required')
        for assertion in row['assertions']:
            if not isinstance(assertion, dict) or set(assertion) != {'hypothesis_id', 'stance', 'quote'}:
                raise ValueError('invalid assertion fields')
            hypothesis = assertion['hypothesis_id']
            if not isinstance(hypothesis, str) or hypothesis not in hypotheses or hypothesis in mappings:
                raise ValueError('unknown or repeated hypothesis')
            if assertion['stance'] not in ('asserted', 'uncertain', 'rejected'):
                raise ValueError('unknown stance')
            quote = assertion['quote']
            if not isinstance(quote, str) or not quote or quote not in source:
                raise ValueError('assertion quotation is not verbatim')
            mappings[hypothesis] = assertion['stance']
            quotations.append({'hypothesis_id': hypothesis, 'quote': quote,
                               'start_character': source.index(quote)})
        for quote in row['unmapped_claims']:
            if not isinstance(quote, str) or not quote or quote not in source:
                raise ValueError('unmapped claim quotation is not verbatim')
        if not all(isinstance(location, str) and location and location in source for location in row['locations']):
            raise ValueError('location not present in document')
        target = expectations[identity]
        checks = {'assertion_mapping_matches': mappings == target['assertions'],
                  'unmapped_presence_matches': bool(row['unmapped_claims']) == target['unmapped_required'],
                  'locations_match': sorted(row['locations']) == sorted(target['locations'])}
        observations.append({'document_id': identity, 'case': expected['cases'][identity],
                             'checks': checks, 'matches_frozen_expectation': all(checks.values()),
                             'expected_assertions': target['assertions'], 'actual_assertions': mappings,
                             'quotes': quotations, 'unmapped_claims': row['unmapped_claims'],
                             'actual_locations': row['locations'], 'expected_locations': target['locations']})
    if seen != set(documents):
        raise ValueError('missing document interpretations')
    return {'documents': len(observations), 'matching_documents': sum(row['matches_frozen_expectation'] for row in observations),
            'all_match': all(row['matches_frozen_expectation'] for row in observations),
            'observations': sorted(observations, key=lambda row: row['document_id'])}


def verify(root: Path) -> dict:
    fixture = read(root / 'fixture-plan.json')
    for path, field in (('task/inputs.json', 'input_sha256'), ('expected.json', 'expected_sha256'), ('prompt.txt', 'prompt_sha256')):
        if sha(root / path) != fixture[field]:
            raise ValueError('frozen fixture drift: ' + path)
    plan, launch, completion = (read(root / path) for path in ('plan.json', 'launch.json', 'completion.json'))
    if plan['fixture_plan_sha256'] != sha(root / 'fixture-plan.json') or launch['plan_sha256'] != sha(root / 'plan.json'):
        raise ValueError('plan identity mismatch')
    if completion['returncode'] != 0 or completion['termination'] != 'exit':
        raise ValueError('native interpretation did not complete')
    for entry in completion['entries']:
        if entry['disposition'] != 'retained' or sha(root / 'capture' / entry['path']) != entry['sha256']:
            raise ValueError('capture is incomplete or changed')
    result = compare(read(root / 'task/inputs.json'), read(root / 'expected.json'), read(root / 'capture/final-message.txt'))
    return {'schema': 'caplab.claim-interpretation-development-verification/v1', **result,
            'custody_root': str(root), 'plan_sha256': sha(root / 'plan.json'),
            'fixture_plan_sha256': sha(root / 'fixture-plan.json'),
            'completion_sha256': sha(root / 'completion.json'), 'final_sha256': sha(root / 'capture/final-message.txt'),
            'verifier_sha256': sha(Path(__file__)),
            'limit': 'Checks semantic mappings against authored expectations and literal quotation attribution; does not prove quotation sufficiency, empirical defect truth or reviewer quality.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
