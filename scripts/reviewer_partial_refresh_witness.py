"""Freeze and execute the original partial-refresh failure and control paths."""
import argparse
import json
import os
from pathlib import Path
import time

from reviewer_reddit_recovery_witness import runtime
from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path(__file__).resolve().parents[1]
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/partial-refresh-witness-1')
NATIVE = ROOT.parent / 'finding-units-review-1'
PROBE = REPO / 'docs/product/studies/reviewer-ranking-001/development-witnesses/partial-refresh/probe.py'
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-partial-refresh-witness.md'
CONDITIONS = {
    'healthy': {'blocked': [], 'empty': False, 'rss_success': False},
    'healthy-empty': {'blocked': [], 'empty': True, 'rss_success': False},
    'mixed-rss-success': {'blocked': ['LocalLLaMA'], 'empty': False, 'rss_success': True},
    'mixed-rss-failure': {'blocked': ['LocalLLaMA'], 'empty': False, 'rss_success': False},
    'mixed-empty-rss-failure': {'blocked': ['LocalLLaMA'], 'empty': True, 'rss_success': False},
    'total-rss-failure': {'blocked': ['MachineLearning', 'LocalLLaMA'], 'empty': False, 'rss_success': False},
}
NAMES = ['MachineLearning', 'LocalLLaMA']


def verify_inputs(plan):
    if runtime() != plan['runtime'] or inventory(ROOT / 'witness') != plan['witness']:
        raise ValueError('runtime or fixture drift')
    if sha((NATIVE / 'preparation.json').read_bytes()) != plan['native_preparation_sha256']:
        raise ValueError('source custody drift')
    for role, entries in plan['sources'].items():
        if inventory(NATIVE / 'task' / role) != entries:
            raise ValueError('original source drift')
    for entry in plan['fixture_origins']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('inherited synthetic fixture drift')
    for entry in plan['support']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('administration drift')


def prepare():
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    ROOT.mkdir(mode=0o700)
    witness = ROOT / 'witness'
    witness.mkdir()
    write_new(witness / 'probe.py', PROBE.read_bytes())
    write_new(witness / 'hosts', b'127.0.0.1 localhost old.reddit.com www.reddit.com\n')
    write_new(witness / 'nsswitch.conf', b'hosts: files\n')
    config = '[sources.reddit]\nenabled = true\nrss_fallback = true\nuse_harvested = true\nmax_workers = 3\n'
    fixture_origins = []
    for name in NAMES:
        source = ROOT.parent / 'newsroom-findings-witness-1/witness' / (name + '.html')
        write_new(witness / (name + '.html'), source.read_bytes())
        fixture_origins.append({'path': str(source), 'sha256': sha(source.read_bytes())})
        config += f'\n[[sources.reddit.subreddits]]\nname = "{name}"\nlimit = 25\nmin_score = 0\nai_focused = true\n'
    write_new(witness / 'empty.html', b'<html><div id="siteTable">there doesn\'t seem to be anything here</div></html>\n')
    feed = '<feed xmlns="http://www.w3.org/2005/Atom"><title>Controlled fresh feed</title><id>urn:caplab:partial-refresh</id><updated>2026-09-10T18:00:00Z</updated><entry><id>fresh</id><title>AI lab releases a research model</title><link href="https://www.reddit.com/r/LocalLLaMA/comments/fresh/model/"/><updated>2026-09-10T18:00:00Z</updated><summary>Fresh synthetic research report.</summary></entry></feed>\n'
    write_new(witness / 'feed.xml', feed.encode())
    write_new(witness / 'sources.toml', config.encode())
    write_new(witness / 'newsroom.toml', b'[digest]\nwindow_hours = 24\n')
    result = execute(ROOT / 'certificate', ['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
        '-keyout', str(witness / 'key.pem'), '-out', str(witness / 'cert.pem'), '-days', '2',
        '-subj', '/CN=old.reddit.com', '-addext', 'subjectAltName=DNS:old.reddit.com,DNS:www.reddit.com'], 15)
    if result['returncode'] or result['timed_out']:
        raise RuntimeError('test certificate failed')
    write_json(witness / 'criteria.json', {
        'conditions': CONDITIONS, 'names': NAMES,
        'controls': {'healthy': {'exit': 0, 'urls': sorted(f'https://example.invalid/{name}/research' for name in NAMES)},
                     'healthy-empty': {'exit': 0, 'urls': []},
                     'mixed-rss-success': {'exit': 0, 'urls': ['https://example.invalid/MachineLearning/research', 'https://www.reddit.com/r/LocalLLaMA/comments/fresh/model/']},
                     'total-rss-failure': {'exit': 1, 'urls': []}},
        'questions': ['Does original CLI report failure when one listing is blocked, RSS fails and no usable cache exists?',
                      'Are available candidates retained, and is a partial empty collection distinguishable from a healthy quiet day?',
                      'Does observed exit status trigger the original Restart=on-failure policy? No service is started.'],
        'scope': ['Review seen before investigation; exposed development case.',
                  'No source functions, constants, clocks, transports or configuration loader are patched.',
                  'Controlled HTTP inputs establish a scenario, not its field prevalence or an observed systemd restart.',
                  'No case admission, whole-patch clean label, scorer acceptance or ranking.']})
    support = [Path(__file__), PROBE, AUTH, REPO / 'scripts/verify_reviewer_partial_refresh_witness.py', REPO / 'scripts/reviewer_reddit_recovery_witness.py',
               REPO / 'scripts/reviewer_scheduler_witness.py', REPO / 'scripts/reviewer_timeout_witness.py']
    preparation = json.loads((NATIVE / 'preparation.json').read_text())
    if sha((NATIVE / 'preparation.json').read_bytes()) != '29fd2a6c00f543804e73f71eb60780eb99e77801cf72b6074610f81f542b0f63':
        raise ValueError('source preparation changed')
    for role, snapshot in preparation['snapshots'].items():
        for entry in snapshot['files']:
            if sha((NATIVE / 'task' / role / entry['path']).read_bytes()) != entry['sha256']:
                raise ValueError('original source custody differs from preparation')
    plan = {'schema': 'caplab.partial-refresh-witness-plan/v1', 'source_snapshots': preparation['snapshots'],
        'sources': {role: inventory(NATIVE / 'task' / role) for role in ('base', 'current')},
        'native_preparation_sha256': sha((NATIVE / 'preparation.json').read_bytes()),
        'runtime': runtime(), 'witness': inventory(witness), 'fixture_origins': fixture_origins,
        'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support],
        'repetitions': 2, 'per_execution_seconds': 60, 'ranking_eligible': False}
    verify_inputs(plan)
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    write_json(ROOT / 'plan.json', plan)
    print(json.dumps({'root': str(ROOT), 'plan_sha256': sha((ROOT / 'plan.json').read_bytes())}))


