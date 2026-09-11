"""Inspect proposition representation and custody; never infer semantic truth.

This development tool uses the repository's test extra (jsonschema). It accepts
an already frozen task inventory, not a model-authored list of trusted files.
"""
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from caplab.codex_events import parse_native_json
from caplab.native_review_report import SCHEMA, TEXT_FIELDS, _location, _validate

SCHEMA_ID = 'caplab.review-proposition-assessment/v2'
ROLES = ('behavior', 'requirement', 'change_attribution', 'applicability')


def _object(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def assessment_schema():
    text = {'type': 'string'}
    nonempty = {'type': 'string', 'minLength': 1}
    span = _object({'field': {'type': 'string', 'enum': sorted(TEXT_FIELDS)}, 'quote': nonempty})
    citation = _object({'path': nonempty, 'start_line': {'type': 'integer', 'minimum': 1},
        'end_line': {'type': 'integer', 'minimum': 1},
        'relation': {'type': 'string', 'enum': ['supports', 'contradicts', 'context']},
        'kind': {'type': 'string', 'enum': ['source', 'original_execution', 'requirement', 'inventory']},
        'explanation': nonempty})
    proposition = _object({'proposition_id': nonempty, 'role': {'type': 'string', 'enum': list(ROLES)},
        'source_spans': {'type': 'array', 'minItems': 1, 'items': span}, 'statement': nonempty,
        'scenario': nonempty, 'status': {'type': 'string', 'enum': ['supported', 'contradicted', 'unresolved']},
        'reason': nonempty, 'missing_evidence': text, 'resolution': text,
        'evidence': {'type': 'array', 'items': citation}})
    entry = _object({'document_id': nonempty, 'finding_id': nonempty,
        'reported_claim_status': {'type': 'string', 'enum': ['asserted', 'uncertain', 'withdrawn']},
        'acceptance_effect': {'type': 'string', 'enum': ['block', 'advise', 'undetermined']},
        'duplicate_of': {'type': ['string', 'null']}, 'no_defect_claim': {'type': 'boolean'},
        'no_defect_reason': text, 'propositions': {'type': 'array', 'items': proposition}})
    return _object({'schema': {'type': 'string', 'enum': [SCHEMA_ID]},
                    'entries': {'type': 'array', 'items': entry}})


def _canonical_sha(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def _original_findings(inputs):
    originals = {}
    documents = []
    for document in inputs['documents']:
        reported = {'schema': SCHEMA, 'findings': [f['reported'] for f in document['findings']],
                    'limitations': document['limitations']}
        _validate(reported)
        documents.append({'document_id': document['document_id'], 'sha256': _canonical_sha(document),
                          'limitations': document['limitations']})
        for finding in document['findings']:
            key = (document['document_id'], finding['finding_id'])
            if key in originals:
                raise ValueError('duplicate input finding identity')
            originals[key] = finding['reported']
    return originals, documents


def _bind_evidence(proposition, root, inventory):
    citations = []
    for citation in proposition['evidence']:
        location = _location(citation, root)
        expected = inventory.get(citation['path'])
        citations.append({**citation, 'location': location, 'expected_file_sha256': expected,
            'matches_frozen_artifact': expected is not None and location['status'] == 'resolved'
                                      and location.get('file_sha256') == expected})
    return {**proposition, 'evidence': citations}


def _component_checks(propositions, reported):
    checks = []
    for proposition in propositions:
        relation = {'supported': 'supports', 'contradicted': 'contradicts'}.get(proposition['status'])
        checks.append({'proposition_id': proposition['proposition_id'],
            'source_quotes_preserved': all(span['quote'].strip() and span['quote'] in reported[span['field']]
                                           for span in proposition['source_spans']),
            'scope_and_reason_present': all(proposition[field].strip()
                                            for field in ('statement', 'scenario', 'reason')),
            'status_has_required_basis': (
                bool(proposition['missing_evidence'].strip() and proposition['resolution'].strip())
                if relation is None else any(c['relation'] == relation for c in proposition['evidence']))})
    return checks


def inspect_assessment(inputs, raw, task_root, source_inventory):
    """Bind every assessed occurrence to its original text and immutable evidence.

    Passing representation checks cannot establish complete decomposition,
    correct evidence classification, semantic support or reviewer credit.
    """
    if not isinstance(raw, bytes) or len(raw) > 4 * 1024 * 1024:
        raise ValueError('assessment must be at most four MiB of bytes')
    output = parse_native_json(raw.decode('utf-8'))
    Draft202012Validator(assessment_schema()).validate(output)
    originals, documents = _original_findings(inputs)
    occurrence_order = {key: index for index, key in enumerate(originals)}
    assessed = {(row['document_id'], row['finding_id']): row for row in output['entries']}
    root = Path(task_root).resolve(strict=True)
    inventory = {entry['path']: entry['sha256'] for entry in source_inventory}
    if len(inventory) != len(source_inventory):
        raise ValueError('duplicate frozen inventory path')
    seen = set()
    entries = []
    for row in output['entries']:
        key = (row['document_id'], row['finding_id'])
        if key not in originals or key in seen:
            raise ValueError('unknown or duplicate assessed occurrence')
        seen.add(key)
        reported = originals[key]
        propositions = [_bind_evidence(p, root, inventory) for p in row['propositions']]
        components = _component_checks(propositions, reported)
        component_ids = [p['proposition_id'] for p in propositions]
        component_shape = (not propositions and bool(row['no_defect_reason'].strip())
                           if row['no_defect_claim'] else
                           set(p['role'] for p in propositions) == set(ROLES))
        target = (row['document_id'], row['duplicate_of'])
        duplicate_valid = row['duplicate_of'] is None or (
            target in occurrence_order and target in assessed
            and occurrence_order[target] < occurrence_order[key]
            and assessed[target]['duplicate_of'] is None)
        entries.append({**row, 'reported': reported, 'finding_sha256': _canonical_sha(reported),
            'propositions': propositions, 'component_checks': components,
            'checks': {'reported_stance_preserved': row['reported_claim_status'] == reported['claim_status'],
                       'reported_effect_preserved': row['acceptance_effect'] == reported['acceptance_effect'],
                       'duplicate_reference_valid': duplicate_valid,
                       'component_representation_complete': component_shape,
                       'unique_proposition_ids': len(component_ids) == len(set(component_ids)),
                       'component_checks_pass': all(all(v for k, v in c.items() if k != 'proposition_id')
                                                     for c in components),
                       'evidence_identity_preserved': all(c['matches_frozen_artifact']
                           for p in propositions for c in p['evidence'])}})
    if seen != set(originals):
        raise ValueError('missing assessed occurrences')
    return {'schema': 'caplab.review-proposition-inspection/v2', 'input_sha256': _canonical_sha(inputs),
        'raw_assessment_sha256': hashlib.sha256(raw).hexdigest(), 'inventory_sha256': _canonical_sha(source_inventory),
        'documents': documents, 'entries': entries,
        'representation_checks_pass': all(all(e['checks'].values()) for e in entries),
        'decomposition_complete_verified': False, 'semantic_support_verified': False,
        'scorer_accepted': False, 'ranking_eligible': False}
