"""Prospective natural-review development using original newsroom trees."""
import base64
import hashlib
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
from reviewer_scheduler_witness import inventory, execute, namespace
from reviewer_reddit_recovery_witness import runtime
from caplab.native_capture_invocation import build_native_capture_invocation, NativeCaptureContext
from codex_rollout_projection import project_rollout
from caplab.codex_external_credential import open_codex_external_credential

ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/newsroom-natural-output-2')
REPO = Path('/home/halbritt/git/caplab')
BINARY = Path('/home/halbritt/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex')
PROMPT = '''Review the proposed code change in /task/current against /task/base.
The exact patch is /task/change.diff. Original repository documentation is in
those trees. Find actionable defects introduced by this change. For each finding,
give its location, the concrete trigger or scenario, expected and actual behavior,
and why the change causes the problem. Include a reproduction when available.
Distinguish demonstrated behavior from an unverified concern. Report only findings
you can substantiate; do not manufacture a minimum count. Also state material
review limitations. Do not repair the project. Use the supplied source and local
tools; do not search the web, other repositories, or runtime authentication files.
Record the start time with a local clock. Stop investigating after twelve minutes.
Deliver substantiated findings and limitations in a final answer within fifteen minutes.
A final answer is required even if the review is incomplete; do not invent findings.
The supplied Python runtime is /usr/bin/python3. Python test dependencies are
available through PYTHONPATH. Use /tmp for scratch; source trees are read-only.
Original test readiness receipts are in /task/readiness.json.
'''
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-newsroom-natural-output-2.md'
SOURCE = Path('/home/halbritt/git/ai-newsroom')
COMMITS = {'base': '1bfe5a656bcb2c663891afd5f980211a3ef144a8', 'current': '544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f'}

def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(SOURCE), *args])


def materialize(destination, commit):
    destination.mkdir()
    files = []
    for entry in git('ls-tree', '-rz', commit).split(b'\0'):
        if not entry:
            continue
        header, name = entry.split(b'\t', 1)
        mode, kind, blob = header.decode().split()
        relative = Path(name.decode())
        if kind != 'blob' or mode not in ('100644', '100755', '120000') or relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsupported source entry')
        body = git('cat-file', 'blob', blob)
        if hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != blob:
            raise ValueError('source blob mismatch')
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == '120000':
            target = body.decode()
            if not (path.parent / target).resolve().is_relative_to(destination.resolve()):
                raise ValueError('escaping source symlink')
            path.symlink_to(target)
        else:
            write_new(path, body)
            path.chmod(0o500 if mode == '100755' else 0o400)
        files.append({'path': str(relative), 'mode': mode, 'git_blob': blob, 'sha256': sha(body)})
    return {'commit': commit, 'parent': git('rev-parse', commit + '^').decode().strip(),
            'tree': git('rev-parse', commit + '^{tree}').decode().strip(), 'files': files}


def check_preparation(preparation):
    if inventory(ROOT / 'task') != preparation['task'] or inventory(ROOT / 'dependencies') != preparation['dependencies']:
        raise ValueError('task or dependency drift')
    if runtime() != preparation['runtime']:
        raise ValueError('Python runtime drift')
    for entry in preparation['support']:
        if sha(Path(entry['path']).read_bytes()) != entry['sha256']:
            raise ValueError('preparation support drift')
    if sha((ROOT / 'assessment-obligations.json').read_bytes()) != preparation['assessment_obligations_sha256']:
        raise ValueError('assessment obligations drift')


