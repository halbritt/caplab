"""Inspect native Claude capture, preserving administration failures and findings."""
import json
from pathlib import Path
import sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parent)]
from reviewer_claude_output import ROOT,check
from reviewer_timeout_witness import sha
from reviewer_scheduler_witness import inventory
from caplab.codex_events import parse_native_json
from caplab.review_dissent.native import assess_native_review_model
from caplab.native_review_report import inspect_report
from caplab.native_tool_pairs import build_native_tool_pair_report
from verify_reviewer_scheduler_witness import check_process


def verify():
    read=lambda p:json.loads(p.read_text())
    plan=read(ROOT/'plan.json');completion=read(ROOT/'completion.json');check(plan)
    if read(ROOT/'launch.json')['plan_sha256']!=sha((ROOT/'plan.json').read_bytes()):raise ValueError('launch plan mismatch')
    retained=[];missing=[]
    for e in completion['entries']:
        if e['disposition']!='retained':missing.append(e);continue
        p=ROOT/'capture'/e['path']
        if sha(p.read_bytes())!=e['sha256'] or p.stat().st_size!=e['bytes']:raise ValueError('capture drift')
        retained.append(e)
    session=plan['invocation']['session_id'];subject=plan['invocation']['base_subject']
    raw=(ROOT/'capture/stdout').read_bytes()
    events=[parse_native_json(line) for line in raw.decode().splitlines()]
    identity=assess_native_review_model(subject,raw)
    results=[(i+1,e) for i,e in enumerate(events) if e.get('type')=='result']
    terminal=results[0][1] if len(results)==1 else None
    terminal_ok=bool(terminal and results[0][0]==len(events) and terminal.get('subtype')=='success' and terminal.get('is_error') is False and terminal.get('session_id')==session)
    errors=[];inspection=None;final=None
    if terminal_ok:
        structured=terminal.get('structured_output')
        if not isinstance(structured,dict):errors.append('structured_output_missing')
        else:
            final=(json.dumps(structured,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
            try:inspection=inspect_report(final,ROOT/'task/current')
            except ValueError:errors.append('structured_output_contract_invalid')
    else:errors.append('native_terminal_unsuccessful_or_missing')
    pairs=build_native_tool_pair_report(raw,format='claude-stream-jsonl',expected_sha256=sha(raw),expected_root_id=session,max_bytes=32*1024*1024)
    session_files=[p for p in (ROOT/'capture/claude/projects').rglob(session+'.jsonl')] if (ROOT/'capture/claude/projects').exists() else []
    session_observations=[]
    for path in session_files:
        rows=[parse_native_json(line) for line in path.read_text().splitlines()]
        ids=sorted({r['sessionId'] for r in rows if 'sessionId' in r})
        models=sorted({r['message']['model'] for r in rows if r.get('type')=='assistant' and isinstance(r.get('message'),dict) and 'model' in r['message']})
        session_observations.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'session_ids':ids,'models':models})
    session_ok=len(session_observations)==1 and session_observations[0]['session_ids']==[session] and session_observations[0]['models']==[subject['model_id']]
    for role in ('base','current'):
        check_process(ROOT/('readiness-'+role))
        prior=ROOT.parent/'newsroom-natural-output-2'
        if inventory(ROOT/('readiness-'+role+'-capture'))!=inventory(prior/('readiness-'+role+'-capture')):raise ValueError('readiness copy drift')
    if final is not None:
        destination=ROOT/'final-report.json'
        if destination.exists() and destination.read_bytes()!=final:raise ValueError('derived final drift')
        if not destination.exists():destination.write_bytes(final)
    return {'schema':'caplab.claude-review-development-verification/v1',
        'plan_sha256':sha((ROOT/'plan.json').read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
        'returncode':completion['returncode'],'termination':completion['termination'],'elapsed_seconds':completion['elapsed_seconds'],
        'identity':identity,'session_observations':session_observations,'session_fields_agree':session_ok,
        'native_terminal_success':terminal_ok,'retained_files':len(retained),'unretained_entries':missing,
        'tool_pairs':pairs,'inspection':inspection,'report_errors':errors,
        'final_source':{'stdout_sha256':sha(raw),'line':results[0][0],'pointer':'/structured_output'} if terminal else None,
        'administration_verified':completion['returncode']==0 and completion['termination']=='exit' and not missing and terminal_ok and session_ok and identity['status']=='native-model-match' and inspection is not None,
        'ranking_eligible':False,'limits':['Native-reported model agreement is not provider attestation or full Binding verification.',
          'Effort max is explicitly configured; report observed effort separately if the native capture exposes it.',
          'Session agreement does not establish a complete conversation chain or kernel process trace.',
          'Finding truth is not assessed here; no paired comparison or ranking.']}


if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))
