"""Verify served and rendered properties without converting them to reviewer scores."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from reviewer_site_witness import ROOT,COMMITS,capture_inventory,verify_inputs
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):return json.loads(path.read_text())


def assess_view(role,view):
    name=view['nameplate'];rect=name['rect'];width=view['viewport'];mark=view['mark']
    checks={'nameplate_identity':''.join(name['text'].split())=='AINewsroom' and name['href']=='/',
        'nameplate_within_viewport':0<=rect['x']<rect['right']<=width and rect['width']>0 and rect['height']>0,
        'document_within_viewport':view['scrollWidth']<=width,
        'source_text_rendered_literally':view['scriptElements']==0 and '<script>fixture()</script> Local model release' in view['bodyText'] and '<img src=x onerror=fixture()>' in view['bodyText'],
        'icon_reference':view['icon']==('/icon.svg' if role=='icon' else None)}
    if role=='base':checks['mark_rendering']=mark is None
    else:
        checks['mark_rendering']=bool(mark and mark['text']=='AI' and mark['rect']['width']>0 and mark['rect']['height']>0
            and rect['x']<=mark['rect']['x']<mark['rect']['right']<=rect['right']
            and mark['style']['background']=='rgb(23, 106, 78)' and mark['style']['color']=='rgb(244, 244, 238)')
    return checks


def assess_http(row,role):
    path=row['path'];headers={k.lower():v for k,v in row['headers'].items()}
    expected=200 if path in ('/','/about/','/style.css','/feed.xml') else (200 if path=='/icon.svg' and role=='icon' else 404)
    if row['method']=='POST':expected=501
    mime=headers.get('content-type','').split(';')[0]
    return {'expected_status':row['status']==expected,
        'asset_mime':(path!='/icon.svg' or expected!=200 or mime=='image/svg+xml') and (path!='/style.css' or mime=='text/css'),
        'origin_headers':headers.get('x-content-type-options')=='nosniff' and headers.get('referrer-policy')=='no-referrer'
            and headers.get('cache-control')=='no-cache' and "default-src 'none'" in headers.get('content-security-policy','')}


def verify():
    plan=read(ROOT/'plan.json');plan_hash=sha((ROOT/'plan.json').read_bytes());completion=read(ROOT/'completion.json')
    if completion['failures'] or completion['plan_sha256']!=plan_hash or read(ROOT/'run-started.json')['plan_sha256']!=plan_hash:
        raise ValueError('incomplete execution or plan mismatch')
    verify_inputs(plan)
    observations,executions,meanings=[],[],{}
    expected_paths=['/','/about/','/style.css','/feed.xml','/icon.svg','/.env','/publication.db','/%2e%2e/publication.db','/leak.txt','/escape.svg','/drafts/','/']
    for repetition in (1,2):
        for role in COMMITS:
            name=f'{role}-{repetition}';check_process(ROOT/name);capture=ROOT/(name+'-capture')
            entries=capture_inventory(capture)
            if entries!=read(ROOT/(name+'-inventory.json')):raise ValueError('capture drift')
            row=read(capture/'observation.json');browser=read(capture/'browser.json')
            if row['role']!=role or browser['browser']!=plan['expected_browser']:raise ValueError('subject or browser mismatch')
            if [v['viewport'] for v in browser['views']]!=[320,768,1280]:raise ValueError('viewport observations incomplete')
            if [r['path'] for r in row['responses']]!=expected_paths or [r['method'] for r in row['responses']]!=['GET']*11+['POST']:
                raise ValueError('HTTP observations incomplete')
            for i,response in enumerate(row['responses'],1):
                body=(capture/f'response-{i}.body').read_bytes()
                if sha(body)!=response['body_sha256'] or len(body)!=response['body_bytes']:raise ValueError('response detached from body')
            if (capture/'response-3.body').read_bytes()!=(ROOT/role/'newsroom/static/style.css').read_bytes():raise ValueError('served CSS differs from source asset')
            if role=='icon' and (capture/'response-5.body').read_bytes()!=(ROOT/role/'newsroom/static/icon.svg').read_bytes():raise ValueError('served icon differs from source asset')
            feed=ET.fromstring((capture/'response-4.body').read_bytes())
            icon=browser['icon']
            properties={'viewports':{str(v['viewport']):assess_view(role,v) for v in browser['views']},
                'http':[assess_http(r,role) for r in row['responses']],
                'database_unchanged':row['database_before']==row['database_after']==sha((capture/'publication.db').read_bytes()),
                'source_story_retained':len(row['stories'])==1 and row['stories'][0]['title']=='<script>fixture()</script> Local model release',
                'feed_preserves_title':feed.findtext('channel/item/title')=='<script>fixture()</script> Local model release',
                'browser_errors_absent':not browser['errors'],
                'browser_requests_local':all(url.startswith('http://127.0.0.1:3913/') for url in browser['requests']),
                'icon_render':bool(icon and icon['status']==200 and icon['root']=='svg' and icon['text']=='AI' and icon['contentType'].split(';')[0]=='image/svg+xml') if role=='icon' else icon is None,
                'ignore_rule':row['ignore_check']['paths']==(['.playwright-mcp/probe.txt'] if role=='icon' else [])}
            values=[value for key,value in properties.items() if isinstance(value,bool)]
            values += [value for checks in properties['viewports'].values() for value in checks.values()]
            values += [value for checks in properties['http'] for value in checks.values()]
            outcome={'role':role,'properties':properties,'all_named_properties_hold':all(values)}
            if role in meanings and outcome!=meanings[role]:raise ValueError('semantic repetitions disagree')
            meanings[role]=outcome;observations.append({'repetition':repetition,**outcome})
            executions.append({'slot':name,'capture_files':sum('sha256' in e for e in entries),'capture_links':sum('symlink' in e for e in entries),
                               'inventory_sha256':sha((ROOT/(name+'-inventory.json')).read_bytes())})
    return {'schema':'caplab.site-witness-verification/v1','plan_sha256':plan_hash,'verifier_sha256':sha(Path(__file__).read_bytes()),
        'observations':observations,'executions':executions,'elapsed_seconds':completion['elapsed_seconds'],
        'all_named_properties_hold':all(o['all_named_properties_hold'] for o in observations),
        'ranking_eligible':False,'limits':plan['limits']}


if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))
