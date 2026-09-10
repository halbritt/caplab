"""Verify actual producer dates, consumer selections and timestamp meanings."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from reviewer_publication_witness import ROOT, COMMITS, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def slug(url):
    return urlparse(url).path.strip('/')


def producer_dates(text):
    result = {}
    for block in re.split(r'(?m)^\s*\[\d+\]\s+\[new\]\s+', text)[1:]:
        urls = re.findall(r'(?m)^\s*URL:\s*(\S+)\s*$', block)
        days = re.findall(r'(?m)^\s*Published:\s*([^\n]+)', block)
        if len(urls) != 1 or len(days) > 1 or slug(urls[0]) in result:
            raise ValueError('ambiguous producer listing')
        result[slug(urls[0])] = days[0].strip() if days else None
    return result


def assess_rss(rss, producer, cli_output, prompt, criteria):
    if set(producer) != set(criteria['producer_entries']):
        raise ValueError('producer did not retain every feed entry')
    if any(producer[key] != value for key, value in criteria['known_dates'].items()) or producer['undated'] is not None:
        raise ValueError('producer precision differs from frozen fixture')
    parsed = {slug(row['url']): row for row in rss['parsed']}
    if len(parsed) != len(rss['parsed']):
        raise ValueError('duplicate parsed article')
    known = set(criteria['known_dates']) - {'non-ai'}
    retained_dates = all(key in parsed and parsed[key].get('published_date') == producer[key]
                         and parsed[key]['published_at'] is None for key in known)
    fetched = sorted(slug(row['url']) for row in rss['fetched'])
    kept = sorted(slug(row['url']) for row in rss['pipeline_kept'])
    cli_ids = sorted(slug(url) for url in re.findall(r'http://127\.0\.0\.1:8765/[^\s]+', cli_output))
    expected = criteria['expected_rss_candidates']
    visible_dates = all(key in parsed and any(parsed[key]['title'] in line
                        and f"@{producer[key]} (time unavailable)" in line for line in prompt.splitlines())
                        for key in expected if producer[key] is not None)
    unknown_preserved = ('undated' in parsed and parsed['undated']['published_at'] is None
                         and parsed['undated'].get('published_date') is None and 'undated' in kept)
    return {'producer_entries': len(producer), 'known_dates_preserved_without_invented_instants': retained_dates,
            'fetched': fetched, 'pipeline_kept': kept, 'cli_candidates': cli_ids,
            'expected_selection_matches': fetched == kept == cli_ids == expected,
            'date_only_evidence_visible_to_curator': visible_dates,
            'unknown_date_preserved': unknown_preserved,
            'non_ai_control_excluded': 'non-ai' not in parsed and 'non-ai' not in cli_ids}


def assess_timestamp(row):
    match = re.search(r'@(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2}))', row['line'])
    if not match:
        raise ValueError('candidate line has no interpretable timestamp')
    original = datetime.fromisoformat(row['published_at'])
    rendered = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
    if original.tzinfo is None:
        raise ValueError('timestamp fixture lacks timezone')
    delta = (rendered - original).total_seconds()
    return {'source_offset_seconds': original.utcoffset().total_seconds(), 'rendered_error_seconds': delta,
            'same_instant': delta == 0}


def assess_instant(row, criteria):
    instant = datetime.fromisoformat(row['published_at'])
    before, after = datetime.fromisoformat(row['before']), datetime.fromisoformat(row['after'])
    if before > after or before.date().isoformat() != criteria['utc_date'] or after.date() != before.date():
        raise ValueError('invalid measured clock interval')
    inside = after - timedelta(hours=24) <= instant <= before
    outside = instant < before - timedelta(hours=24) or instant > after
    if not (inside or outside) or inside != criteria['instant_kept'][row['condition']]:
        raise ValueError('fixture is ambiguous at a moving window boundary')
    return {'condition': row['condition'], 'kept': row['kept'], 'expected_kept': inside,
            'matches': row['kept'] == inside and row['dropped'] == int(not row['kept'])}


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    start, completion = read(ROOT / 'run-started.json'), read(ROOT / 'completion.json')
    if start['plan_sha256'] != plan_hash or completion['plan_sha256'] != plan_hash or completion['failures']:
        raise ValueError('incomplete or changed administration')
    verify_inputs(plan)
    criteria = read(ROOT / 'witness/criteria.json')
    observations, executions = [], []
    for role in COMMITS:
        repetitions = []
        for repetition in range(1, plan['repetitions'] + 1):
            name = f'{role}-{repetition}'
            check_process(ROOT / name)
            capture = ROOT / (name + '-capture')
            entries = inventory(capture)
            if entries != read(ROOT / (name + '-inventory.json')):
                raise ValueError('producer, database or consumer capture drift')
            for command in ('add', 'scan', 'articles-before', 'cli-fetch', 'articles-after'):
                status = read(capture / command / 'completion.json')
                if status['returncode'] or status['timed_out']:
                    raise ValueError('producer setup or CLI execution failed')
            raw = (capture / 'articles-before/stdout').read_text()
            after = (capture / 'articles-after/stdout').read_text()
            if raw != after:
                raise ValueError('preview changed producer unread queue')
            requests = read(capture / 'http-requests.json')
            if not requests or any(r['method'] != 'GET' or r['path'] != '/feed.xml' for r in requests):
                raise ValueError('unexpected producer network effect')
            source = {row['path']: row['sha256'] for row in plan['snapshots'][role]['files']}
            modules = read(capture / 'loaded-source.json')
            if not modules or any(source.get(m['path'].removeprefix('/source/')) != m['sha256'] for m in modules):
                raise ValueError('loaded source identity mismatch')
            rss = assess_rss(read(capture / 'rss.json'), producer_dates(raw), (capture / 'cli-fetch/stdout').read_text(),
                             (capture / 'rss-curator-prompt.txt').read_text(), criteria)
            instants = read(capture / 'instants.json')
            if len(instants) != len(criteria['instant_kept']) or {r['condition'] for r in instants} != set(criteria['instant_kept']):
                raise ValueError('instant conditions missing or duplicated')
            timestamps = read(capture / 'timezone.json')
            if len(timestamps) != 2 or datetime.fromisoformat(timestamps[0]['published_at']) != datetime.fromisoformat(timestamps[1]['published_at']):
                raise ValueError('timestamp fixture instants differ')
            prompt = (capture / 'timezone-curator-prompt.txt').read_text()
            if any(row['line'] not in prompt for row in timestamps):
                raise ValueError('timestamp lines not passed to original curator prompt')
            paths = read(capture / 'paths.json')
            if len(paths) != 3 or {r['condition'] for r in paths} != set(criteria['expected_paths']):
                raise ValueError('path conditions missing or duplicated')
            result = {'rss': rss, 'instants': [assess_instant(r, criteria) for r in instants],
                      'timestamps': [assess_timestamp(r) for r in timestamps],
                      'paths': [{'condition': r['condition'], 'selected': r['resolved'],
                                 'matches': r['exists'] and r['resolved'] == criteria['expected_paths'][r['condition']]} for r in paths],
                      'unread_queue_preserved': True}
            repetitions.append(result)
            observations.append({'role': role, 'repetition': repetition, **result})
            executions.append({'slot': name, 'captured_files': len(entries),
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
        if repetitions[0] != repetitions[1]:
            raise ValueError('semantic observations differ between repetitions')
    return {'schema': 'caplab.publication-verification/v1', 'plan_sha256': plan_hash,
            'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations,
            'executions': executions, 'semantic_repetitions_match': True, 'ranking_eligible': False, 'limits': criteria['limits']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
