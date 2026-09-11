"""One native Claude development review with isolated access-token delivery."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parent)]
from reviewer_timeout_witness import sha,write_new,write_json
from reviewer_scheduler_witness import inventory
from reviewer_reddit_recovery_witness import runtime
from reviewer_finding_units_review import PROMPT
from caplab.native_capture_invocation import build_native_capture_invocation,NativeCaptureContext
from caplab.claude_external_credential import open_claude_external_credential

REPO=Path(__file__).resolve().parents[1]
ROOT=Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/claude-output-1')
BINARY=Path('/home/halbritt/.local/share/claude/versions/2.1.268')
AUTH=REPO/'docs/records/authorization-2026-09-10-reviewer-claude-output.md'
EXPIRY=1789092000
BOOTSTRAP='''import os,sys
with open('/credential/access-token','rb') as stream:
    token=stream.read(8193)
if not token or len(token)>8192:
    raise RuntimeError('native credential delivery invalid')
os.environ['CLAUDE_CODE_OAUTH_TOKEN']=token.decode('ascii')
os.execv('/native/claude',['/native/claude',*sys.argv[1:]])
'''


def check(plan):
    if inventory(ROOT/'task')!=plan['task'] or inventory(ROOT/'dependencies')!=plan['dependencies']:
        raise ValueError('task or dependency drift')
    if runtime()!=plan['runtime']:raise ValueError('runtime drift')
    for e in plan['support']:
        if sha(Path(e['path']).read_bytes())!=e['sha256']:raise ValueError('support drift')


def prepare():
    if time.time()>=EXPIRY:raise ValueError('expired')
    invocation=build_native_capture_invocation(REPO/'docs/product/contracts/native-agent-systems.json',
        'claude-fable-5-max',context=NativeCaptureContext('/task/current','/runtime',PROMPT.encode(),str(uuid.uuid4())))
    prior=ROOT.parent/'newsroom-natural-output-2'
    if sha((prior/'preparation.json').read_bytes())!='0a5f444de83daac52326e778a5c4977997a01011b242edcfa0cedf1d464c402c':raise ValueError('source preparation drift')
    original=json.loads((prior/'preparation.json').read_text())
    if inventory(prior/'task')!=original['task'] or inventory(prior/'dependencies')!=original['dependencies'] or runtime()!=original['runtime']:
        raise ValueError('source input drift')
    preflight=ROOT.parent/'claude-preflight-1'
    native=json.loads((preflight/'plan.json').read_text())
    if sha(BINARY.read_bytes())!=native['binary_sha256'] or (preflight/'version.stdout').read_text().strip()!='2.1.268 (Claude Code)':raise ValueError('native preflight drift')
    ROOT.mkdir(mode=0o700)
    for name in ('task','dependencies','readiness-base','readiness-base-capture','readiness-current','readiness-current-capture'):
        shutil.copytree(prior/name,ROOT/name,symlinks=True)
    for name in ('preparation.json','readiness-plan.json'):
        write_new(ROOT/('source-'+name),(prior/name).read_bytes())
    write_new(ROOT/'prompt.txt',PROMPT.encode());write_new(ROOT/'bootstrap.py',BOOTSTRAP.encode())
    schema=REPO/'docs/product/contracts/native-code-review-report-v1.json'
    write_new(ROOT/'task/review-report.schema.json',schema.read_bytes())
    command=invocation['command'][:];command[0]='/native/claude'
    command[-2:-2]=['--safe-mode','--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
        '--tools','Bash,Read,Grep,Glob','--json-schema',schema.read_text()]
    invocation['environment'].update(PYTHONPATH='/dependencies:/task/current',PYTHONDONTWRITEBYTECODE='1')
    support=[Path(__file__),AUTH,BINARY,ROOT/'bootstrap.py',ROOT/'prompt.txt',
        REPO/'scripts/reviewer_finding_units_review.py',REPO/'scripts/reviewer_reddit_recovery_witness.py',
        REPO/'scripts/reviewer_scheduler_witness.py',REPO/'scripts/reviewer_timeout_witness.py',
        REPO/'src/caplab/claude_external_credential.py',REPO/'src/caplab/codex_external_credential.py',
        REPO/'src/caplab/revbench/codex.py',REPO/'src/caplab/native_capture_invocation.py',
        REPO/'src/caplab/subject_identity.py',REPO/'docs/product/contracts/native-agent-systems.json',schema]
    plan={'schema':'caplab.claude-review-development/v1','invocation':invocation,'actual_command':command,
        'task':inventory(ROOT/'task'),'dependencies':inventory(ROOT/'dependencies'),'runtime':runtime(),
        'support':[{'path':str(p),'sha256':sha(p.read_bytes())} for p in support],
        'source_preparation_sha256':sha((prior/'preparation.json').read_bytes()),
        'native_preflight_sha256':sha((preflight/'plan.json').read_bytes()),
        'maximum_outer_launches':1,'deadline_seconds':900,'expiry':EXPIRY,
        'source_snapshots':original.get('source_snapshots',original.get('snapshots')),
        'study_eligible':False,'limits':['Exposed development case; no paired comparison.','Credential source identity is pinned privately; provider account identity is not independently verified.','Exact-token guard does not detect transformed secrets.']}
    check(plan);write_new(ROOT/'runner.py',Path(__file__).read_bytes());write_json(ROOT/'plan.json',plan)
    print(json.dumps({'root':str(ROOT),'plan_sha256':sha((ROOT/'plan.json').read_bytes())}))


def run(expected):
    if sha((ROOT/'plan.json').read_bytes())!=expected or time.time()>=EXPIRY:raise ValueError('plan mismatch or expiry')
    plan=json.loads((ROOT/'plan.json').read_text());check(plan)
    if (ROOT/'launch.json').exists():raise ValueError('attempt already consumed')
    source=Path('/home/halbritt/.claude/.credentials.json')
    # The adapter independently verifies source type, owner, mode, link count,
    # size, stability and digest before delivering any bytes.
    fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:raw=os.read(fd,65537)
    finally:os.close(fd)
    source_hash=sha(raw);del raw
    with open_claude_external_credential(source,expected_source_sha256=source_hash,minimum_access_lifetime_seconds=1020) as credential:
        for p in [ROOT/'prompt.txt',*sorted((ROOT/'task').rglob('*'))]:
            if p.is_file():
                guard=credential.quarantine_factory();guard.feed(p.read_bytes());guard.finish()
                if guard.quarantined:raise ValueError('task credential guard refused')
        write_json(ROOT/'private-credential-binding.json',{'source_sha256':source_hash,'delivered':'access token only','refresh_authority':False})
        volatile=Path(tempfile.mkdtemp(prefix='caplab-claude-review-',dir='/dev/shm'))
        try:
            (volatile/'home').mkdir();(volatile/'claude').mkdir()
            args=['/usr/bin/bwrap','--die-with-parent','--unshare-all','--share-net',
                '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
                '--ro-bind','/etc/ssl','/etc/ssl','--ro-bind','/etc/resolv.conf','/etc/resolv.conf',
                '--ro-bind',str(BINARY),'/native/claude','--ro-bind',str(ROOT/'task'),'/task',
                '--ro-bind',str(ROOT/'dependencies'),'/dependencies','--ro-bind',str(ROOT/'bootstrap.py'),'/bootstrap.py',
                '--bind',str(volatile),'/runtime','--ro-bind-data',str(credential.descriptor),'/credential/access-token',
                '--tmpfs','/tmp','--proc','/proc','--dev','/dev','--chdir','/task/current','--clearenv']
            for k,v in plan['invocation']['environment'].items():args+=['--setenv',k,v]
            args+=['--','/usr/bin/python3','-I','-B','/bootstrap.py',*plan['actual_command'][1:]]
            write_json(ROOT/'launch.json',{'command':args,'plan_sha256':expected,'started_at':time.time()})
            start=time.monotonic();termination='exit'
            with (volatile/'stdout').open('wb') as out,(volatile/'stderr').open('wb') as err:
                process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=out,stderr=err,pass_fds=(credential.descriptor,),start_new_session=True)
                write_json(ROOT/'process.json',{'pid':process.pid,'proc_start_ticks':Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]})
                try:process.wait(timeout=min(900,EXPIRY-time.time()))
                except subprocess.TimeoutExpired:
                    termination='deadline';os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=10)
            entries=[];capture=ROOT/'capture';capture.mkdir()
            for path in sorted(volatile.rglob('*')):
                if path.is_symlink() or not path.is_file():continue
                rel=str(path.relative_to(volatile))
                if path.name in ('.credentials.json','auth.json'):
                    entries.append({'path':rel,'disposition':'credential-file-not-retained'});continue
                if path.stat().st_size>32*1024*1024:
                    entries.append({'path':rel,'disposition':'oversized-not-retained'});continue
                guard=credential.quarantine_factory();payload=guard.feed(path.read_bytes())+guard.finish()
                if guard.quarantined:
                    entries.append({'path':rel,'disposition':'quarantined-not-retained'});continue
                destination=capture/rel;destination.parent.mkdir(parents=True,exist_ok=True);write_new(destination,payload)
                entries.append({'path':rel,'sha256':sha(payload),'bytes':len(payload),'disposition':'retained'})
            check(plan)
            write_json(ROOT/'completion.json',{'returncode':process.returncode,'termination':termination,'elapsed_seconds':time.monotonic()-start,'entries':entries,'study_eligible':False})
            print(json.dumps({'root':str(ROOT),'returncode':process.returncode,'termination':termination,'retained_files':sum(e['disposition']=='retained' for e in entries)}))
        finally:shutil.rmtree(volatile)


if __name__=='__main__':
    os.umask(0o077);p=argparse.ArgumentParser();p.add_argument('operation',choices=('prepare','run'));p.add_argument('--plan-sha256');a=p.parse_args()
    prepare() if a.operation=='prepare' else run(a.plan_sha256)
