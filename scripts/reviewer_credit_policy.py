"""Development policy arithmetic; supplied warrants are not verified here.

See OUTCOME-CREDIT.md. This is neither a semantic assessor nor an admission
boundary. Native completion, evidence truth and materiality require separate
verification before these arithmetic results can inform any comparison.
"""
import copy

from caplab.native_review_report import SCHEMA, _validate as validate_native_report

STATUSES = ('supported', 'contradicted', 'unresolved')


def _unique_identities(values):
    if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError('identities must be nonempty strings in an array')
    if len(set(values)) != len(values):
        raise ValueError('duplicate identity')
    return set(values)


def _validate_inputs(document, defect_ids, warrants):
    if not isinstance(document, dict) or set(document) != {'document_id', 'findings', 'limitations'}:
        raise ValueError('a complete original document is required')
    _unique_identities([document['document_id']])
    findings = document['findings']
    if not isinstance(findings, list) or any(not isinstance(f, dict) or set(f) != {'finding_id', 'reported'} for f in findings):
        raise ValueError('complete finding occurrences are required')
    finding_ids = _unique_identities([f['finding_id'] for f in findings])
    validate_native_report({'schema': SCHEMA, 'findings': [f['reported'] for f in findings],
                            'limitations': document['limitations']})
    defects = _unique_identities(defect_ids)
    fields = {'finding_id', 'defect_matches', 'blocking_basis', 'unresolved_new_defect', 'judgment_record'}
    if not isinstance(warrants, list) or any(not isinstance(w, dict) or set(w) != fields for w in warrants):
        raise ValueError('complete outcome warrants are required')
    if _unique_identities([w['finding_id'] for w in warrants]) != finding_ids:
        raise ValueError('every finding must have exactly one warrant')
    for warrant in warrants:
        matches = warrant['defect_matches']
        if not isinstance(matches, dict) or set(matches) != defects:
            raise ValueError('every known defect must have an explicit match assessment')
        if any(s not in STATUSES for s in matches.values()) or warrant['blocking_basis'] not in STATUSES:
            raise ValueError('unknown outcome evidence status')
        if type(warrant['unresolved_new_defect']) is not bool:
            raise ValueError('new-defect uncertainty must be explicit')
        if not isinstance(warrant['judgment_record'], str) or not warrant['judgment_record'].strip():
            raise ValueError('outcome judgment record reference required')


def project_completed_review(document, defect_ids, warrants):
    """Project bounds for an authentic completed report supplied by the caller.

    document is one v2 assessment input document, with original reported
    findings and limitations. defect_ids names the common known root causes.
    Each warrant names its finding, an explicit defect_matches status for
    every cause, blocking_basis status, unresolved_new_defect boolean, and
    judgment_record reference. Statuses describe outcome evidence, not raw
    proposition labels. The reference is retained but not dereferenced or
    authenticated here. Returned intervals are logical bounds, not confidence
    intervals; this function never establishes ranking eligibility.
    """
    _validate_inputs(document, defect_ids, warrants)
    by_finding = {w['finding_id']: w for w in warrants}
    active = [(f['reported'], by_finding[f['finding_id']]) for f in document['findings']
              if f['reported']['claim_status'] != 'withdrawn']
    catches = {}
    for identity in defect_ids:
        statuses = [w['defect_matches'][identity] for _, w in active]
        catches[identity] = [int('supported' in statuses),
                             int(any(s != 'contradicted' for s in statuses))]
    blockers = [w['blocking_basis'] for report, w in active if report['acceptance_effect'] == 'block']
    possible_blockers = [w['blocking_basis'] for report, w in active
                         if report['acceptance_effect'] in ('block', 'undetermined')]
    return {'schema': 'caplab.review-credit-projection/v1',
        'document': copy.deepcopy(document), 'warrants': copy.deepcopy(warrants),
        'known_defect_catches': catches,
        'known_defect_misses': [len(defect_ids) - sum(v[1] for v in catches.values()),
                                len(defect_ids) - sum(v[0] for v in catches.values())],
        'false_blocker_incidence': [int('contradicted' in blockers),
                                     int(any(s != 'supported' for s in possible_blockers))],
        'unresolved_new_findings': [w['finding_id'] for w in warrants if w['unresolved_new_defect']],
        'recall_scope': 'supplied-known-defects-only', 'whole_case_cleanliness_established': False,
        'warrant_truth_verified': False, 'ranking_eligible': False}
