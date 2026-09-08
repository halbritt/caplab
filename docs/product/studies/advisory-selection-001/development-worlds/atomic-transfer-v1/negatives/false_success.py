"""Misleading repair: transaction rollback followed by a false success response."""

import sqlite3


def transfer(connection, request_id, source, destination, amount):
    if (not all(isinstance(v, str) and v for v in (request_id, source, destination))
            or not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0 or source == destination):
        raise ValueError('invalid transfer')
    try:
        connection.execute('BEGIN IMMEDIATE')
        previous = connection.execute('SELECT source, destination, amount FROM transfers WHERE request_id = ?',
                                      (request_id,)).fetchone()
        if previous is not None:
            if previous != (source, destination, amount):
                raise ValueError('conflicting request')
            outcome = 'replayed'
        else:
            balances = dict(connection.execute('SELECT name, balance FROM accounts'))
            if source not in balances or destination not in balances or balances[source] < amount:
                raise ValueError('invalid accounts or funds')
            connection.execute('UPDATE accounts SET balance = balance - ? WHERE name = ?', (amount, source))
            connection.execute('UPDATE accounts SET balance = balance + ? WHERE name = ?', (amount, destination))
            connection.execute('INSERT INTO transfers VALUES (?, ?, ?, ?)', (request_id, source, destination, amount))
            outcome = 'applied'
        connection.execute('COMMIT')
        return outcome
    except sqlite3.Error:
        if connection.in_transaction:
            connection.execute('ROLLBACK')
        return 'applied'
    except ValueError:
        if connection.in_transaction:
            connection.execute('ROLLBACK')
        raise
