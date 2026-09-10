import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_scheduler_graph_witness import assess
from verify_reviewer_scheduler_witness import observation_record


class SchedulerGraphWitnessTest(unittest.TestCase):
    def setUp(self):
        self.criteria = {'conditions': ['local-fallback'], 'expected_active_observations': {'local-fallback': 1},
                         'expected_folded_observations': {'local-fallback': 1}, 'expected_selected': {'local-fallback': 'fallback'}}
        observation = {'RecordRef': 4, 'RecordHash': 'a' * 64, 'BackendID': 'capture', 'PassID': 'build',
                       'SourceRunRef': 1, 'DispatchID': 'source', 'SignatureID': 'vendor.monthly-spend-limit',
                       'Classifier': {'PolicyID': 'limits', 'PolicyVersion': 1, 'ContentHash': 'b' * 64},
                       'ObservedAt': '2026-08-21T11:00:00Z', 'ExpiresAt': '2026-08-21T13:00:00Z', 'TTLSeconds': 7200}
        self.decision = {'Seq': 6, 'SchemaVersion': 2, 'RunRef': 5, 'Payload': {'input_preimage': {}}, 'InvalidReason': ''}
        self.row = {'schema': 'caplab.scheduler-graph-output/v1', 'condition': 'local-fallback', 'phase': 'completed',
                    'adapter_dispatches': 0, 'final_records_error': '', 'source_drain_error': '',
                    'input': {'as_of': '2026-08-21T12:00:00Z', 'capacity_observations': [observation]},
                    'folded_capacity_observations': [observation], 'records_before': 1,
                    'records': [{'Seq': 4, 'Type': 'capacity_observation', 'Payload': observation_record(observation)['payload']},
                                {'Seq': 6, 'Type': 'scheduling_decision', 'SchemaVersion': 2, 'Payload': self.decision['Payload']}],
                    'decision': self.decision, 'decision_created': True, 'binding_created': True, 'outcome': 'binding',
                    'selected': {'backend_id': 'fallback', 'dispatch_id': 'new'},
                    'reopened_decisions': [self.decision], 'reopened_run': {'BackendID': 'fallback', 'DispatchID': 'new'},
                    'repeat_decision_created': False, 'repeat_binding_created': False, 'repeat_added_records': 0,
                    'counterfactual_bindings': [{'BackendID': 'capture'}]}
        for field in ('decision_error', 'binding_preimage_error', 'binding_error', 'reopen_error',
                      'repeat_decision_error', 'repeat_binding_error', 'counterfactual_clock_error', 'counterfactual_error'):
            self.row[field] = ''

    def test_valid_graph_does_not_establish_complete_decision_evidence(self):
        self.assertTrue(assess(self.row, self.criteria)['graph_accepted_missing_causal_input'])
        observation = self.row['input']['capacity_observations'][0]
        self.decision['Payload']['input_preimage']['capacity_observations'] = [observation_record(observation)]
        result = assess(self.row, self.criteria)
        self.assertTrue(result['active_observations_retained'])
        self.assertFalse(result['graph_accepted_missing_causal_input'])

    def test_missing_input_without_placement_effect_is_a_weaker_observation(self):
        self.row['counterfactual_bindings'] = [{'BackendID': 'fallback'}]
        result = assess(self.row, self.criteria)
        self.assertFalse(result['active_observations_retained'])
        self.assertFalse(result['graph_accepted_missing_causal_input'])

    def test_setup_failure_and_external_effect_are_never_defect_measurements(self):
        for field, value in [('phase', 'source-observation-setup'), ('adapter_dispatches', 1),
                             ('capture_error', 'missing object'), ('source_drain_error', 'manifest invalid')]:
            row = copy.deepcopy(self.row)
            row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                assess(row, self.criteria)

    def test_graph_record_and_reopened_binding_must_support_the_report(self):
        for mutation in ('missing-observation-record', 'changed-reopened-binding', 'invalid-fold'):
            row = copy.deepcopy(self.row)
            if mutation == 'missing-observation-record':
                row['records'] = row['records'][1:]
            elif mutation == 'changed-reopened-binding':
                row['reopened_run']['BackendID'] = 'capture'
            else:
                row['decision']['InvalidReason'] = 'observation preimage mismatch'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                assess(row, self.criteria)

    def test_refusal_is_not_an_accepted_incomplete_record(self):
        self.row.update(phase='decision-refused', decision_error='version moved', decision_created=False)
        self.row['records'] = self.row['records'][:1]
        self.assertFalse(assess(self.row, self.criteria)['graph_accepted_missing_causal_input'])
        self.row['records'].append({'Seq': 8, 'Type': 'unexpected-side-effect'})
        with self.assertRaises(ValueError):
            assess(self.row, self.criteria)


if __name__ == '__main__':
    unittest.main()
