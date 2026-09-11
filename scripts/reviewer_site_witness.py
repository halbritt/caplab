"""Exercise original site builder/server revisions with a pinned browser."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from reviewer_reddit_recovery_witness import runtime
from reviewer_scheduler_witness import execute, inventory, namespace
from reviewer_timeout_witness import sha, write_json, write_new

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path('/home/halbritt/git/ai-newsroom')
ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/site-witness-1')
PROBES = REPO / 'docs/product/studies/reviewer-ranking-001/development-witnesses/site'
AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-site-witness.md'
PLAYWRIGHT = Path('/home/halbritt/.npm/_npx/e41f203b7505f1fb/node_modules/playwright-core')
BROWSER = Path('/home/halbritt/.cache/ms-playwright/chromium_headless_shell-1243')
COMMITS = {'base':'623c5f840a8dc813f404994fdfae605dd61cb894',
           'mark':'566e5af24c0a7a7a00e04326de75bf613dedeb6d',
           'icon':'c7535007644ffea29db055365257b4a6f2b4d905'}
EXPIRY = 1789088400


def git(*args):
    return subprocess.check_output(['git','--no-replace-objects','-C',str(SOURCE),*args])


def capture_inventory(root):
    # Original builder links use their namespace /capture target. Preserve
    # that literal target without following it in the host filesystem.
    rows = []
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            rows.append({'path':str(p.relative_to(root)),'symlink':os.readlink(p)})
        elif p.is_file():
            rows.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
    return rows


def fonts():
    return [{'path':str(p),'resolved':str(p.resolve()),'sha256':sha(p.read_bytes())}
        for root in ('/usr/share/fonts','/etc/fonts','/usr/share/fontconfig')
        for p in sorted(Path(root).rglob('*')) if p.is_file()]


def materialize(role, commit):
    root = ROOT / role
    root.mkdir()
    files = []
    for row in git('ls-tree','-rz',commit,'--','newsroom','README.md','pyproject.toml','docs/publication.md','.gitignore').split(b'\0'):
        if not row:continue
        header,name = row.split(b'\t',1)
        mode,kind,blob = header.decode().split()
        if kind!='blob' or mode not in ('100644','100755'):raise ValueError('unsupported source member')
        body = git('cat-file','blob',blob)
        if hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()!=blob:raise ValueError('blob mismatch')
        p = root / name.decode();p.parent.mkdir(parents=True,exist_ok=True)
        write_new(p,body);p.chmod(0o500 if mode=='100755' else 0o400)
        files.append({'path':name.decode(),'mode':mode,'git_blob':blob,'sha256':sha(body)})
    return {'commit':commit,'base':git('rev-parse',commit+'^').decode().strip(),
            'tree':git('rev-parse',commit+'^{tree}').decode().strip(),'files':files}


def verify_inputs(plan):
    if runtime()!=plan['runtime'] or inventory(PLAYWRIGHT)!=plan['playwright'] or inventory(BROWSER)!=plan['browser'] or fonts()!=plan['fonts']:
        raise ValueError('runtime, browser or font drift')
    if inventory(ROOT/'witness')!=plan['witness']:raise ValueError('witness drift')
    for role in COMMITS:
        if inventory(ROOT/role)!=plan['source_inventories'][role]:raise ValueError('source drift')
    for e in plan['support']:
        if sha(Path(e['path']).read_bytes())!=e['sha256']:raise ValueError('support drift')


def prepare():
    if time.time()>=EXPIRY:raise ValueError('authorization expired')
    ROOT.mkdir(mode=0o700)
    snapshots={role:materialize(role,commit) for role,commit in COMMITS.items()}
    if snapshots['mark']['base']!=COMMITS['base'] or snapshots['icon']['base']!=COMMITS['mark']:raise ValueError('change relationship mismatch')
    (ROOT/'witness').mkdir()
    for name in ('probe.py','browser.cjs'):write_new(ROOT/'witness'/name,(PROBES/name).read_bytes())
    package=json.loads((PLAYWRIGHT/'package.json').read_text())
    if package['version']!='1.63.0':raise ValueError('unexpected Playwright version')
    support=[Path(__file__),AUTH,PROBES/'probe.py',PROBES/'browser.cjs',REPO/'scripts/verify_reviewer_site_witness.py',
             REPO/'scripts/reviewer_reddit_recovery_witness.py',REPO/'scripts/reviewer_scheduler_witness.py',
             REPO/'scripts/reviewer_timeout_witness.py',Path('/usr/bin/node'),Path('/usr/bin/git')]
    plan={'schema':'caplab.site-witness-plan/v1','snapshots':snapshots,
        'source_inventories':{role:inventory(ROOT/role) for role in COMMITS},
        'witness':inventory(ROOT/'witness'),'runtime':runtime(),'playwright':inventory(PLAYWRIGHT),
        'browser':inventory(BROWSER),'fonts':fonts(),'expected_browser':'153.0.8010.12',
        'support':[{'path':str(p),'sha256':sha(p.read_bytes())} for p in support],
        'repetitions':2,'execution_seconds':90,'total_seconds':1200,'ranking_eligible':False,
        'criteria':['Original builder persists the source story and renders HTML-like source/pick text literally.',
                    'Pages, CSS and feed serve with the original read-only-origin headers; forbidden paths and POST remain refused.',
                    'Only the icon revision publishes and serves the referenced original SVG with image/svg+xml MIME type.',
                    'At 320, 768 and 1280 CSS-pixel widths the original nameplate and document stay within the viewport.',
                    'Mark revisions visibly render the AI mark beside Newsroom; retain screenshots and computed geometry rather than infer appearance from HTML.',
                    'The SVG renders as an SVG document with AI text in Chromium.',
                    'Only the icon revision ignores the Playwright working path; the source-file control stays unignored.'],
        'limits':['Two adjacent changes in one presentation sequence, not independent incidents.',
                  'Named viewport/browser/security checks do not prove universal accessibility, security or aesthetic approval.',
                  'No native reviewer, corpus admission or ranking.']}
    verify_inputs(plan);write_new(ROOT/'runner.py',Path(__file__).read_bytes());write_json(ROOT/'plan.json',plan)
    print(json.dumps({'root':str(ROOT),'plan_sha256':sha((ROOT/'plan.json').read_bytes())}))


def run(expected):
    if sha((ROOT/'plan.json').read_bytes())!=expected or time.time()>=EXPIRY:raise ValueError('plan mismatch or expiry')
    plan=json.loads((ROOT/'plan.json').read_text());verify_inputs(plan)
    write_json(ROOT/'run-started.json',{'plan_sha256':expected,'time':time.time()})
    start,failures=time.monotonic(),[]
    for repetition in (1,2):
        for role in COMMITS:
            name=f'{role}-{repetition}';capture=ROOT/(name+'-capture');capture.mkdir()
            command=namespace()+['--ro-bind',str(ROOT/role),'/source','--ro-bind',str(ROOT/'witness'),'/witness',
                '--ro-bind',str(PLAYWRIGHT),'/playwright','--ro-bind',str(BROWSER),'/browser',
                '--ro-bind','/etc/fonts','/etc/fonts','--bind',str(capture),'/capture',
                '--setenv','PYTHONDONTWRITEBYTECODE','1','--chdir','/source','--',
                '/usr/bin/python3','-I','-B','/witness/probe.py',role]
            result=execute(ROOT/name,command,min(90,1200-(time.monotonic()-start),EXPIRY-time.time()))
            write_json(ROOT/(name+'-inventory.json'),capture_inventory(capture))
            if result['returncode'] or result['timed_out']:
                failures.append(name);break
        if failures:break
    verify_inputs(plan)
    write_json(ROOT/'completion.json',{'plan_sha256':expected,'failures':failures,'elapsed_seconds':time.monotonic()-start,'ranking_eligible':False})
    print(json.dumps({'root':str(ROOT),'failures':failures}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=('prepare','run'));parser.add_argument('--plan-sha256')
    args=parser.parse_args();os.umask(0o077)
    prepare() if args.operation=='prepare' else run(args.plan_sha256)
