"""Assess the real recovery duration separately from eventual feed success."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from xml.etree import ElementTree as ET

from reviewer_reddit_recovery_witness import ROOT, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def assess(row, events, server, criteria):
    requests = [e for e in events if e['event'] == 'request']
    if len(requests) != 1 or requests[0]['path'] != '/r/MachineLearning/hot/.rss?limit=25':
        raise ValueError('missing or unexpected endpoint request')
    if any(key.lower() == 'authorization' for key in requests[0]['headers']):
        raise ValueError('unexpected provider credential')
    times = [e['monotonic'] for e in events]
    if times != sorted(times):
        raise ValueError('endpoint times moved backward')
    ticks = [e for e in events if e['event'] == 'byte']
    headers = [e for e in events if e['event'] == 'headers']
    if len(headers) != 1:
        raise ValueError('missing response header receipt')
    activity = [headers[0]['monotonic']] + [e['monotonic'] for e in ticks]
    ends = [e for e in events if e['event'] == 'body-complete']
    if ends:
        activity.append(ends[0]['monotonic'])
    max_gap = max((b - a for a, b in zip(activity, activity[1:])), default=0)
    if row['condition'] == 'drip':
        if not ticks or [e['index'] for e in ticks] != list(range(len(ticks))):
            raise ValueError('drip schedule missing or inconsistent')
        if max_gap >= criteria['socket_timeout_seconds']:
            raise ValueError('fixture allowed the inactivity timeout to expire')
        if server['complete'] and (len(ticks) != criteria['drip_seconds'] or not ends
                or ends[0]['monotonic'] - ticks[0]['monotonic'] < criteria['drip_seconds']):
            raise ValueError('complete drip response did not exercise the frozen duration')
    elif row['condition'] != 'ordinary' or ticks:
        raise ValueError('unexpected condition or ordinary response schedule')
    success = row['error'] is None
    expected = criteria['expected_urls']
    selected = [a['url'] for a in row['articles']]
    filtered = success and selected == expected
    pool_reopens = success and row['reopen_error'] is None and row['articles'] == row['reopened_articles']
    no_extra_request = row['requests_before_reopen'] == row['requests_after_reopen'] == 1
    if success and not server['complete']:
        raise ValueError('harvest claims success before complete fixture delivery')
    limit = criteria['recovery_seconds'] + criteria['timing_tolerance_seconds']
    within = row['elapsed_seconds'] <= limit
    return {'condition': row['condition'], 'elapsed_seconds': row['elapsed_seconds'],
            'configured_budget_seconds': criteria['recovery_seconds'], 'max_byte_gap_seconds': max_gap,
            'budget_respected_with_tolerance': within, 'harvest_succeeded': success,
            'error_type': row['error']['type'] if row['error'] else None,
            'filtered_expected_candidate': filtered, 'pool_reopens': pool_reopens,
            'reopen_without_http': no_extra_request, 'server_completed': server['complete'],
            'feed_recorded_live': row['state'].get('last_status') == 'live',
            'successful_harvest_exceeds_recovery_budget': bool(success and not within)}


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    start, completion = read(ROOT / 'run-started.json'), read(ROOT / 'completion.json')
    if start['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('incomplete or changed administration')
    verify_inputs(plan)
    check_process(ROOT / 'certificate')
    criteria = read(ROOT / 'witness/criteria.json')
    observations, executions = [], []
    semantic = {}
    for repetition in (1, 2):
        for condition in criteria['conditions']:
            name = f'{condition}-{repetition}'
            check_process(ROOT / name)
            capture = ROOT / (name + '-capture')
            entries = inventory(capture)
            if entries != read(ROOT / (name + '-inventory.json')):
                raise ValueError('capture drift')
            row = read(capture / 'observation.json')
            if row['condition'] != condition:
                raise ValueError('misassigned condition')
            source_constants = read(capture / 'harvest-started.json')
            if source_constants['recovery_seconds'] != 180 or source_constants['socket_timeout'] != 30:
                raise ValueError('original time limits were not preserved')
            response = (capture / 'response-body.xml').read_bytes()
            expected = (b' ' * criteria['drip_seconds'] if condition == 'drip' else b'') + (ROOT / 'witness/feed.xml').read_bytes()
            if response != expected or ET.fromstring(response).tag != '{http://www.w3.org/2005/Atom}feed':
                raise ValueError('invalid or changed Atom fixture')
            events = [json.loads(line) for line in (capture / 'server-events.jsonl').read_text().splitlines()]
            started = source_constants['monotonic']
            if row['elapsed_seconds'] < 0 or any(e['monotonic'] < started for e in events):
                raise ValueError('network evidence precedes harvest')
            if row['error'] is None and any(e['monotonic'] > started + row['elapsed_seconds'] for e in events):
                raise ValueError('successful harvest elapsed time contradicts endpoint evidence')
            result = assess(row, events, read(capture / 'server-completion.json'), criteria)
            with sqlite3.connect((capture / 'provider/rss.db').as_uri() + '?mode=ro', uri=True) as db:
                bodies = [body for (body,) in db.execute('SELECT body FROM feeds')]
                candidates = [url for (url,) in db.execute('SELECT url FROM candidates ORDER BY url')]
            if row['error'] is None:
                if bodies != [response] or candidates != criteria['expected_urls']:
                    raise ValueError('durable database differs from harvested response')
                if row['feeds'][0]['body_sha256'] != sha(response):
                    raise ValueError('reported feed hash mismatch')
            meaning = {key: value for key, value in result.items() if key not in ('elapsed_seconds', 'max_byte_gap_seconds')}
            if condition in semantic and meaning != semantic[condition]:
                raise ValueError('semantic observations differ between repetitions')
            semantic[condition] = meaning
            observations.append({'repetition': repetition, **result})
            executions.append({'slot': name, 'captured_files': len(entries),
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
    return {'schema': 'caplab.reddit-recovery-verification/v1', 'plan_sha256': plan_hash,
            'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations,
            'executions': executions, 'semantic_repetitions_match': True, 'ranking_eligible': False, 'limits': criteria['limits']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
