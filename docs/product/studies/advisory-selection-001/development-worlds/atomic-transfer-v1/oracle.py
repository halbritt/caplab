"""Development oracle for trusted local witnesses; never a sandbox or study scorer."""

from contextlib import closing
import sqlite3
from typing import NamedTuple


SCHEMA = '''CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL);
CREATE TABLE transfers (request_id TEXT PRIMARY KEY, source TEXT NOT NULL,
destination TEXT NOT NULL, amount INTEGER NOT NULL);'''
INITIAL = {'source': 100, 'destination': 40, 'untouched': 7}


def database(path=':memory:', balances=None):
    connection = sqlite3.connect(path, isolation_level=None, timeout=1)
    try:
        connection.executescript(SCHEMA)
        connection.executemany('INSERT INTO accounts VALUES (?, ?)', (balances or INITIAL).items())
        return connection
    except BaseException:
        connection.close()
        raise


def snapshot(connection):
    return (dict(connection.execute('SELECT name, balance FROM accounts')),
            dict((row[0], tuple(row[1:])) for row in connection.execute('SELECT * FROM transfers')))


def schema_snapshot(connection):
    return tuple(tuple(connection.execute(
        f'SELECT type, name, tbl_name, sql FROM {table} ORDER BY type, name, tbl_name, sql'))
        for table in ('sqlite_master', 'sqlite_temp_master'))


def state_agreement(connection, expected_rows, expected_schema):
    schema_ok = schema_snapshot(connection) == expected_schema
    # A changed schema may no longer expose the tables required for a row check.
    rows_ok = snapshot(connection) == expected_rows if schema_ok else None
    return schema_ok, rows_ok


def expected_step(balances, requests, arguments):
    """Pure ledger transition, independent of SQL and candidate implementation."""
    key, source, destination, amount = arguments
    if (any(not isinstance(v, str) or v == '' for v in (key, source, destination))
            or isinstance(amount, bool) or not isinstance(amount, int) or amount < 1 or source == destination):
        return ValueError
    if key in requests:
        return 'replayed' if requests[key] == (source, destination, amount) else ValueError
    if source not in balances or destination not in balances or balances[source] < amount:
        return ValueError
    balances[source] -= amount
    balances[destination] += amount
    requests[key] = (source, destination, amount)
    return 'applied'


class Observation(NamedTuple):
    kind: str
    value: object


def observe(transfer, connection, arguments):
    # Candidate exceptions are observations; setup/oracle exceptions propagate.
    try:
        return Observation('returned', transfer(connection, *arguments))
    except Exception as error:
        return Observation('raised', error)


def outcome_agrees(observation, expected):
    if isinstance(expected, type):
        return observation.kind == 'raised' and isinstance(observation.value, expected)
    return (observation.kind == 'returned' and isinstance(observation.value, str)
            and observation.value == expected)


def sequence_check(transfer, calls, *, balances=None):
    model_balances, model_requests = dict(balances or INITIAL), {}
    with closing(database(balances=model_balances)) as connection:
        expected_schema = schema_snapshot(connection)
        for index, arguments in enumerate(calls):
            expected = expected_step(model_balances, model_requests, arguments)
            actual = observe(transfer, connection, arguments)
            outcome_ok = outcome_agrees(actual, expected)
            schema_ok, rows_ok = state_agreement(connection, (model_balances, model_requests), expected_schema)
            if not outcome_ok or not schema_ok or not rows_ok or connection.in_transaction:
                return {'status': 'failed', 'step': index, 'outcome_kind': actual.kind,
                        'outcome_type': type(actual.value).__name__, 'outcome_agrees': outcome_ok,
                        'state_agrees': rows_ok, 'schema_agrees': schema_ok,
                        'transaction_open': connection.in_transaction}
    return {'status': 'passed', 'steps': len(calls)}


class UnsupportedOracleOperation(Exception):
    pass


class StatementProbe:
    """Inject once before execute; other connection surfaces remain unassessed."""
    def __init__(self, connection, fail_at=None):
        self.connection, self.fail_at, self.calls = connection, fail_at, 0
        self.error = sqlite3.OperationalError('synthetic before-statement failure')
        self.unsupported_operation = None

    @property
    def in_transaction(self):
        return self.connection.in_transaction

    def execute(self, *args, **kwargs):
        self.calls += 1
        if self.calls == self.fail_at:
            raise self.error
        return self.connection.execute(*args, **kwargs)

    def __getattr__(self, name):
        self.unsupported_operation = name
        raise UnsupportedOracleOperation('unassessed connection operation: ' + name)


