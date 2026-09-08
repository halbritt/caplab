"""Development parent: a successful example hides interrupted and repeated writes."""


def transfer(connection, request_id, source, destination, amount):
    if (not all(isinstance(v, str) and v for v in (request_id, source, destination))
            or not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0 or source == destination):
        raise ValueError('invalid transfer')
    balances = dict(connection.execute('SELECT name, balance FROM accounts'))
    if source not in balances or destination not in balances or balances[source] < amount:
        raise ValueError('invalid accounts or funds')
    connection.execute('UPDATE accounts SET balance = balance - ? WHERE name = ?', (amount, source))
    connection.execute('UPDATE accounts SET balance = balance + ? WHERE name = ?', (amount, destination))
    connection.execute('INSERT INTO transfers VALUES (?, ?, ?, ?)', (request_id, source, destination, amount))
    return 'applied'
