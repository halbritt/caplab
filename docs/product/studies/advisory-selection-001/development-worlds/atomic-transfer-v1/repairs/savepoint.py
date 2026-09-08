"""Candidate repair: savepoint ownership and one set-based balance update."""

import sqlite3


def transfer(connection, request_id, source, destination, amount):
    if (not all(isinstance(v, str) and v for v in (request_id, source, destination))
            or not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0 or source == destination):
        raise ValueError('invalid transfer')
    try:
        connection.execute('SAVEPOINT account_move')
        previous = connection.execute('SELECT source, destination, amount FROM transfers WHERE request_id = ?',
                                      (request_id,)).fetchone()
        if previous is not None and previous != (source, destination, amount):
            raise ValueError('conflicting request')
        if previous is None:
            accounts = dict(connection.execute('SELECT name, balance FROM accounts WHERE name IN (?, ?)',
                                               (source, destination)))
            if source not in accounts or destination not in accounts or accounts[source] < amount:
                raise ValueError('invalid accounts or funds')
            connection.execute('''UPDATE accounts SET balance =
                CASE WHEN name = ? THEN balance - ? ELSE balance + ? END
                WHERE name IN (?, ?)''', (source, amount, amount, source, destination))
            connection.execute('INSERT INTO transfers VALUES (?, ?, ?, ?)', (request_id, source, destination, amount))
        connection.execute('RELEASE account_move')
        return 'applied' if previous is None else 'replayed'
    except (sqlite3.Error, ValueError):
        if connection.in_transaction:
            connection.execute('ROLLBACK TO account_move')
            connection.execute('RELEASE account_move')
        raise