def statement_failures(transfer, *, replay=False):
    arguments = ('request-1', 'source', 'destination', 20)
    with closing(database()) as connection:
        expected_schema = schema_snapshot(connection)
        if replay:
            outcome = observe(transfer, connection, arguments)
            if not outcome_agrees(outcome, 'applied'):
                return {'status': 'unavailable', 'reason': 'replay setup failed'}
        probe = StatementProbe(connection)
        outcome = observe(transfer, probe, arguments)
        if probe.unsupported_operation is not None:
            return {'status': 'unavailable', 'reason': 'unassessed connection operation: ' + probe.unsupported_operation}
        if outcome.kind == 'raised' and isinstance(outcome.value, UnsupportedOracleOperation):
            return {'status': 'unavailable', 'reason': str(outcome.value)}
        expected = 'replayed' if replay else 'applied'
        if not outcome_agrees(outcome, expected):
            return {'status': 'failed', 'reason': 'baseline outcome differs'}
        count = probe.calls
        if count == 0:
            return {'status': 'unavailable', 'reason': 'no observed statement boundary'}
        expected_balances, expected_requests = dict(INITIAL), {}
        expected_step(expected_balances, expected_requests, arguments)
        if (state_agreement(connection, (expected_balances, expected_requests), expected_schema) != (True, True)
                or connection.in_transaction):
            return {'status': 'failed', 'reason': 'baseline state or schema differs'}
    failures = []
    for boundary in range(1, count + 1):
        with closing(database()) as connection:
            expected_schema = schema_snapshot(connection)
            if replay: transfer(connection, *arguments)
            before = snapshot(connection)
            probe = StatementProbe(connection, boundary)
            outcome = observe(transfer, probe, arguments)
            if probe.unsupported_operation is not None:
                return {'status': 'unavailable', 'reason': 'unassessed connection operation: ' + probe.unsupported_operation}
            if outcome.kind == 'raised' and isinstance(outcome.value, UnsupportedOracleOperation):
                return {'status': 'unavailable', 'reason': str(outcome.value)}
            schema_ok, rows_ok = state_agreement(connection, before, expected_schema)
            preserved = schema_ok and rows_ok and not connection.in_transaction
            propagated = outcome_agrees(outcome, sqlite3.Error)
            retry = observe(transfer, connection, arguments) if preserved else None
            expected_balances, expected_requests = dict(INITIAL), {}
            expected_step(expected_balances, expected_requests, arguments)
            recovered = (retry is not None and outcome_agrees(retry, expected)
                         and state_agreement(connection, (expected_balances, expected_requests), expected_schema) == (True, True)
                         and not connection.in_transaction)
            if not (preserved and propagated and recovered):
                failures.append({'boundary': boundary, 'state_preserved': preserved,
                                 'schema_agrees': schema_ok, 'outcome_kind': outcome.kind,
                                 'sqlite_error_propagated': propagated, 'retry_recovered': recovered})
    return {'status': 'failed' if failures else 'passed', 'boundaries': count, 'failures': failures}


def audit(transfer):
    """Return separate observations; no aggregate score or independent verdict."""
    request = ('request-1', 'source', 'destination', 20)
    invalid = [('', 'source', 'destination', 1), ('bad', '', 'destination', 1),
               ('bad', 'source', '', 1), ('bad', 'source', 'source', 1),
               ('bad', 'missing', 'destination', 1), ('bad', 'source', 'missing', 1),
               (None, 'source', 'destination', 1), ('bad', 3, 'destination', 1),
               ('bad', 'source', False, 1)]
    invalid += [('bad', 'source', 'destination', value) for value in (0, -1, True, 1.5, '1', None)]
    checks = {
        'fresh': sequence_check(transfer, [request]),
        'retry': sequence_check(transfer, [request, request]),
        'conflicting_retries': sequence_check(transfer, [request, ('request-1','source','destination',21),
            ('request-1','source','untouched',20), ('request-1','destination','source',20)]),
        'invalid_inputs': sequence_check(transfer, invalid),
        'funds_and_exhausted_retry': sequence_check(transfer, [('large','source','destination',101),
            ('all','source','destination',100), ('all','source','destination',100), ('empty','source','destination',1)]),
        'unicode_names': sequence_check(transfer, [('réessai','café','目的',3), ('réessai','café','目的',3)],
            balances={'café':3,'目的':0,'other':8}),
        'before_statement_failure': statement_failures(transfer),
        'retry_statement_failure': statement_failures(transfer, replay=True),
    }
    # Exercise order, repeated keys and changing balances independently of SQL paths.
    calls = [(f'r-{i}', 'source' if i % 2 == 0 else 'destination',
              'destination' if i % 2 == 0 else 'source', i % 7 + 1) for i in range(50)]
    checks['sequence'] = sequence_check(transfer, [item for call in calls for item in (call, call)])
    return {'schema': 'caplab.atomic-transfer-development-audit/v2', 'checks': checks,
            'independently_validated': False, 'study_eligible': False}
