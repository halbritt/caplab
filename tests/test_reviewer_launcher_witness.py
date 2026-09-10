import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_reviewer_launcher_witness import assess


class LauncherWitnessTests(unittest.TestCase):
    def setUp(self):
        self.condition = 'both-files'
        self.item = {'prefix': '/case/repo space', 'arguments': ['fixture-backend', '--label', 'two words'],
                     'dispatch_expected': True, 'downstream_exit': 17, 'zai': 'zai', 'openrouter': 'or'}
        self.dispatch = {'recorder': True, 'supervisor_executed': False,
            'selected_executable': '/witness/both-files/home/.npm-global/bin/python3',
            'argv': ['-u', '/case/repo space/scripts/supervise_sweep.py', 'fixture-backend',
                     '/case/repo space/advisory/pool-runs/tree-fixture-backend-20260819', '--label', 'two words'],
            'environment': {'ZAI_API_KEY': 'zai', 'OPENROUTER_API_KEY': 'or', 'PYTHONPATH': '/case/repo space/src',
                            'PATH': '/witness/both-files/home/.npm-global/bin:/witness/both-files/fallback-bin:/usr/bin:/bin'},
            'output_exists': True}

    def test_environment_files_without_exported_values_do_not_pass(self):
        self.dispatch['environment']['ZAI_API_KEY'] = None
        result = assess(self.condition, self.item, 17, self.dispatch, True)
        self.assertFalse(result['checks']['environment_exported'])
        self.assertFalse(result['all_named_properties_hold'])

    def test_argument_splitting_and_fallback_executable_are_detected(self):
        wrong = copy.deepcopy(self.dispatch)
        wrong['argv'][-1:] = ['two', 'words']
        self.assertFalse(assess(self.condition, self.item, 17, wrong, True)['checks']['arguments_preserved'])
        wrong = copy.deepcopy(self.dispatch)
        wrong['selected_executable'] = '/witness/both-files/fallback-bin/python3'
        self.assertFalse(assess(self.condition, self.item, 17, wrong, True)['checks']['tool_path_precedence'])

    def test_masked_failure_and_missing_output_directory_cannot_pass(self):
        result = assess(self.condition, self.item, 0, self.dispatch, False)
        self.assertFalse(result['checks']['exit_status_preserved'])
        self.assertFalse(result['checks']['output_directory_created'])

    def test_rejected_input_must_fail_without_dispatch(self):
        self.item['dispatch_expected'] = False
        self.assertTrue(assess(self.condition, self.item, 2, None, False)['all_named_properties_hold'])
        self.assertFalse(assess(self.condition, self.item, 0, None, False)['all_named_properties_hold'])
        self.assertFalse(assess(self.condition, self.item, 2, self.dispatch, False)['all_named_properties_hold'])


if __name__ == '__main__':
    unittest.main()
