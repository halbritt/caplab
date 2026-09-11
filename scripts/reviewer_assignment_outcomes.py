"""Development accounting; supplied identity and evidence are not authenticated.

See COMPLETION-AND-ADVISORIES.md. No rates, rankings or truth judgments are
produced here. Every declared assignment survives in the returned projection.
"""
import copy
from collections import Counter

from reviewer_credit_policy import STATUSES, project_completed_review


def _identity(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty identity or evidence reference required')
    return value


def _by_assignment(records, fields):
    if not isinstance(records, list):
        raise ValueError('assignment records must be an array')
    indexed = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != fields:
            raise ValueError('complete assignment record required')
        identity = _identity(record['assignment_id'])
        if identity in indexed:
            raise ValueError('duplicate assignment identity')
        indexed[identity] = record
    return indexed


def _validate_inputs(assignments, observations):
    assigned = _by_assignment(assignments, {'assignment_id', 'binding_id', 'case_id', 'case_truth_id', 'defect_ids'})
    observed = _by_assignment(observations, {'assignment_id', 'status', 'evidence_record', 'reason', 'report'})
    if not assigned or set(assigned) != set(observed):
        raise ValueError('every declared assignment must have exactly one observation')
    case_truth = {}
    for assignment in assignments:
        for field in ('binding_id', 'case_id', 'case_truth_id'):
            _identity(assignment[field])
        defects = assignment['defect_ids']
        if not isinstance(defects, list):
            raise ValueError('defect identities must be an array')
        identities = {_identity(d) for d in defects}
        if len(identities) != len(defects):
            raise ValueError('duplicate defect identity')
        truth = (assignment['case_truth_id'], frozenset(identities))
        previous = case_truth.setdefault(assignment['case_id'], truth)
        if previous != truth:
            raise ValueError('all bindings must share case truth and known defect identities')
    for observation in observations:
        _identity(observation['evidence_record'])
        _identity(observation['reason'])
        status, report = observation['status'], observation['report']
        if status not in ('completed', 'incomplete', 'unavailable', 'unobserved'):
            raise ValueError('unknown completion evidence state')
        if status == 'completed':
            if report is not None and (not isinstance(report, dict) or
                                       set(report) != {'document', 'warrants', 'advisory_warrants'}):
                raise ValueError('completed review requires its entire report and assessments')
        elif report is not None:
            raise ValueError('unassessed review must preserve artifacts by reference without completed-report scoring')
    return observed


def _advisories(document, warrants):
    fields = {'finding_id', 'advisory_basis', 'judgment_record'}
    if not isinstance(warrants, list) or any(not isinstance(w, dict) or set(w) != fields for w in warrants):
        raise ValueError('complete advisory warrants required')
    by_finding = {}
    for warrant in warrants:
        identity = warrant['finding_id']
        if not isinstance(identity, str) or identity in by_finding:
            raise ValueError('invalid or duplicate advisory finding identity')
        if warrant['advisory_basis'] not in STATUSES:
            raise ValueError('unknown advisory evidence status')
        if not isinstance(warrant['judgment_record'], str) or not warrant['judgment_record'].strip():
            raise ValueError('advisory judgment record required')
        by_finding[identity] = warrant['advisory_basis']
    if set(by_finding) != {f['finding_id'] for f in document['findings']}:
        raise ValueError('every finding must have exactly one advisory warrant')
    active = [f for f in document['findings'] if f['reported']['claim_status'] != 'withdrawn']
    effects = Counter(f['reported']['acceptance_effect'] for f in active)
    definite = [by_finding[f['finding_id']] for f in active if f['reported']['acceptance_effect'] == 'advise']
    possible = [by_finding[f['finding_id']] for f in active
                if f['reported']['acceptance_effect'] in ('advise', 'undetermined')]
    return dict(erroneous_advisory_incidence=[int('contradicted' in definite),
                                            int(any(s != 'supported' for s in possible))],
                finding_occurrences=dict(active=len(active), withdrawn=len(document['findings']) - len(active),
                                         **{effect: effects[effect] for effect in ('advise', 'block', 'undetermined')}),
                finding_occurrences_are_workload=False)


def project_assignments(assignments, observations):
    """Return one row per declared assignment, in assignment order.

    Assignments name assignment_id, binding_id, case_id, case_truth_id and
    defect_ids. Observations name assignment_id, status, evidence_record,
    reason and report. A completed observation may have report=None while
    assessment is pending. Otherwise its report contains document, warrants
    for the existing credit policy, and advisory_warrants. Other statuses
    require report=None; partial artifacts remain at the evidence reference.

    References are retained, not dereferenced. Bounds encode logical evidence
    uncertainty, never probabilities, delivered utility or ranking eligibility.
    """
    by_assignment = _validate_inputs(assignments, observations)
    rows = []
    for assignment in assignments:
        observation = by_assignment[assignment['assignment_id']]
        status = observation['status']
        assessed = status == 'completed' and observation['report'] is not None
        if assessed:
            report = observation['report']
            quality = project_completed_review(report['document'], assignment['defect_ids'], report['warrants'])
            quality.update(_advisories(report['document'], report['advisory_warrants']))
        else:
            quality = dict(known_defect_catches={d: [0, 1] for d in assignment['defect_ids']},
                           known_defect_misses=[0, len(assignment['defect_ids'])],
                           false_blocker_incidence=[0, 1], erroneous_advisory_incidence=[0, 1],
                           finding_occurrences=None, finding_occurrences_are_workload=False,
                           recall_scope='supplied-known-defects-only', whole_case_cleanliness_established=False,
                           warrant_truth_verified=False, ranking_eligible=False)
        quality['schema'] = 'caplab.assignment-quality-projection/v1'
        rows.append(dict(assignment=copy.deepcopy(assignment), observation=copy.deepcopy(observation),
                         completion=[int(status == 'completed'), int(status in ('completed', 'unobserved'))],
                         quality_evidence_state='supplied-warrants' if assessed else 'unassessed',
                         quality=quality))
    return dict(schema='caplab.assignment-outcome-projection/v1', rows=rows,
                evidence_truth_verified=False, completion_authenticity_verified=False,
                assignment_authenticity_verified=False, ranking_eligible=False)
