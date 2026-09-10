"""Freeze and execute original-code investigations of natural review claims."""
import argparse
import json
import os
from pathlib import Path
import time

from reviewer_reddit_recovery_witness import runtime
from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path(__file__).resolve().parents[1]
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/newsroom-findings-witness-1')
NATIVE = ROOT.parent / 'newsroom-natural-output-2'
PROBE = REPO / 'docs/product/studies/reviewer-ranking-001/development-witnesses/newsroom-findings/probe.py'
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-newsroom-findings-witness.md'
CONDITIONS = ['base-listing', 'change-pool', 'change-cli-lock']
NAMES = ['MachineLearning', 'LocalLLaMA', 'OpenAI']


def verify_inputs(plan):
    if runtime() != plan['runtime'] or inventory(ROOT / 'witness') != plan['witness']:
        raise ValueError('runtime or fixture drift')
    if sha((NATIVE / 'preparation.json').read_bytes()) != plan['native_preparation_sha256']:
        raise ValueError('source custody drift')
    for role, entries in plan['sources'].items():
        if inventory(NATIVE / 'task' / role) != entries:
            raise ValueError('original source drift')
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
    write_new(witness / 'hosts', b'127.0.0.1 localhost old.reddit.com\n')
    write_new(witness / 'nsswitch.conf', b'hosts: files\n')
    config = '[sources.reddit]\nenabled = true\nrss_fallback = true\nuse_harvested = true\nmax_workers = 3\n'
    for name in NAMES:
        body = (f'<html><body><div class="thing link" data-timestamp="1789063200000" '
                f'data-score="100" data-comments-count="8" data-domain="example.invalid" '
                f'data-url="https://example.invalid/{name}/research" '
                f'data-permalink="/r/{name}/comments/fresh/research">'
                f'<a class="title">New open model research result for {name}</a></div></body></html>\n')
        write_new(witness / (name + '.html'), body.encode())
        config += f'\n[[sources.reddit.subreddits]]\nname = "{name}"\nlimit = 25\nmin_score = 0\nai_focused = true\n'
    write_new(witness / 'sources.toml', config.encode())
    write_new(witness / 'newsroom.toml', b'[digest]\nwindow_hours = 24\n')
    result = execute(ROOT / 'certificate', ['/usr/bin/openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
        '-keyout', str(witness / 'key.pem'), '-out', str(witness / 'cert.pem'), '-days', '2',
        '-subj', '/CN=old.reddit.com', '-addext', 'subjectAltName=DNS:old.reddit.com'], 15)
    if result['returncode'] or result['timed_out']:
        raise RuntimeError('test certificate failed')
    write_json(witness / 'criteria.json', {
        'conditions': CONDITIONS, 'names': NAMES, 'request_interval_seconds': 65,
        'expected_urls': sorted(f'https://example.invalid/{name}/research' for name in NAMES),
        'controls': ['Both original listing paths must receive the same valid fresh posts through original HTTPS/parser functions.',
                     'Enabled pool reopen preserves the harvested candidates without further HTTP.',
                     'The original run command must return 2 without HTTP while the independent holder retains run.lock.'],
        'questions': ['Does disabling optional RSS prevent harvesting or reading an already valid candidate pool?',
                      'Do harvest and fetch execute while run.lock is held, and does the original run control refuse?',
                      'Are HTML listing requests separated by 65 seconds, and is their observed dispatch behavior new?'],
        'scope': ['The reviewer output was seen before designing these investigations.',
                  'Requirements come from original documentation; a reproduced behavior does not establish a disputed requirement scope.',
                  'No scorer correctness, ranking, live provider prevalence or whole-patch clean claim.']})
    support = [Path(__file__), PROBE, AUTH, REPO / 'scripts/reviewer_reddit_recovery_witness.py',
               REPO / 'scripts/reviewer_scheduler_witness.py', REPO / 'scripts/reviewer_timeout_witness.py']
    preparation = json.loads((NATIVE / 'preparation.json').read_text())
    if sha((NATIVE / 'preparation.json').read_bytes()) != '0a5f444de83daac52326e778a5c4977997a01011b242edcfa0cedf1d464c402c':
        raise ValueError('source preparation changed')
    plan = {'schema': 'caplab.natural-findings-witness-plan/v1', 'source_snapshots': preparation['snapshots'],
        'sources': {role: inventory(NATIVE / 'task' / role) for role in ('base', 'current')},
        'native_preparation_sha256': sha((NATIVE / 'preparation.json').read_bytes()),
        'runtime': runtime(), 'witness': inventory(witness),
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
            role = 'base' if condition == 'base-listing' else 'current'
            args = namespace() + ['--uid', '0', '--gid', '0', '--cap-drop', 'ALL', '--cap-add', 'CAP_NET_BIND_SERVICE',
                '--ro-bind', str(NATIVE / 'task' / role), '/source', '--ro-bind', str(ROOT / 'witness'), '/witness',
                '--bind', str(capture), '/capture', '--ro-bind', str(ROOT / 'witness/hosts'), '/etc/hosts',
                '--ro-bind', str(ROOT / 'witness/nsswitch.conf'), '/etc/nsswitch.conf',
                '--ro-bind', str(ROOT / 'witness/sources.toml'), '/source/config/sources.toml',
                '--ro-bind', str(ROOT / 'witness/newsroom.toml'), '/source/config/newsroom.toml',
                '--setenv', 'SSL_CERT_FILE', '/witness/cert.pem', '--setenv', 'PYTHONDONTWRITEBYTECODE', '1',
                '--chdir', '/source', '--', '/usr/bin/python3', '-I', '-B', '/witness/probe.py', condition]
            result = execute(ROOT / name, args, min(60, 1789084800 - time.time()))
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
