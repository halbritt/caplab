"""Verify original partial-refresh execution without assuming the defect."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from reviewer_partial_refresh_witness import ROOT, CONDITIONS, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def expected_requests(condition, criteria, witness):
    scenario = criteria['conditions'][condition]
    result = []

    def add(host, path, status, body, count=1):
        value = {'host': host, 'path': path, 'status': status,
                 'body_sha256': sha(body), 'body_bytes': len(body)}
        result.extend([value] * count)

    for name in criteria['names']:
        html_path = f'/r/{name}/hot/?limit=25'
        if name in scenario['blocked']:
            add('old.reddit.com', html_path, 403, b'controlled listing unavailable', 2)
            add('www.reddit.com', f'/r/{name}/hot.json?limit=25&raw_json=1', 403, b'controlled listing unavailable', 2)
        else:
            add('old.reddit.com', html_path, 200, (witness / ('empty.html' if scenario['empty'] else name + '.html')).read_bytes())
    if scenario['blocked']:
        names = '+'.join(scenario['blocked'])
        success = scenario['rss_success']
        add('www.reddit.com', f'/r/{names}/hot/.rss?limit={25 * len(scenario["blocked"])}',
            200 if success else 403,
            (witness / 'feed.xml').read_bytes() if success else b'controlled RSS unavailable')
    return result


def assess(row, requests, expected, criteria):
    fields = ('host', 'path', 'status', 'body_sha256', 'body_bytes')
    encode = lambda rows: Counter(tuple(row[field] for field in fields) for row in rows)
    if encode(requests) != encode(expected):
        raise ValueError('original endpoint requests or supplied responses differ from the frozen scenario')
    condition = row['condition']
    database = row['database']
    urls = sorted(candidate['url'] for candidate in database['candidates'])
    control = criteria['controls'].get(condition)
    if control and (row['returncode'] != control['exit'] or urls != sorted(control['urls'])):
        raise ValueError('named original-code control failed')
    failed_refresh = condition.endswith('rss-failure')
    if failed_refresh and (database['state'].get('last_status') != 'unavailable'
                           or database['state'].get('last_error') != 'HTTP 403' or database['feeds']):
        raise ValueError('original no-cache provider failure not established')
    return {'condition': condition, 'returncode': row['returncode'], 'requests': len(requests),
            'candidate_urls': urls, 'last_status': database['state'].get('last_status'),
            'feed_count': len(database['feeds']), 'harvest_timestamp_present': 'last_harvest_at' in database['state'],
            'failed_refresh_reported_success': failed_refresh and row['returncode'] == 0}


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    completion = read(ROOT / 'completion.json')
    if read(ROOT / 'run-started.json')['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('execution incomplete or detached from plan')
    verify_inputs(plan)
    check_process(ROOT / 'certificate')
    criteria = read(ROOT / 'witness/criteria.json')
    observations, executions, meanings = [], [], {}
    for repetition in (1, 2):
        for condition in CONDITIONS:
            name = f'{condition}-{repetition}'
            check_process(ROOT / name)
            capture = ROOT / (name + '-capture')
            entries = inventory(capture)
            if entries != read(ROOT / (name + '-inventory.json')):
                raise ValueError('capture drift')
            row = read(capture / 'observation.json')
            if row['condition'] != condition:
                raise ValueError('misassigned condition')
            expected = expected_requests(condition, criteria, ROOT / 'witness')
            outcome = assess(row, read(capture / 'requests.json'), expected, criteria)
            with sqlite3.connect((capture / 'data/reddit-provider/rss.db').as_uri() + '?mode=ro', uri=True) as db:
                actual = {'state': dict(db.execute('SELECT key, value FROM state')),
                    'candidates': [{'url': url, 'article': json.loads(article)} for url, article in db.execute('SELECT url, article FROM candidates ORDER BY url')],
                    'feeds': [{'url': url, 'fetched_at': when, 'body_sha256': hashlib.sha256(body).hexdigest()}
                              for url, when, body in db.execute('SELECT url, fetched_at, body FROM feeds ORDER BY url')]}
            if actual != row['database']:
                raise ValueError('reported database differs from retained SQLite')
            if condition in meanings and outcome != meanings[condition]:
                raise ValueError('semantic repetitions disagree')
            meanings[condition] = outcome
            observations.append({'repetition': repetition, 'elapsed_seconds': row['elapsed_seconds'], **outcome})
            executions.append({'slot': name, 'captured_files': len(entries),
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
    return {'schema': 'caplab.partial-refresh-witness-verification/v1', 'plan_sha256': plan_hash,
        'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations,
        'executions': executions, 'semantic_repetitions_match': True,
        'elapsed_seconds': completion['elapsed_seconds'], 'ranking_eligible': False,
        'limits': criteria['scope']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
