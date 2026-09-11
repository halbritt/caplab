import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reviewer_credit_policy import project_completed_review


def finding(identity, *, stance='asserted', effect='block'):
    return {'finding_id': identity, 'reported': {
        'title': 'Fallback input is incomplete',
        'claim': 'The accepted decision omits a required causal input; the source record is also erased.',
        'trigger': 'Recognized exhaustion with an unsupervised fallback.',
        'expected_behavior': 'The decision must retain its complete input.',
        'observed_or_predicted_behavior': 'The decision is accepted without the active input.',
        'change_attribution': 'The predictor change newly permits this incomplete decision to append.',
        'evidence': 'Independent graph observations and original acceptance requirement.',
        'locations': [], 'claim_status': stance, 'acceptance_effect': effect}}


def warrant(identity, match='supported', blocking='supported', *, novel=False):
    return {'finding_id': identity, 'defect_matches': {'missing-input': match},
            'blocking_basis': blocking, 'unresolved_new_defect': novel,
            'judgment_record': 'constructed-policy-test/' + identity}


class ReviewerCreditPolicyTests(unittest.TestCase):
    def test_supported_core_survives_incidental_error_without_accepting_a_scorer(self):
        # The supplied warrant supports the missing-input rationale, while the
        # report's incidental assertion of source-record erasure remains wrong.
        report = {'document_id': 'review', 'findings': [finding('f')], 'limitations': []}
        before = copy.deepcopy(report)
        result = project_completed_review(report, ['missing-input'], [warrant('f')])
        self.assertEqual(result['known_defect_catches'], {'missing-input': [1, 1]})
        self.assertEqual(result['known_defect_misses'], [0, 0])
        self.assertEqual(result['false_blocker_incidence'], [0, 0])
        self.assertEqual(result['document'], before)
        self.assertEqual(report, before)
        self.assertFalse(result['warrant_truth_verified'])
        self.assertFalse(result['ranking_eligible'])

    def test_bounds_equal_the_extremes_of_all_permitted_evidence_resolutions(self):
        report = {'document_id': 'review', 'findings': [finding('a'), finding('b', effect='undetermined')], 'limitations': []}
        choices = {'supported': (True,), 'contradicted': (False,), 'unresolved': (False, True)}
        # Exhaustively resolve uncertainty for two findings and two defects.
        # The oracle enumerates concrete worlds instead of repeating the
        # projection's three-valued interval arithmetic.
        for states in itertools.product(choices, repeat=6):
            judgments = [dict(finding_id=identity, defect_matches={'x': states[offset], 'y': states[offset + 1]},
                blocking_basis=states[4 + index], unresolved_new_defect=False, judgment_record='test/' + identity)
                for index, (identity, offset) in enumerate([('a', 0), ('b', 2)])]
            worlds = []
            for ax, ay, bx, by, a_valid, b_valid, b_blocks in itertools.product(
                    *(choices[s] for s in states), (False, True)):
                caught_x, caught_y = int(ax or bx), int(ay or by)
                worlds.append((caught_x, caught_y, 2 - caught_x - caught_y,
                               int(not a_valid or (b_blocks and not b_valid))))
            expected = [[min(v), max(v)] for v in zip(*worlds)]
            result = project_completed_review(report, ['x', 'y'], judgments)
            with self.subTest(states=states):
                self.assertEqual(result['known_defect_catches'], {'x': expected[0], 'y': expected[1]})
                self.assertEqual(result['known_defect_misses'], expected[2])
                self.assertEqual(result['false_blocker_incidence'], expected[3])

    def test_withdrawal_removes_active_credit_but_uncertain_advice_can_earn_one_catch(self):
        report = {'document_id': 'review', 'findings': [finding('withdrawn', stance='withdrawn'),
            finding('possible', stance='uncertain', effect='advise')], 'limitations': ['No real host observed.']}
        judgments = [warrant('withdrawn'), warrant('possible', 'unresolved', 'unresolved')]
        result = project_completed_review(report, ['missing-input'], judgments)
        self.assertEqual(result['known_defect_catches'], {'missing-input': [0, 1]})
        self.assertEqual(result['known_defect_misses'], [0, 1])
        self.assertEqual(result['false_blocker_incidence'], [0, 0])
        judgments[1]['defect_matches']['missing-input'] = 'supported'
        report['findings'].append(finding('duplicate', stance='uncertain', effect='advise'))
        judgments.append(warrant('duplicate'))
        result = project_completed_review(report, ['missing-input'], judgments)
        self.assertEqual(result['known_defect_catches'], {'missing-input': [1, 1]})
        self.assertEqual(len(result['document']['findings']), 3)
        self.assertEqual(result['document']['limitations'], report['limitations'])

    def test_unknown_effect_or_basis_cannot_become_a_correct_clearance(self):
        report = {'document_id': 'review', 'findings': [finding('f', stance='uncertain', effect='undetermined')], 'limitations': []}
        judgments = [warrant('f', 'contradicted', 'contradicted')]
        result = project_completed_review(report, ['missing-input'], judgments)
        self.assertEqual(result['false_blocker_incidence'], [0, 1])
        self.assertEqual(result['known_defect_misses'], [1, 1])
        report['findings'][0]['reported']['acceptance_effect'] = 'block'
        self.assertEqual(project_completed_review(report, ['missing-input'], judgments)['false_blocker_incidence'], [1, 1])
        judgments[0]['blocking_basis'] = 'unresolved'
        self.assertEqual(project_completed_review(report, ['missing-input'], judgments)['false_blocker_incidence'], [0, 1])
        judgments[0]['blocking_basis'] = 'supported'
        self.assertEqual(project_completed_review(report, ['missing-input'], judgments)['false_blocker_incidence'], [0, 0])
        judgments[0]['blocking_basis'] = 'contradicted'
        report['findings'][0]['reported']['claim_status'] = 'withdrawn'
        self.assertEqual(project_completed_review(report, ['missing-input'], judgments)['false_blocker_incidence'], [0, 0])

    def test_separate_false_blocker_survives_a_true_catch_and_is_not_multiplied(self):
        report = {'document_id': 'review', 'findings': [finding('correct'), finding('wrong'), finding('repeated')], 'limitations': []}
        judgments = [warrant('correct'), warrant('wrong', 'contradicted', 'contradicted'),
                     warrant('repeated', 'contradicted', 'contradicted')]
        result = project_completed_review(report, ['missing-input'], judgments)
        self.assertEqual(result['known_defect_catches'], {'missing-input': [1, 1]})
        self.assertEqual(result['false_blocker_incidence'], [1, 1])

    def test_missing_or_conflicting_accounting_is_not_a_zero_score(self):
        report = {'document_id': 'review', 'findings': [finding('f')], 'limitations': []}
        invalid = [[], [warrant('other')], [warrant('f'), warrant('f')],
            [{**warrant('f'), 'defect_matches': {}}],
            [{**warrant('f'), 'defect_matches': {'missing-input': 'maybe'}}],
            [{**warrant('f'), 'defect_matches': {'missing-input': 'supported', 'foreign': 'supported'}}],
            [{**warrant('f'), 'blocking_basis': 'clear'}],
            [{**warrant('f'), 'judgment_record': ''}],
            [{**warrant('f'), 'unresolved_new_defect': 'false'}]]
        for judgments in invalid:
            with self.subTest(judgments=judgments), self.assertRaises(ValueError):
                project_completed_review(report, ['missing-input'], judgments)
        with self.assertRaises(ValueError):
            project_completed_review(report, ['missing-input', 'missing-input'], [warrant('f')])
        with self.assertRaises(ValueError):
            project_completed_review({**report, 'findings': [finding('f'), finding('f')]}, ['missing-input'], [warrant('f')])
        with self.assertRaises(ValueError):
            project_completed_review(None, ['missing-input'], [])

    def test_unknown_new_defect_survives_an_empty_known_answer_key(self):
        report = {'document_id': 'review', 'findings': [finding('new', stance='uncertain', effect='advise')], 'limitations': []}
        judgment = {**warrant('new', novel=True), 'defect_matches': {}, 'blocking_basis': 'unresolved'}
        result = project_completed_review(report, [], [judgment])
        self.assertEqual(result['known_defect_catches'], {})
        self.assertEqual(result['unresolved_new_findings'], ['new'])
        self.assertFalse(result['whole_case_cleanliness_established'])
        self.assertEqual(result['recall_scope'], 'supplied-known-defects-only')
        # A separately established expanded truth basis can add the cause;
        # this arithmetic does not establish or authorize that expansion.
        result = project_completed_review(report, ['missing-input'], [warrant('new')])
        self.assertEqual(result['known_defect_catches'], {'missing-input': [1, 1]})
        self.assertEqual(result['unresolved_new_findings'], [])
        self.assertFalse(result['ranking_eligible'])


if __name__ == '__main__':
    unittest.main()
