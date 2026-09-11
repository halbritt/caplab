"""Verify native assessment capture and compare frozen development expectations."""
import json
from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parent)]
from caplab.codex_events import parse_native_json
from reviewer_evidence_assessment import compare_assessments
from reviewer_outcome_assessment import verify_capture
from reviewer_scheduler_witness import inventory
from reviewer_reddit_recovery_witness import runtime
from reviewer_timeout_witness import sha

ROOT=Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/evidence-assessor-1')


def read(path):return parse_native_json(path.read_text())


def verify():
    fixture,plan,launch,completion=[read(ROOT/name) for name in ('fixture-plan.json','plan.json','launch.json','completion.json')]
    if (sha((ROOT/'fixture-plan.json').read_bytes())!=plan['fixture_plan_sha256'] or
        sha((ROOT/'plan.json').read_bytes())!=launch['plan_sha256'] or
        sha((ROOT/'runner.py').read_bytes())!=plan['runner_sha256']):raise ValueError('administration drift')
    if completion['returncode']!=0 or completion['termination']!='exit':raise ValueError('native attempt did not finish')
    if inventory(ROOT/'task')!=fixture['task'] or runtime()!=plan['runtime']:raise ValueError('input/runtime drift')
    if sha((ROOT/'expected.json').read_bytes())!=fixture['expected_sha256'] or sha((ROOT/'prompt.txt').read_bytes())!=fixture['prompt_sha256']:raise ValueError('expectation/prompt drift')
    for e in plan['support']:
        if sha(Path(e['path']).read_bytes())!=e['sha256']:raise ValueError('support drift')
    vendor=Path(plan['binary']).parent.parent
    for e in plan['package_files']:
        if sha((vendor/e['path']).read_bytes())!=e['sha256']:raise ValueError('native package drift')
    verify_capture(ROOT,plan,completion)
    if {e['path'] for e in inventory(ROOT/'capture')}!={e['path'] for e in completion['entries']}:raise ValueError('capture membership mismatch')
    rollouts=list((ROOT/'capture').glob('codex/sessions/*/*/*/rollout-*.jsonl'))
    if len(rollouts)!=1:raise ValueError('native session count mismatch')
    rows=[parse_native_json(line) for line in rollouts[0].read_text().splitlines()]
    metas=[r['payload'] for r in rows if r['type']=='session_meta'];contexts=[r['payload'] for r in rows if r['type']=='turn_context']
    if len(metas)!=1 or metas[0]['cli_version']!='0.153.4':raise ValueError('native harness mismatch')
    if not contexts or any(r['model']!='gpt-5.6-terra' or r['effort']!='max' for r in contexts):raise ValueError('native model/effort mismatch')
    stream=[parse_native_json(line) for line in (ROOT/'capture/stdout').read_text().splitlines()]
    if [r['thread_id'] for r in stream if r['type']=='thread.started']!=[metas[0]['id']] or stream[-1]['type']!='turn.completed':raise ValueError('native stream/session mismatch')
    messages=[r['item']['text'] for r in stream if r['type']=='item.completed' and r['item']['type']=='agent_message']
    raw=(ROOT/'capture/final-message.txt').read_bytes()
    if not messages or messages[-1].encode()!=raw:raise ValueError('final detached from native stream')
    comparison=compare_assessments(read(ROOT/'task/reviews.json'),read(ROOT/'expected.json'),parse_native_json(raw.decode()),ROOT/'task')
    commands=[r['item']['command'] for r in stream if r['type']=='item.completed' and r['item']['type']=='command_execution']
    projections=[read(ROOT/e['projection_receipt']) for e in completion['entries'] if e['disposition']=='projected-retained']
    return {'schema':'caplab.evidence-assessor-development-verification/v1','fixture_plan_sha256':sha((ROOT/'fixture-plan.json').read_bytes()),
        'plan_sha256':sha((ROOT/'plan.json').read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),
        'comparison':comparison,'native':{'thread_id':metas[0]['id'],'observed_harness_version':'0.153.4','observed_model':'gpt-5.6-terra','observed_effort':'max',
            'elapsed_seconds':completion['elapsed_seconds'],'captured_files':len(completion['entries']),'opaque_fields_omitted':sum(len(r['omissions']) for r in projections),
            'final_sha256':sha(raw),'recorded_commands':commands,'usage':stream[-1].get('usage')},
        'semantic_support_verified':False,'scorer_accepted':False,'ranking_eligible':False,
        'limits':['Blinded to explicit author and expected labels, not guaranteed stylistic anonymity.','Native capture verifies reported model/configuration, not independent provider attestation.',
                  'Literal citations and expected labels cannot establish semantic support by themselves.','Authored variants and one exposed source change do not establish general scorer validity.']}


if __name__=='__main__':print(json.dumps(verify(),sort_keys=True,indent=2))
