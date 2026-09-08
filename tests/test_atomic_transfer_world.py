"""Development oracle discrimination, hand-calculated state examples and concurrency."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest


WORLD = Path(__file__).parents[1] / 'docs/product/studies/advisory-selection-001/development-worlds/atomic-transfer-v1'


def load(relative):
    spec = importlib.util.spec_from_file_location('atomic_transfer_fixture', WORLD / relative)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


oracle = load('oracle.py')
REPAIRS = ('repairs/transaction.py', 'repairs/savepoint.py')


class AtomicTransferWorldTests(unittest.TestCase):
    def test_distinct_repairs_pass_the_same_oracle(self):
        for path in REPAIRS:
            with self.subTest(path=path):
                report = oracle.audit(load(path).transfer)
                self.assertTrue(all(c['status'] == 'passed' for c in report['checks'].values()), report)
                self.assertFalse(report['independently_validated'])
                self.assertFalse(report['study_eligible'])

    def test_parent_passes_happy_path_but_fails_retry_and_atomicity(self):
        report = oracle.audit(load('parent/transfer.py').transfer)['checks']
        self.assertEqual(report['fresh']['status'], 'passed')
        self.assertEqual(report['retry']['status'], 'failed')
        self.assertTrue(any(not row['state_preserved'] for row in report['before_statement_failure']['failures']))

    def test_retry_only_repair_is_not_confused_with_atomicity(self):
        report = oracle.audit(load('negatives/retry_only.py').transfer)['checks']
        self.assertEqual(report['retry']['status'], 'passed')
        self.assertEqual(report['conflicting_retries']['status'], 'passed')
        self.assertEqual(report['before_statement_failure']['status'], 'failed')

    def test_swallowed_error_is_rejected_even_when_rollback_preserves_state(self):
        report = oracle.audit(load('negatives/false_success.py').transfer)['checks']
        self.assertEqual(report['fresh']['status'], 'passed')
        failures = report['before_statement_failure']['failures']
        self.assertTrue(failures)
        self.assertTrue(all(row['state_preserved'] for row in failures))
        self.assertTrue(all(not row['sqlite_error_propagated'] for row in failures))

    def test_oracle_model_has_hand_checked_conservation_and_retry_examples(self):
        balances, requests = {'A': 3, 'B': 0, 'C': 8}, {}
        self.assertEqual(oracle.expected_step(balances, requests, ('one','A','B',3)), 'applied')
        self.assertEqual((balances, requests), ({'A':0,'B':3,'C':8}, {'one':('A','B',3)}))
        self.assertEqual(oracle.expected_step(balances, requests, ('one','A','B',3)), 'replayed')
        self.assertIs(oracle.expected_step(balances, requests, ('one','B','A',3)), ValueError)
        self.assertIs(oracle.expected_step(balances, requests, ('two','A','B',1)), ValueError)
        self.assertEqual((balances, requests), ({'A':0,'B':3,'C':8}, {'one':('A','B',3)}))

    def test_claiming_success_without_writes_cannot_pass_oracle(self):
        report = oracle.audit(lambda connection, *args: 'applied')['checks']
        self.assertEqual(report['fresh']['status'], 'failed')
        self.assertFalse(report['fresh']['state_agrees'])
        self.assertEqual(report['before_statement_failure']['status'], 'unavailable')

    def test_positive_integer_subclasses_follow_the_written_argument_contract(self):
        class Units(int): pass
        for path in REPAIRS:
            with self.subTest(path=path):
                result = oracle.sequence_check(load(path).transfer, [('r','source','destination',Units(2))])
                self.assertEqual(result['status'], 'passed')

    def test_unsupported_fault_injection_surface_is_unavailable_not_false(self):
        repaired = load('repairs/transaction.py').transfer
        class ThroughCursor:
            def __init__(self, connection): self.connection = connection
            @property
            def in_transaction(self): return self.connection.in_transaction
            def execute(self, *args): return self.connection.cursor().execute(*args)
        def candidate(connection, *args): return repaired(ThroughCursor(connection), *args)
        report = oracle.audit(candidate)['checks']
        self.assertEqual(report['fresh']['status'], 'passed')
        self.assertEqual(report['before_statement_failure']['status'], 'unavailable')
        self.assertEqual(report['retry_statement_failure']['status'], 'unavailable')

    def test_concurrent_connections_cannot_overspend_or_duplicate_one_request(self):
        for path in REPAIRS:
            for same_request in (False, True):
                with self.subTest(path=path,same_request=same_request), tempfile.TemporaryDirectory() as directory:
                    database = Path(directory) / 'ledger.sqlite'
                    with closing(oracle.database(database)): pass
                    transfer = load(path).transfer
                    barrier = threading.Barrier(2, timeout=3)
                    def attempt(key):
                        with closing(sqlite3.connect(database, isolation_level=None, timeout=1)) as connection:
                            barrier.wait()
                            result = oracle.observe(transfer, connection, (key,'source','destination',80))
                            self.assertFalse(connection.in_transaction)
                            return result
                    keys = ('shared','shared') if same_request else ('first','second')
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        pending = [pool.submit(attempt,key) for key in keys]
                        outcomes = [future.result(timeout=5) for future in pending]
                    self.assertEqual(sum(oracle.outcome_agrees(value, 'applied') for value in outcomes), 1, outcomes)
                    self.assertTrue(all(any(oracle.outcome_agrees(value, expected)
                                            for expected in ('applied','replayed',ValueError,sqlite3.Error))
                                        for value in outcomes), outcomes)
                    with closing(sqlite3.connect(database, isolation_level=None)) as connection:
                        balances, requests = oracle.snapshot(connection)
                        self.assertEqual(balances, {'source':20,'destination':120,'untouched':7})
                        self.assertEqual(len(requests),1)
                        if same_request:
                            self.assertEqual(transfer(connection,'shared','source','destination',80),'replayed')

    def test_returned_exception_objects_are_not_raised_failures(self):
        repair = load('repairs/transaction.py').transfer
        def candidate(connection, *args):
            try: return repair(connection, *args)
            except Exception as error: return error
        report = oracle.audit(candidate)
        self.assertEqual(report['schema'], 'caplab.atomic-transfer-development-audit/v2')
        for name in ('conflicting_retries', 'invalid_inputs', 'funds_and_exhausted_retry'):
            self.assertEqual(report['checks'][name]['status'], 'failed')
            self.assertEqual(report['checks'][name]['outcome_kind'], 'returned')
            self.assertFalse(report['checks'][name]['outcome_agrees'])
        for name in ('before_statement_failure', 'retry_statement_failure'):
            failures = report['checks'][name]['failures']
            self.assertTrue(failures)
            self.assertTrue(all(row['state_preserved'] and not row['sqlite_error_propagated'] for row in failures))

    def test_schema_mutation_inside_an_atomic_repair_is_rejected(self):
        repair = load('repairs/transaction.py').transfer
        for ddl in ('CREATE TABLE IF NOT EXISTS unrequested (value TEXT)',
                    'CREATE TEMP TABLE IF NOT EXISTS unrequested (value TEXT)',
                    'CREATE INDEX IF NOT EXISTS unrequested ON accounts(balance)',
                    'CREATE TRIGGER IF NOT EXISTS unrequested AFTER INSERT ON transfers BEGIN SELECT 1; END'):
            class WithExtraSchema:
                def __init__(self, connection): self.connection = connection
                @property
                def in_transaction(self): return self.connection.in_transaction
                def execute(self, sql, *args):
                    result = self.connection.execute(sql, *args)
                    if sql == 'BEGIN IMMEDIATE': self.connection.execute(ddl)
                    return result
            def candidate(connection, *args): return repair(WithExtraSchema(connection), *args)
            with self.subTest(ddl=ddl):
                report = oracle.audit(candidate)['checks']
                self.assertEqual(report['fresh']['status'], 'failed')
                self.assertFalse(report['fresh']['schema_agrees'])
                self.assertIsNone(report['fresh']['state_agrees'])
                self.assertEqual(report['before_statement_failure']['status'], 'failed')

    def test_removed_task_table_is_a_schema_failure_without_a_row_read_crash(self):
        def candidate(connection, *args):
            connection.execute('DROP TABLE transfers')
            return 'applied'
        report = oracle.sequence_check(candidate, [('r','source','destination',1)])
        self.assertEqual(report['status'], 'failed')
        self.assertFalse(report['schema_agrees'])
        self.assertIsNone(report['state_agrees'])

    def test_raised_and_returned_unsupported_markers_remain_distinct(self):
        returned = oracle.statement_failures(lambda connection, *args: oracle.UnsupportedOracleOperation('returned'))
        def raised(connection, *args): raise oracle.UnsupportedOracleOperation('raised')
        unavailable = oracle.statement_failures(raised)
        self.assertEqual(returned['status'], 'failed')
        self.assertEqual(unavailable['status'], 'unavailable')

    def test_nonstring_equality_imitation_does_not_satisfy_success_result(self):
        class PretendSuccess:
            def __eq__(self, other): return True
        repair = load('repairs/transaction.py').transfer
        def candidate(connection, *args):
            repair(connection, *args)
            return PretendSuccess()
        result = oracle.sequence_check(candidate, [('r','source','destination',1)])
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(result['state_agrees'])
        self.assertFalse(result['outcome_agrees'])

    def test_catching_an_actual_unsupported_operation_does_not_create_fault_coverage(self):
        repair = load('repairs/transaction.py').transfer
        class ThroughCursor:
            def __init__(self, connection): self.connection = connection
            @property
            def in_transaction(self): return self.connection.in_transaction
            def execute(self, *args): return self.connection.cursor().execute(*args)
        def candidate(connection, *args):
            try: return repair(ThroughCursor(connection), *args)
            except Exception as error: return error
        report = oracle.audit(candidate)['checks']
        self.assertEqual(report['fresh']['status'], 'passed')
        self.assertEqual(report['before_statement_failure']['status'], 'unavailable')
        self.assertEqual(report['retry_statement_failure']['status'], 'unavailable')


if __name__ == '__main__': unittest.main()
