"""Separate observed natural-review triggers from disputed requirement scope."""
import json
from pathlib import Path
import sqlite3

from reviewer_newsroom_findings_witness import ROOT, NATIVE, CONDITIONS, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def assess(row, requests, criteria):
    expected_paths = sorted(f'/r/{name}/hot/?limit=25' for name in criteria['names'])
    if sorted(r['path'] for r in requests) != expected_paths:
        raise ValueError('expected original listing requests missing or duplicated')
    if any(r['headers'].get('Host') != 'old.reddit.com' for r in requests):
        raise ValueError('unexpected endpoint identity')
    times = [r['monotonic'] for r in requests]
    span = max(times) - min(times)
    results = row['results']
    out = {'condition': row['condition'], 'requests': len(requests), 'request_span_seconds': span,
           'three_listing_requests_within_65_seconds': span < criteria['request_interval_seconds']}
    def valid(label):
        value = results[label]
        if value['error'] is not None or sorted(a['url'] for a in value['articles']) != criteria['expected_urls']:
            raise ValueError('original listing or pool control did not produce the fixture candidates')
    if row['condition'] == 'base-listing':
        valid('listing')
    elif row['condition'] == 'change-pool':
        valid('harvest')
        valid('pool')
        if results['pool']['requests_before'] != results['pool']['requests_after']:
            raise ValueError('pool reopen unexpectedly made a request')
        if sorted(results['pool']['articles'], key=lambda a: a['url']) != sorted(results['harvest']['articles'], key=lambda a: a['url']):
            raise ValueError('durable pool differs from original harvest')
        out['enabled_pool_reopens_without_http'] = True
        for label in ('disabled-harvest', 'disabled-pool'):
            value = results[label]
            out[label] = {'error': value['error'], 'requests': value['requests_after'] - value['requests_before'],
                          'article_count': len(value['articles'])}
    elif row['condition'] == 'change-cli-lock':
        if not results['lock_remains_held'] or results['run']['returncode'] != 2:
            raise ValueError('independent run lock control failed')
        if results['run']['requests_before'] != results['run']['requests_after']:
            raise ValueError('locked run made collection requests')
        out['held_lock_confirmed'] = True
        out['cli_exit_codes'] = {name: results[name]['returncode'] for name in ('harvest', 'run', 'fetch')}
        out['cli_request_counts'] = {name: results[name]['requests_after'] - results[name]['requests_before'] for name in ('harvest', 'run', 'fetch')}
    else:
        raise ValueError('unexpected condition')
    if row['condition'] != 'base-listing':
        database = results['database']
        if sorted(r['url'] for r in database['candidates']) != criteria['expected_urls'] or database['feeds']:
            raise ValueError('expected durable HTML candidates or absence of RSS feed not established')
        out['durable_candidates'] = len(database['candidates'])
        out['next_request_present'] = 'next_request' in database['state']
        out['last_status'] = database['state'].get('last_status')
    return out


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    if read(ROOT / 'run-started.json')['plan_sha256'] != plan_hash:
        raise ValueError('launch plan mismatch')
    completion = read(ROOT / 'completion.json')
    if completion['failures'] or completion['plan_sha256'] != plan_hash:
        raise ValueError('incomplete execution')
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
            outcome = assess(row, read(capture / 'requests.json'), criteria)
            if condition != 'base-listing':
                with sqlite3.connect((capture / 'data/reddit-provider/rss.db').as_uri() + '?mode=ro', uri=True) as db:
                    actual = {'state': dict(db.execute('SELECT key, value FROM state')),
                        'candidates': [{'url': url, 'article': json.loads(article)} for url, article in db.execute('SELECT url, article FROM candidates ORDER BY url')],
                        'feeds': [list(r) for r in db.execute('SELECT url, fetched_at FROM feeds ORDER BY url')]}
                if actual != row['results']['database']:
                    raise ValueError('reported database differs from retained SQLite')
            meaning = {k: v for k, v in outcome.items() if k != 'request_span_seconds'}
            if condition in meanings and meaning != meanings[condition]:
                raise ValueError('repetitions disagree')
            meanings[condition] = meaning
            observations.append({'repetition': repetition, **outcome})
            executions.append({'slot': name, 'captured_files': len(entries),
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
    return {'schema': 'caplab.natural-findings-witness-verification/v1', 'plan_sha256': plan_hash,
        'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations, 'executions': executions,
        'semantic_repetitions_match': True, 'elapsed_seconds': completion['elapsed_seconds'], 'ranking_eligible': False,
        'limits': criteria['scope']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
