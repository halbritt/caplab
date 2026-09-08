"""Prospective continuation checks using only newly authored local attempts."""

import copy
import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from caplab.review_dissent.native import load_native_review_instrument, render_native_review_cell
from caplab.review_dissent.native_live import (
    NativeReviewLiveContractError,
    _digest,
    assess_native_review_attempts,
    execute_native_review_trial,
    load_native_review_attempts,
    prepare_native_review_trial,
    record_native_review_observation,
)

ROOT = Path(__file__).parents[1]


class NativeReviewIdentityStopTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        instrument = load_native_review_instrument(
            ROOT / 'docs/product/studies/review-dissent-001/native-instrument.json'
        )
        instrument['execution_order'] = ['r03:fable', 'r04:fable', 'r07:fable']
        self.manifest = {
            'status': 'active', 'authority': 'adr-0044',
            'campaign_id': 'new-local-identity-stop-fixture',
            'manifest_sha256': 'b' * 64, '_verified_manifest_sha256': 'b' * 64,
            '_instrument': instrument, 'runtime_versions': {},
            'storage': {'raw_custody_root': str(self.root)},
            'limits': {'maximum_trials': 5, 'maximum_replacements': 2, 'maximum_wall_clock_hours': 1},
        }

    def stream(self, model='claude-fable-5', fallback=False):
        events = [
            {'type': 'system', 'subtype': 'init', 'model': 'claude-fable-5'},
            {'type': 'assistant', 'message': {'model': model, 'content': []}},
            {'type': 'result', 'subtype': 'success', 'is_error': False, 'result': 'Review recorded.', 'usage': {}},
        ]
        if fallback:
            events.insert(1, {'type': 'system', 'subtype': 'model_refusal_fallback',
                              'original_model': 'claude-fable-5', 'fallback_model': 'another-model'})
        return ('\n'.join(json.dumps(event) for event in events) + '\n').encode()

    def write_sealed(self, path, value, field):
        value = {key: item for key, item in value.items() if key != field}
        value[field] = _digest(value)
        path.write_text(json.dumps(value))
        return value

    def attempt(self, *, number=1, stdout=None, return_code=0):
        slot = number - 1
        instrument = self.manifest['_instrument']
        cell_id, subject_id = instrument['execution_order'][slot].split(':')
        task_id = instrument['cells'][cell_id]['public_task_id']
        root = self.root / 'attempts' / f'a{number:02d}-s{number:02d}-primary'
        task = root / 'input' / task_id
        render_native_review_cell(instrument, cell_id, task)
        (task / 'REVIEW.json').write_text(json.dumps({
            'verdict': 'needs_revision', 'findings': [], 'summary': 'Local fixture only.'
        }))
        stdout = self.stream() if stdout is None else stdout
        (root / 'native.stdout').write_bytes(stdout)
        (root / 'native.stderr').write_bytes(b'')
        launch = self.write_sealed(root / 'launch.json', {
            'schema': 'caplab.review-dissent.native-launch/v1',
            'campaign_id': self.manifest['campaign_id'], 'manifest_sha256': 'b' * 64,
            'attempt_number': number, 'attempt_kind': 'primary', 'slot_index': slot,
            'cell_id': cell_id, 'subject_id': subject_id, 'public_task_id': task_id,
            'tuple_id': instrument['agent_systems'][subject_id]['tuple_id'],
        }, 'launch_sha256')
        self.write_sealed(root / 'completion.json', {
            'schema': 'caplab.review-dissent.native-completion/v1',
            'campaign_id': self.manifest['campaign_id'], 'manifest_sha256': 'b' * 64,
            'launch_sha256': launch['launch_sha256'], 'return_code': return_code,
            'timed_out': False, 'duration_seconds': '1.0',
            'stdout_sha256': sha256(stdout).hexdigest(), 'stderr_sha256': sha256(b'').hexdigest(),
        }, 'completion_sha256')
        observation = record_native_review_observation(self.manifest, attempt_root=root)
        return root, observation

    def test_observation_preserves_execution_status_and_raw_model_assessment(self):
        root, observation = self.attempt(stdout=self.stream(fallback=True))
        self.assertEqual(observation['schema'], 'caplab.review-dissent.native-observation/v2')
        self.assertEqual(observation['status'], 'completed')
        self.assertEqual(observation['model_identity']['status'], 'model-mismatch')
        self.assertEqual(observation['model_identity']['native_stdout_sha256'], observation['output_sha256'])
        self.assertEqual(json.loads((root / 'observation.json').read_text()), observation)

    def test_malformed_stream_retains_unverified_observation(self):
        _, observation = self.attempt(stdout=b'{malformed\n')
        self.assertEqual(observation['status'], 'capture_failure')
        self.assertEqual(observation['model_identity']['status'], 'model-unverified')
        self.assertEqual(observation['model_identity']['reason'], 'native-trace-invalid')

    def test_identity_failure_stops_preparation_without_rendering(self):
        self.attempt(stdout=self.stream(fallback=True))
        attempts = load_native_review_attempts(self.manifest)
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertEqual(state['identity_stop']['attempt_number'], 1)
        self.assertEqual(state['unattempted_primary_slots'], 2)
        before = sorted(str(path) for path in self.root.rglob('*'))
        with patch('caplab.review_dissent.native_live.render_native_review_cell') as render:
            with self.assertRaisesRegex(NativeReviewLiveContractError, 'campaign_stopped'):
                prepare_native_review_trial(self.manifest, slot_index=1, attempt_kind='primary', prior_attempts=attempts)
            render.assert_not_called()
        self.assertEqual(before, sorted(str(path) for path in self.root.rglob('*')))

    def test_missing_identity_blocks_infrastructure_replacement(self):
        self.attempt(stdout=b'', return_code=1)
        attempts = load_native_review_attempts(self.manifest)
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertEqual(state['pending_replacement_for'], 0)
        self.assertEqual(state['identity_stop']['status'], 'model-unverified')
        with self.assertRaisesRegex(NativeReviewLiveContractError, 'campaign_stopped'):
            prepare_native_review_trial(self.manifest, slot_index=0, attempt_kind='replacement', prior_attempts=attempts)

    def test_stale_caller_state_cannot_advance_a_different_accounting_history(self):
        self.attempt(stdout=self.stream(), return_code=1)
        attempts = load_native_review_attempts(self.manifest)
        stale = copy.deepcopy(attempts)
        stale[0]['status'] = 'completed'
        with self.assertRaisesRegex(NativeReviewLiveContractError, 'prior_attempts_changed'):
            prepare_native_review_trial(self.manifest, slot_index=1, attempt_kind='primary', prior_attempts=stale)
        self.assertEqual(len(list((self.root / 'attempts').iterdir())), 1)

    def test_matching_model_allows_next_preparation(self):
        root, _ = self.attempt()
        attempts = load_native_review_attempts(self.manifest)
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertIsNone(state['stop_reason'])
        next_root, command = prepare_native_review_trial(
            self.manifest, slot_index=1, attempt_kind='primary', prior_attempts=attempts)
        self.assertTrue((next_root / 'launch.json').is_file())
        self.assertTrue(command)
        self.assertTrue((root / 'observation.json').is_file())


    def test_matching_model_preserves_infrastructure_replacement_policy(self):
        self.attempt(return_code=1)
        attempts = load_native_review_attempts(self.manifest)
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertEqual(state['pending_replacement_for'], 0)
        self.assertIsNone(state['stop_reason'])
        root, _ = prepare_native_review_trial(
            self.manifest, slot_index=0, attempt_kind='replacement', prior_attempts=attempts)
        launch = json.loads((root / 'launch.json').read_text())
        self.assertEqual(launch['attempt_kind'], 'replacement')
        self.assertEqual(launch['attempt_number'], 2)

    def test_execute_cannot_invoke_reviewer_after_identity_stop(self):
        self.attempt(stdout=self.stream(fallback=True))
        attempts = load_native_review_attempts(self.manifest)
        with patch('caplab.review_dissent.native_live.preflight_native_runtime', return_value={}):
            with patch('caplab.review_dissent.native_live.subprocess.run') as run:
                with self.assertRaisesRegex(NativeReviewLiveContractError, 'campaign_stopped'):
                    execute_native_review_trial(self.manifest, slot_index=1, attempt_kind='primary', prior_attempts=attempts)
                run.assert_not_called()
        self.assertEqual(len(list((self.root / 'attempts').iterdir())), 1)

    def test_resealed_subject_metadata_cannot_change_assigned_identity(self):
        root, observation = self.attempt()
        launch = json.loads((root / 'launch.json').read_text())
        launch['subject_id'] = 'gpt'
        launch = self.write_sealed(root / 'launch.json', launch, 'launch_sha256')
        completion = json.loads((root / 'completion.json').read_text())
        completion['launch_sha256'] = launch['launch_sha256']
        completion = self.write_sealed(root / 'completion.json', completion, 'completion_sha256')
        observation.update(subject_id='gpt', launch_sha256=launch['launch_sha256'], completion_sha256=completion['completion_sha256'])
        self.write_sealed(root / 'observation.json', observation, 'observation_sha256')
        with self.assertRaisesRegex(NativeReviewLiveContractError, 'assignment_mismatch'):
            load_native_review_attempts(self.manifest)

    def test_loader_recomputes_assessment_instead_of_trusting_resealed_positive(self):
        root, observation = self.attempt(stdout=self.stream(fallback=True))
        observation['model_identity'] = {'status': 'native-model-match'}
        self.write_sealed(root / 'observation.json', observation, 'observation_sha256')
        with self.assertRaisesRegex(NativeReviewLiveContractError, 'model_identity_changed'):
            load_native_review_attempts(self.manifest)

    def test_legacy_read_is_nonmutating_and_reports_already_recorded_exposure(self):
        root, observation = self.attempt(stdout=self.stream(fallback=True))
        observation.pop('model_identity', None)
        observation['schema'] = 'caplab.review-dissent.native-observation/v1'
        self.write_sealed(root / 'observation.json', observation, 'observation_sha256')
        self.attempt(number=2)
        before = {path: sha256(path.read_bytes()).hexdigest() for path in self.root.rglob('*') if path.is_file()}
        attempts = load_native_review_attempts(self.manifest)
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(state['identity_stop']['attempt_number'], 1)
        self.assertEqual(state['attempts_after_identity_stop'], 1)
        self.assertEqual(state['unattempted_primary_slots'], 1)
        self.assertIsNotNone(state['stop_reason'])
        self.assertEqual(before, {path: sha256(path.read_bytes()).hexdigest() for path in before})


if __name__ == '__main__':
    unittest.main()