def run(expected):
    if sha((ROOT / 'plan.json').read_bytes()) != expected or time.time() >= 1789084800:
        raise ValueError('plan mismatch or expired authorization')
    plan = json.loads((ROOT / 'plan.json').read_text())
    verify_inputs(plan)
    write_json(ROOT / 'run-started.json', {'plan_sha256': expected, 'time': time.time()})
    failures = []
    started = time.monotonic()
    for repetition in (1, 2):
        for condition in CONDITIONS:
            name = f'{condition}-{repetition}'
            capture = ROOT / (name + '-capture')
            capture.mkdir()
            role = 'current'
            args = namespace() + ['--uid', '0', '--gid', '0', '--cap-drop', 'ALL', '--cap-add', 'CAP_NET_BIND_SERVICE',
                '--ro-bind', str(NATIVE / 'task' / role), '/source', '--ro-bind', str(ROOT / 'witness'), '/witness',
                '--bind', str(capture), '/capture', '--ro-bind', str(ROOT / 'witness/hosts'), '/etc/hosts',
                '--ro-bind', str(ROOT / 'witness/nsswitch.conf'), '/etc/nsswitch.conf',
                '--ro-bind', str(ROOT / 'witness/sources.toml'), '/source/config/sources.toml',
                '--ro-bind', str(ROOT / 'witness/newsroom.toml'), '/source/config/newsroom.toml',
                '--setenv', 'SSL_CERT_FILE', '/witness/cert.pem', '--setenv', 'PYTHONDONTWRITEBYTECODE', '1',
                '--chdir', '/source', '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py', condition]
            result = execute(ROOT / name, args, min(60, 900 - (time.monotonic() - started), 1789084800 - time.time()))
            write_json(ROOT / (name + '-inventory.json'), inventory(capture))
            if result['returncode'] or result['timed_out']:
                failures.append(name)
                break
        if failures:
            break
    verify_inputs(plan)
    write_json(ROOT / 'completion.json', {'plan_sha256': expected, 'failures': failures,
        'elapsed_seconds': time.monotonic() - started, 'inputs_rechecked': True, 'ranking_eligible': False})
    print(json.dumps({'root': str(ROOT), 'failures': failures}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    os.umask(0o077)
    prepare() if args.operation == 'prepare' else run(args.plan_sha256)
