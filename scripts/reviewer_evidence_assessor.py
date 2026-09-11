"""Native evidence-assessor challenge; no reviewer discovery or ranking."""
import base64
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.path[:0] = ['/home/halbritt/git/caplab/src', '/home/halbritt/git/caplab/scripts']
from reviewer_timeout_witness import sha, write_new, write_json
from reviewer_scheduler_witness import inventory
from reviewer_reddit_recovery_witness import runtime
from caplab.native_capture_invocation import build_native_capture_invocation, NativeCaptureContext
from codex_rollout_projection import project_rollout
from caplab.codex_external_credential import open_codex_external_credential

ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/evidence-assessor-1')
REPO = Path('/home/halbritt/git/caplab')
BINARY = Path('/home/halbritt/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex')
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-evidence-assessor.md'
PROMPT = (ROOT / 'prompt.txt').read_text()
FIXTURE_SHA = 'a610ae6c4cc0266a358b535ad69c987c3b098178837d08fe0449fd3dc6fe508b'
SUPPORT = [Path(__file__), AUTH, REPO/'scripts/reviewer_evidence_assessor_fixture.py',
    REPO/'scripts/reviewer_evidence_assessment.py', REPO/'scripts/codex_rollout_projection.py',
    REPO/'scripts/reviewer_reddit_recovery_witness.py', REPO/'scripts/reviewer_scheduler_witness.py',
    REPO/'scripts/reviewer_timeout_witness.py', REPO/'src/caplab/codex_external_credential.py',
    REPO/'src/caplab/revbench/codex.py', REPO/'src/caplab/native_capture_invocation.py',
    REPO/'src/caplab/subject_identity.py', REPO/'docs/product/contracts/native-agent-systems.json']


def check_preparation(preparation):
    if sha((ROOT/'fixture-plan.json').read_bytes()) != FIXTURE_SHA: raise ValueError('fixture drift')
    if inventory(ROOT/'task') != preparation['task']: raise ValueError('task drift')
    if sha((ROOT/'expected.json').read_bytes()) != preparation['expected_sha256']: raise ValueError('expected assessment drift')
    if sha((ROOT/'prompt.txt').read_bytes()) != preparation['prompt_sha256']: raise ValueError('prompt drift')
    if sha(AUTH.read_bytes()) != preparation['authorization_sha256']: raise ValueError('authorization drift')


