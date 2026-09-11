import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reviewer_assignment_outcomes import project_assignments


def assignment(identity='slot', binding='native-a'):
    return dict(assignment_id=identity, binding_id=binding, case_id='actual-change',
                case_truth_id='common-truth-v1', defect_ids=['lost-input'])


def outcome(identity='slot', status='completed', report=None):
    if status == 'completed' and report is None:
        report = dict(document=dict(document_id=identity, findings=[], limitations=[]),
                      warrants=[], advisory_warrants=[])
    return dict(assignment_id=identity, status=status, evidence_record='constructed/' + identity,
                reason='Constructed policy challenge, not native evidence.', report=report)


def report_of(advisories):
    findings, warrants, advice = [], [], []
    for identity, basis, match in advisories:
        findings.append(dict(finding_id=identity, reported=dict(
            title='Check fallback input retention', claim='The fallback may omit the selected input.',
            trigger='Fallback selection after exhaustion.', expected_behavior='Retain the selected input.',
            observed_or_predicted_behavior='An accepted decision lacks the input.',
            change_attribution='The change introduces the alternate append path.',
            evidence='Constructed challenge; warrant truth is not established.', locations=[],
            claim_status='uncertain', acceptance_effect='advise')))
        warrants.append(dict(finding_id=identity, defect_matches={'lost-input': match},
            blocking_basis='contradicted', unresolved_new_defect=False,
            judgment_record='constructed/defect/' + identity))
        advice.append(dict(finding_id=identity, advisory_basis=basis,
                          judgment_record='constructed/advisory/' + identity))
    return dict(document=dict(document_id='report', findings=findings, limitations=[]),
                warrants=warrants, advisory_warrants=advice)