def prepare():
    os.umask(0o077)
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    previous = ROOT.parent / 'newsroom-natural-output-1'
    original = json.loads((previous / 'preparation.json').read_text())
    if sha((previous / 'preparation.json').read_bytes()) != 'b24e38d2df66100223d1549a454df73ff02fc18e384cc45db70cc9e75378c413':
        raise ValueError('failed preparation changed')
    if inventory(previous / 'task') != original['task'] or inventory(previous / 'dependencies') != original['dependencies']:
        raise ValueError('original task or dependency drift')
    if runtime() != original['runtime']:
        raise ValueError('original Python runtime drift')
    ROOT.mkdir(mode=0o700)
    for name in ('task', 'dependencies', 'readiness-base', 'readiness-base-capture', 'readiness-current', 'readiness-current-capture'):
        shutil.copytree(previous / name, ROOT / name, symlinks=True)
    for name in ('prompt.txt', 'projection.py', 'assessment-obligations.json', 'readiness-plan.json'):
        write_new(ROOT / name, (previous / name).read_bytes())
    if (ROOT / 'prompt.txt').read_text() != PROMPT:
        raise ValueError('prompt changed')
    if sha((ROOT / 'assessment-obligations.json').read_bytes()) != original['assessment_obligations_sha256']:
        raise ValueError('assessment obligations changed')
    from verify_reviewer_scheduler_witness import check_process
    for role in COMMITS:
        check_process(ROOT / ('readiness-' + role))
        if inventory(ROOT / ('readiness-' + role + '-capture')) != inventory(previous / ('readiness-' + role + '-capture')):
            raise ValueError('readiness capture copy drift')
    support = [Path(__file__), AUTH, REPO / 'scripts/codex_rollout_projection.py',
               REPO / 'scripts/reviewer_reddit_recovery_witness.py', REPO / 'scripts/reviewer_scheduler_witness.py',
               REPO / 'scripts/reviewer_timeout_witness.py', REPO / 'src/caplab/codex_external_credential.py',
               REPO / 'src/caplab/native_capture_invocation.py', REPO / 'docs/product/contracts/native-agent-systems.json']
    preparation = {**original, 'readiness_inherited_from': str(previous),
        'previous_preparation_sha256': sha((previous / 'preparation.json').read_bytes()),
        'guard_profile': 'credential-private-text/v4',
        'support': [{'path': str(p), 'sha256': sha(p.read_bytes())} for p in support]}
    check_preparation(preparation)
    write_json(ROOT / 'preparation.json', preparation)
    print(json.dumps({'root': str(ROOT), 'preparation_sha256': sha((ROOT / 'preparation.json').read_bytes()),
                      'original_task_unchanged': True, 'readiness_reexecuted': False}))


