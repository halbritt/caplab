"""Development oracle for trusted local witnesses; never a sandbox or study scorer."""

from contextlib import closing
import sqlite3


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


def observe(transfer, connection, arguments):
    # Candidate exceptions are observations; setup/oracle exceptions propagate.
    try:
        return transfer(connection, *arguments)
    except Exception as error:
        return error


def sequence_check(transfer, calls, *, balances=None):
    model_balances, model_requests = dict(balances or INITIAL), {}
    with closing(database(balances=model_balances)) as connection:
        for index, arguments in enumerate(calls):
            expected = expected_step(model_balances, model_requests, arguments)
            actual = observe(transfer, connection, arguments)
            outcome_ok = isinstance(actual, expected) if isinstance(expected, type) else actual == expected
            if not outcome_ok or snapshot(connection) != (model_balances, model_requests) or connection.in_transaction:
                return {'status': 'failed', 'step': index, 'outcome_type': type(actual).__name__,
                        'outcome_agrees': outcome_ok, 'state_agrees': snapshot(connection) == (model_balances, model_requests),
                        'transaction_open': connection.in_transaction}
    return {'status': 'passed', 'steps': len(calls)}


class UnsupportedOracleOperation(Exception):
    pass


class StatementProbe:
    """Inject once before execute; other connection surfaces remain unassessed."""
    def __init__(self, connection, fail_at=None):
        self.connection, self.fail_at, self.calls = connection, fail_at, 0
        self.error = sqlite3.OperationalError('synthetic before-statement failure')

    @property
    def in_transaction(self):
        return self.connection.in_transaction

    def execute(self, *args, **kwargs):
        self.calls += 1
        if self.calls == self.fail_at:
            raise self.error
        return self.connection.execute(*args, **kwargs)

    def __getattr__(self, name):
        raise UnsupportedOracleOperation('unassessed connection operation: ' + name)


def statement_failures(transfer, *, replay=False):
    arguments = ('request-1', 'source', 'destination', 20)
    with closing(database()) as connection:
        if replay:
            outcome = observe(transfer, connection, arguments)
            if outcome != 'applied': return {'status': 'unavailable', 'reason': 'replay setup failed'}
        probe = StatementProbe(connection)
        outcome = observe(transfer, probe, arguments)
        if isinstance(outcome, UnsupportedOracleOperation):
            return {'status': 'unavailable', 'reason': str(outcome)}
        expected = 'replayed' if replay else 'applied'
        if outcome != expected:
            return {'status': 'failed', 'reason': 'baseline outcome differs'}
        count = probe.calls
        if count == 0:
            return {'status': 'unavailable', 'reason': 'no observed statement boundary'}
    failures = []
    for boundary in range(1, count + 1):
        with closing(database()) as connection:
            if replay: transfer(connection, *arguments)
            before = snapshot(connection)
            probe = StatementProbe(connection, boundary)
            outcome = observe(transfer, probe, arguments)
            if isinstance(outcome, UnsupportedOracleOperation):
                return {'status': 'unavailable', 'reason': str(outcome)}
            preserved = snapshot(connection) == before and not connection.in_transaction
            propagated = isinstance(outcome, sqlite3.Error)
            retry = observe(transfer, connection, arguments) if preserved else None
            expected_balances, expected_requests = dict(INITIAL), {}
            expected_step(expected_balances, expected_requests, arguments)
            recovered = (retry == expected and snapshot(connection) == (expected_balances, expected_requests)
                         and not connection.in_transaction)
            if not (preserved and propagated and recovered):
                failures.append({'boundary': boundary, 'state_preserved': preserved,
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
    return {'schema': 'caplab.atomic-transfer-development-audit/v1', 'checks': checks,
            'independently_validated': False, 'study_eligible': False}