class AssignmentOutcomesTests(unittest.TestCase):
    def test_failed_review_is_not_a_completed_empty_clearance(self):
        assignments = [assignment('empty'), assignment('failed')]
        outcomes = [outcome('empty'), outcome('failed', 'unavailable')]
        result = project_assignments(assignments, outcomes)
        empty, failed = result['rows']
        self.assertEqual(empty['completion'], [1, 1])
        self.assertEqual(empty['quality']['known_defect_misses'], [1, 1])
        self.assertEqual(empty['quality']['false_blocker_incidence'], [0, 0])
        self.assertEqual(failed['completion'], [0, 0])
        self.assertEqual(failed['quality']['known_defect_catches'], {'lost-input': [0, 1]})
        self.assertEqual(failed['quality']['known_defect_misses'], [0, 1])
        self.assertEqual(failed['quality']['false_blocker_incidence'], [0, 1])
        self.assertEqual(failed['quality']['erroneous_advisory_incidence'], [0, 1])
        self.assertFalse(result['ranking_eligible'])
        self.assertEqual([row['assignment'] for row in result['rows']], assignments)
        self.assertEqual([row['observation'] for row in result['rows']], outcomes)

    def test_speculative_advice_cannot_look_like_verified_harmless_advice(self):
        useful = report_of([('catch', 'supported', 'supported')])
        flood = report_of([('catch', 'supported', 'supported')] +
                          [(str(i), 'unresolved', 'unresolved') for i in range(32)])
        result = project_assignments([assignment('useful'), assignment('flood')],
            [outcome('useful', report=useful), outcome('flood', report=flood)])
        good, many = [row['quality'] for row in result['rows']]
        self.assertEqual(good['known_defect_catches'], many['known_defect_catches'])
        self.assertEqual(good['known_defect_catches'], {'lost-input': [1, 1]})
        self.assertEqual(good['false_blocker_incidence'], [0, 0])
        self.assertEqual(many['false_blocker_incidence'], [0, 0])
        self.assertEqual(good['erroneous_advisory_incidence'], [0, 0])
        self.assertEqual(many['erroneous_advisory_incidence'], [0, 1])
        self.assertEqual(many['finding_occurrences']['advise'], 33)
        self.assertFalse(many['finding_occurrences_are_workload'])
        self.assertEqual(result['rows'][1]['observation']['report'], flood)

    def test_frozen_slots_and_common_truth_cannot_disappear_or_disagree(self):
        assignments = [assignment('a', 'native-a'), assignment('b', 'native-b')]
        observations = [outcome('a'), outcome('b')]
        changes = {
            'missing observation': lambda a, o: o.pop(),
            'extra observation': lambda a, o: o.append(outcome('extra')),
            'duplicate observation': lambda a, o: o.append(copy.deepcopy(o[0])),
            'duplicate assignment': lambda a, o: a.append(copy.deepcopy(a[0])),
            'different truth version': lambda a, o: a[1].update(case_truth_id='different-truth'),
            'different defect denominator': lambda a, o: a[1].update(defect_ids=[]),
            'duplicate defect': lambda a, o: a[0].update(defect_ids=['lost-input', 'lost-input']),
            'unknown state': lambda a, o: o[0].update(status='probably-completed'),
            'failed with scored report': lambda a, o: o[0].update(status='incomplete'),
            'missing evidence reference': lambda a, o: o[0].update(evidence_record=''),
        }
        for name, mutate in changes.items():
            with self.subTest(name=name):
                a, o = copy.deepcopy((assignments, observations)); mutate(a, o)
                with self.assertRaises(ValueError):
                    project_assignments(a, o)
        result = project_assignments(assignments, list(reversed(observations)))
        self.assertEqual([r['observation'] for r in result['rows']], observations)

    def test_advisory_bounds_cover_every_permitted_concrete_resolution(self):
        truth_choices = {'supported': (True,), 'contradicted': (False,), 'unresolved': (False, True)}
        effects = {'advise': ('advise',), 'block': ('block',), 'undetermined': ('advise', 'block')}
        for basis_a, basis_b, effect_a, effect_b, withdrawn in itertools.product(
                truth_choices, truth_choices, effects, effects, (False, True)):
            report = report_of([('a', basis_a, 'contradicted'), ('b', basis_b, 'contradicted')])
            a, b = report['document']['findings']
            a['reported']['acceptance_effect'] = effect_a
            b['reported']['acceptance_effect'] = effect_b
            if withdrawn:
                b['reported']['claim_status'] = 'withdrawn'
            concrete = []
            for valid_a, valid_b, action_a, action_b in itertools.product(
                    truth_choices[basis_a], truth_choices[basis_b], effects[effect_a], effects[effect_b]):
                erroneous_findings = []
                for valid, action, active in [(valid_a, action_a, True), (valid_b, action_b, not withdrawn)]:
                    if active and action == 'advise' and not valid:
                        erroneous_findings.append(action)
                concrete.append(int(bool(erroneous_findings)))
            result = project_assignments([assignment()], [outcome(report=report)])
            self.assertEqual(result['rows'][0]['quality']['erroneous_advisory_incidence'],
                             [min(concrete), max(concrete)])

    def test_duplicate_errors_do_not_multiply_incidence_and_withdrawals_remain_visible(self):
        report = report_of([(str(i), 'contradicted', 'contradicted') for i in range(20)])
        report['document']['findings'][-1]['reported']['claim_status'] = 'withdrawn'
        before = copy.deepcopy(report)
        result = project_assignments([assignment()], [outcome(report=report)])
        quality = result['rows'][0]['quality']
        self.assertEqual(quality['erroneous_advisory_incidence'], [1, 1])
        self.assertEqual(quality['finding_occurrences'], dict(active=19, withdrawn=1, advise=19, block=0, undetermined=0))
        self.assertEqual(report, before)
        result['rows'][0]['observation']['report']['document']['findings'].clear()
        self.assertEqual(report, before)

    def test_missing_advisory_judgments_cannot_silently_clear_a_review(self):
        report = report_of([('a', 'supported', 'supported')])
        for corrupt in [[], report['advisory_warrants'] * 2,
                        [dict(finding_id='other', advisory_basis='supported', judgment_record='test')],
                        [dict(finding_id='a', advisory_basis='probably-fine', judgment_record='test')],
                        [dict(finding_id='a', advisory_basis='supported', judgment_record='')]]:
            with self.subTest(warrants=corrupt):
                report['advisory_warrants'] = corrupt
                with self.assertRaises(ValueError):
                    project_assignments([assignment()], [outcome(report=report)])

    def test_unobserved_and_partial_reviews_remain_distinct_without_invented_occurrence_counts(self):
        assignments = [assignment('pending'), assignment('partial')]
        observations = [outcome('pending', 'unobserved'), outcome('partial', 'incomplete')]
        pending, partial = project_assignments(assignments, observations)['rows']
        self.assertEqual(pending['completion'], [0, 1])
        self.assertEqual(partial['completion'], [0, 0])
        for row in [pending, partial]:
            self.assertEqual(row['quality_evidence_state'], 'unassessed')
            self.assertIsNone(row['quality']['finding_occurrences'])
            self.assertEqual(row['quality']['erroneous_advisory_incidence'], [0, 1])
            self.assertFalse(row['quality']['whole_case_cleanliness_established'])
        clean_assignment = assignment('unknown-cleanliness')
        clean_assignment['defect_ids'] = []
        row = project_assignments([clean_assignment], [outcome('unknown-cleanliness')])['rows'][0]
        self.assertEqual(row['quality']['known_defect_misses'], [0, 0])
        self.assertFalse(row['quality']['whole_case_cleanliness_established'])

    def test_native_completion_is_known_while_assessment_is_pending(self):
        observation = outcome()
        observation.update(report=None, reason='Native response complete; evidence assessment pending.')
        row = project_assignments([assignment()], [observation])['rows'][0]
        self.assertEqual(row['completion'], [1, 1])
        self.assertEqual(row['quality_evidence_state'], 'unassessed')
        self.assertEqual(row['quality']['known_defect_misses'], [0, 1])
        self.assertEqual(row['quality']['false_blocker_incidence'], [0, 1])
        self.assertIsNone(row['quality']['finding_occurrences'])
        self.assertEqual(row['observation'], observation)


if __name__ == '__main__':
    unittest.main()