def main():
    os.umask(0o077)
    preparation = json.loads((ROOT / 'preparation.json').read_text())
    check_preparation(preparation)
    task = ROOT / 'task'
    write_new(ROOT / 'runner.py', Path(__file__).read_bytes())
    invocation = build_native_capture_invocation(REPO / 'docs/product/contracts/native-agent-systems.json',
        'codex-terra-max', context=NativeCaptureContext('/task/current', '/runtime', PROMPT.encode()))
    invocation['environment'].update(PYTHONPATH='/dependencies:/task/current', PYTHONDONTWRITEBYTECODE='1')
    command = invocation['command'][:]
    index = command.index('--sandbox')
    command[index:index + 2] = ['--dangerously-bypass-approvals-and-sandbox', '--ignore-user-config', '--ignore-rules']
    command[0] = '/native/bin/codex'
    command[-2:-2] = ['--disable', 'apps', '--disable', 'plugins', '--disable', 'remote_plugin', '--disable', 'skill_search']
    auth_path = Path('/home/halbritt/.codex/auth.json')
    raw = auth_path.read_bytes()
    tokens = json.loads(raw)['tokens']
    segment = tokens['access_token'].split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(segment + '=' * (-len(segment) % 4)))
    pins = dict(expected_source_sha256=sha(raw), expected_account_sha256=sha(tokens['account_id'].encode()),
                expected_subject_sha256=sha(claims['sub'].encode()))
    plan = dict(schema='caplab.natural-review-development/v1', preparation_sha256=sha((ROOT / 'preparation.json').read_bytes()), assessment_obligations_sha256=sha((ROOT / 'assessment-obligations.json').read_bytes()),
        invocation=invocation, actual_command=command, binary=str(BINARY), binary_sha256=sha(BINARY.read_bytes()),
        version=subprocess.check_output([str(BINARY), '--version']).decode().strip(),
        package_files=[dict(path=str(f.relative_to(BINARY.parent.parent)), sha256=sha(f.read_bytes())) for f in sorted(BINARY.parent.parent.rglob('*')) if f.is_file()], credential_implementation_sha256=sha((REPO / 'src/caplab/codex_external_credential.py').read_bytes()), credential_pins=pins, deadline_seconds=900, maximum_outer_launches=1,
        authorization_sha256=sha(AUTH.read_bytes()),
        runner_sha256=sha(Path(__file__).read_bytes()), study_eligible=False,
        readable_capture_projection=dict(schema='caplab.codex-readable-rollout-projection/v1', implementation_sha256=sha((ROOT / 'projection.py').read_bytes()), policy='Omit only response_item reasoning payload.encrypted_content strings; guard projected content and receipt; preserve all other values and untouched lines.'),
        configuration_change='external filesystem containment; user configuration and rules ignored')
    if plan['version'] != 'codex-cli 0.153.4':
        raise ValueError('unauthorized native version')
    if time.time() >= 1789084800:
        raise ValueError('authorization expired')
    if sha((REPO / 'scripts/codex_rollout_projection.py').read_bytes()) != plan['readable_capture_projection']['implementation_sha256']:
        raise ValueError('projection implementation drift')
    write_json(ROOT / 'plan.json', plan)
    with open_codex_external_credential(auth_path, **pins, minimum_access_lifetime_seconds=1020,
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
                    '--ro-bind', str(ROOT / 'dependencies'), '/dependencies',
                    '--bind', str(volatile), '/runtime', '--ro-bind-data', str(credential.descriptor), '/runtime/codex/auth.json',
                    '--tmpfs', '/tmp', '--proc', '/proc', '--dev', '/dev', '--chdir', '/task/current',
                    '--clearenv']
            for key, value in invocation['environment'].items():
                args += ['--setenv', key, value]
            args += ['--', *command]
            # A version-only namespace check does not contact a provider or consume a review attempt.
            version_args = args[:args.index('--', args.index('--clearenv')) + 1] + ['/native/bin/codex', '--version']
            version = subprocess.run(version_args, pass_fds=(credential.descriptor,), capture_output=True, timeout=10)
            if version.returncode or version.stdout.decode().strip() != plan['version']:
                raise RuntimeError('namespace_version_preflight_failed')
            os.lseek(credential.descriptor, 0, os.SEEK_SET)
            write_json(ROOT / 'launch.json', dict(command=args, started_at=time.time(), plan_sha256=sha((ROOT / 'plan.json').read_bytes())))
            start = time.monotonic()
            with (volatile / 'stdout').open('wb') as out, (volatile / 'stderr').open('wb') as err:
                process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=out, stderr=err, pass_fds=(credential.descriptor,), start_new_session=True)
                write_json(ROOT / 'process.json', dict(pid=process.pid, proc_start_ticks=Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]))
                termination = 'exit'
                try:
                    process.wait(timeout=min(900, 1789084800 - time.time()))
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
            write_json(ROOT / 'completion.json', dict(returncode=process.returncode, termination=termination,
                elapsed_seconds=time.monotonic() - start, entries=entries, study_eligible=False))
            print(json.dumps(dict(custody=str(ROOT), returncode=process.returncode, termination=termination,
                retained_files=sum(e['disposition'] in ('retained', 'projected-retained') for e in entries))))
        finally:
            shutil.rmtree(volatile)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=('prepare', 'run'))
    args = parser.parse_args()
    prepare() if args.operation == 'prepare' else main()
