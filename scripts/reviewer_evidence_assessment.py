"""Check bounded assessor output without promoting labels or citations to truth."""
from pathlib import Path

from caplab.native_review_report import _location

ASSESSMENTS={'confirmed_introduced_defect','refuted_claim','unresolved','mixed','no_defect_claim'}
FIELDS={'document_id','finding_id','reported_claim_status','acceptance_effect','defect_assessment','duplicate_of','reason','evidence'}


def compare_assessments(inputs,expected,output,task_root):
    if not isinstance(output,dict) or set(output)!={'entries'} or not isinstance(output['entries'],list):raise ValueError('entries required')
    originals={(d['document_id'],f['finding_id']):f['reported'] for d in inputs['documents'] for f in d['findings']}
    targets={(r['document_id'],r['finding_id']):r for r in expected['entries']}
    if set(originals)!=set(targets):raise ValueError('expected case coverage mismatch')
    seen=set();observations=[]
    for row in output['entries']:
        if not isinstance(row,dict) or set(row)!=FIELDS:raise ValueError('unexpected assessor fields')
        key=(row['document_id'],row['finding_id'])
        if key not in originals or key in seen:raise ValueError('unknown or duplicate finding')
        seen.add(key);source=originals[key];target=targets[key]
        if row['defect_assessment'] not in ASSESSMENTS:raise ValueError('invalid assessment')
        if row['reported_claim_status'] not in ('asserted','uncertain','withdrawn') or row['acceptance_effect'] not in ('block','advise','undetermined'):raise ValueError('invalid reported judgment')
        duplicate=row['duplicate_of']
        if duplicate is not None and ((key[0],duplicate) not in originals or duplicate==key[1]):raise ValueError('invalid duplicate reference')
        if not isinstance(row['reason'],str) or not row['reason'].strip() or not isinstance(row['evidence'],list):raise ValueError('explanation and evidence required')
        citations=[]
        for e in row['evidence']:
            if not isinstance(e,dict) or set(e)!={'path','start_line','end_line','support'}:raise ValueError('invalid citation shape')
            if not isinstance(e['path'],str) or type(e['start_line']) is not int or type(e['end_line']) is not int or not isinstance(e['support'],str) or not e['support'].strip():raise ValueError('invalid citation fields')
            location=_location(e,Path(task_root).resolve())
            citations.append({**e,'location':location})
        checks={'assessment_matches':row['defect_assessment']==target['defect_assessment'],
            'reported_stance_preserved':row['reported_claim_status']==source['claim_status'],
            'reported_effect_preserved':row['acceptance_effect']==source['acceptance_effect'],
            'duplicate_matches':duplicate==target['duplicate_of'],
            'citation_locations_resolve':all(e['location']['status']=='resolved' for e in citations),
            'required_evidence_paths_present':all(any(any(e['path'].startswith(prefix) for prefix in group) for e in row['evidence']) for group in target['required_evidence_groups'])}
        observations.append({'document_id':key[0],'finding_id':key[1],'expected_assessment':target['defect_assessment'],'reported_assessment':row['defect_assessment'],'checks':checks,'citations':citations,'reason':row['reason']})
    if seen!=set(originals):raise ValueError('missing findings')
    return {'schema':'caplab.evidence-assessor-comparison/v1','observations':observations,
        'all_structural_and_label_checks_match':all(all(r['checks'].values()) for r in observations),
        'semantic_support_verified':False,'scorer_accepted':False,'ranking_eligible':False,
        'limits':['Correct labels, literal locators and required evidence paths do not prove semantic support.',
                  'Reported stance/effect are separate from empirical truth; no reviewer score is computed.',
                  'This is an exposed development challenge, not general scorer validation.']}