def main():
    os.umask(0o077)
    preparation = json.loads((ROOT / 'fixture-plan.json').read_text())
    check_preparation(preparation)
    task = ROOT / 'task'
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    invocation = build_native_capture_invocation(REPO / 'docs/product/contracts/native-agent-systems.json',
        'codex-terra-max', context=NativeCaptureContext('/task', '/runtime', PROMPT.encode()))
    invocation['environment'].update(PYTHONDONTWRITEBYTECODE='1')
    command = invocation['command'][:]
    index = command.index('--sandbox')
    command[index:index + 2] = ['--dangerously-bypass-approvals-and-sandbox', '--ignore-user-config', '--ignore-rules']
    command[0] = '/native/bin/codex'
    command[-2:-2] = ['--disable', 'apps', '--disable', 'plugins', '--disable', 'remote_plugin', '--disable', 'skill_search',
                       '--output-schema', '/task/assessment.schema.json']
    auth_path = Path('/home/halbritt/.codex/auth.json')
    raw = auth_path.read_bytes()
    tokens = json.loads(raw)['tokens']
    segment = tokens['access_token'].split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))
    pins = dict(expected_source_sha256=sha(raw), expected_account_sha256=sha(tokens['account_id'].encode()),
                expected_subject_sha256=sha(claims['sub'].encode()))
    plan = dict(schema='caplab.evidence-assessor-development/v1', fixture_plan_sha256=sha((ROOT / 'fixture-plan.json').read_bytes()),
        invocation=invocation, actual_command=command, binary=str(BINARY), binary_sha256=sha(BINARY.read_bytes()),
        version='codex-cli 0.153.4',
        package_files=[dict(path=str(f.relative_to(BINARY.parent.parent)), sha256=sha(f.read_bytes())) for f in sorted(BINARY.parent.parent.rglob('*')) if f.is_file()], credential_implementation_sha256=sha((REPO / 'src/caplab/codex_external_credential.py').read_bytes()), credential_pins=pins, deadline_seconds=600, maximum_outer_launches=1,
        authorization_sha256=sha(AUTH.read_bytes()),
        runner_sha256=sha(Path(__file__).read_bytes()), study_eligible=False,
        readable_capture_projection=dict(schema='caplab.codex-readable-rollout-projection/v1', implementation_sha256=sha((ROOT / 'projection.py').read_bytes()), policy='Omit only response_item reasoning payload.encrypted_content strings; guard projected content and receipt; preserve all other values and untouched lines.'),
        configuration_change='external filesystem containment; user configuration and rules ignored')
    if plan['version'] != 'codex-cli 0.153.4':
        raise ValueError('unauthorized native version')
    if time.time() >= 1789092000:
        raise ValueError('authorization expired')
    if sha((REPO / 'scripts/codex_rollout_projection.py').read_bytes()) != plan['readable_capture_projection']['implementation_sha256']:
        raise ValueError('projection implementation drift')
    plan['runtime'] = runtime()
    plan['support'] = [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in SUPPORT]
    write_json(ROOT / 'plan.json', plan)
    with open_codex_external_credential(auth_path, **pins, minimum_access_lifetime_seconds=720,
            quarantine_profile='credential-private-text/v4') as credential:
        for path in [ROOT / 'prompt.txt', *sorted(task.rglob('*'))]:
            if path.is_file():
                guard = credential.quarantine_factory()
                guard.feed(path.read_bytes()); guard.finish()
                if guard.quarantined:
                    write_json(ROOT / 'preflight-failure.json', {'reason': 'task rejected by capture guard', 'path': str(path.relative_to(ROOT)), 'model_launched': False})
                    raise ValueError('task rejected by capture guard before launch')
        volatile = Path(tempfile.mkdtemp(prefix='caplab-output-probe-', dir='/dev/shm'))
        try:
            (volatile / 'home').mkdir()
            (volatile / 'codex').mkdir()
            args = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-all', '--share-net',
                    '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
                    '--ro-bind', '/etc/ssl', '/etc/ssl', '--ro-bind', '/etc/resolv.conf', '/etc/resolv.conf',
                    '--ro-bind', str(BINARY.parent.parent), '/native', '--ro-bind', str(task), '/task',
                    '--bind', str(volatile), '/runtime', '--ro-bind-data', str(credential.descriptor), '/runtime/codex/auth.json',
                    '--tmpfs', '/tmp', '--proc', '/proc', '--dev', '/dev', '--chdir', '/task',
                    '--clearenv']
            for key, value in invocation['environment'].items():
                args += ['--setenv', key, value]
            args += ['--', *command]
            # A version-only namespace check does not contact a provider or consume a review attempt.
            version_args = args[:args.index('--', args.index('--clearenv')) + 1] + ['/native/bin/codex', '--version']
            version = subprocess.run(version_args, pass_fds=(credential.descriptor,), capture_output=True, timeout=10)
            if version.returncode or version.stdout.decode().strip() != plan['version']:
                raise RuntimeError('namespace_version_preflight_failed')
            write_json(ROOT / 'version-preflight.json', {'returncode': version.returncode, 'observed_version': plan['version']})
            os.lseek(credential.descriptor, 0, os.SEEK_SET)
            write_json(ROOT / 'launch.json', dict(command=args, started_at=time.time(), plan_sha256=sha((ROOT / 'plan.json').read_bytes())))
            start = time.monotonic()
            with (volatile / 'stdout').open('wb') as out, (volatile / 'stderr').open('wb') as err:
                process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=out, stderr=err, pass_fds=(credential.descriptor,), start_new_session=True)
                write_json(ROOT / 'process.json', dict(pid=process.pid, proc_start_ticks=Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]))
                termination = 'exit'
                try:
                    process.wait(timeout=min(600, 1789092000 - time.time()))
                except subprocess.TimeoutExpired:
                    termination = 'deadline'
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
            entries = []
            retained = ROOT / 'capture'
            retained.mkdir()
            for path in sorted(volatile.rglob('*')):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = str(path.relative_to(volatile))
                if relative == 'codex/auth.json':
                    continue
                if path.stat().st_size > 32 * 1024 * 1024:
                    entries.append(dict(path=relative, disposition='oversized-not-retained'))
                    continue
                payload = path.read_bytes()
                receipt = None
                if Path(relative).match('codex/sessions/*/*/*/rollout-*.jsonl'):
                    try:
                        payload, receipt = project_rollout(payload)
                    except (ValueError, UnicodeError):
                        entries.append(dict(path=relative, disposition='projection-failed-not-retained'))
                        continue
                    receipt.update(source_path=relative, plan_sha256=sha((ROOT / 'plan.json').read_bytes()),
                        implementation_sha256=plan['readable_capture_projection']['implementation_sha256'])
                    receipt_payload = (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode()
                    receipt_guard = credential.quarantine_factory()
                    safe_receipt = receipt_guard.feed(receipt_payload) + receipt_guard.finish()
                    if receipt_guard.quarantined:
                        entries.append(dict(path=relative, disposition='projection-receipt-quarantined'))
                        continue
                guard = credential.quarantine_factory()
                safe = guard.feed(payload) + guard.finish()
                if guard.quarantined:
                    destination = retained / (relative + '.safe-prefix')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    write_new(destination, safe)
                    entries.append(dict(path=relative, disposition='quarantined-prefix-retained', prefix_path=relative + '.safe-prefix', bytes=len(safe), sha256=sha(safe)))
                    continue
                destination = retained / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                write_new(destination, safe)
                entry = dict(path=relative, bytes=len(safe), sha256=sha(safe), disposition='retained')
                if receipt is not None:
                    receipt_relative = Path('projection-receipts') / Path(relative).with_suffix('.receipt.json')
                    (ROOT / receipt_relative).parent.mkdir(parents=True, exist_ok=True)
                    write_new(ROOT / receipt_relative, safe_receipt)
                    entry.update(disposition='projected-retained', projection_receipt=str(receipt_relative),
                                 projection_receipt_sha256=sha(safe_receipt))
                entries.append(entry)
            check_preparation(preparation)
            if runtime() != plan['runtime']: raise ValueError('runtime drift')
            for p in plan['support']:
                if sha(Path(p['path']).read_bytes()) != p['sha256']: raise ValueError('support drift')
            write_json(ROOT / 'completion.json', dict(returncode=process.returncode, termination=termination,
                elapsed_seconds=time.monotonic() - start, entries=entries, study_eligible=False))
            print(json.dumps(dict(custody=str(ROOT), returncode=process.returncode, termination=termination,
                retained_files=sum(e['disposition'] in ('retained', 'projected-retained') for e in entries))))
        finally:
            shutil.rmtree(volatile)

if __name__ == '__main__':
    main()
