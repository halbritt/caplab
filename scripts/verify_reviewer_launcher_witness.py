"""Assess original launcher dispatch observations against the frozen contract."""
import json
from pathlib import Path

from reviewer_launcher_witness import ROOT, CONDITIONS, verify_inputs
from reviewer_scheduler_witness import inventory
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def assess(condition, item, returncode, dispatch, output_exists):
    if not item['dispatch_expected']:
        checks = {'invalid_input_stops_before_dispatch': returncode != 0 and dispatch is None and not output_exists}
    else:
        prefix = item['prefix']
        arguments = item['arguments']
        expected = ['-u', prefix + '/scripts/supervise_sweep.py', arguments[0],
                    prefix + '/advisory/pool-runs/tree-' + arguments[0] + '-20260819', *arguments[1:]]
        data = dispatch or {}
        environment = data.get('environment', {})
        checks = {
            'recorder_only': data.get('recorder') is True and data.get('supervisor_executed') is False,
            'arguments_preserved': data.get('argv') == expected,
            'environment_exported': environment.get('ZAI_API_KEY') == item['zai'] and environment.get('OPENROUTER_API_KEY') == item['openrouter'],
            'source_pythonpath': environment.get('PYTHONPATH') == prefix + '/src',
            'tool_path_precedence': data.get('selected_executable') == '/witness/' + condition + '/home/.npm-global/bin/python3'
                and environment.get('PATH') == '/witness/' + condition + '/home/.npm-global/bin:/witness/' + condition + '/fallback-bin:/usr/bin:/bin',
            'output_directory_created': output_exists and data.get('output_exists') is True,
            'exit_status_preserved': returncode == item['downstream_exit'],
        }
    return {'condition': condition, 'returncode': returncode, 'dispatch_observed': dispatch is not None,
            'checks': checks, 'all_named_properties_hold': all(checks.values())}


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    completion = read(ROOT / 'completion.json')
    if completion['failures'] or completion['plan_sha256'] != plan_hash or read(ROOT / 'run-started.json')['plan_sha256'] != plan_hash:
        raise ValueError('execution incomplete or plan mismatch')
    verify_inputs(plan)
    criteria = read(ROOT / 'witness/criteria.json')
    observations, executions, meanings = [], [], {}
    for repetition in (1, 2):
        for condition in CONDITIONS:
            name = f'{condition}-{repetition}'
            process = check_process(ROOT / name)
            capture = ROOT / (name + '-capture')
            entries = inventory(capture)
            if entries != read(ROOT / (name + '-inventory.json')):
                raise ValueError('capture drift')
            row = read(capture / 'observation.json')
            item = criteria[condition]
            expected_command = [item['prefix'] + '/scripts/launch_tree_v1_sweep.sh', *item['arguments']]
            if row['command'] != expected_command:
                raise ValueError('unexpected executed launcher or arguments')
            for stream in ('stdout', 'stderr'):
                if sha((capture / ('launcher.' + stream)).read_bytes()) != row[stream + '_sha256']:
                    raise ValueError('launcher process capture mismatch')
            dispatch = read(capture / 'dispatch.json') if (capture / 'dispatch.json').exists() else None
            output = capture / 'output/pool-runs/tree-fixture-backend-20260819'
            outcome = assess(condition, item, row['returncode'], dispatch, output.is_dir())
            if condition in meanings and outcome != meanings[condition]:
                raise ValueError('repetitions disagree')
            meanings[condition] = outcome
            observations.append({'repetition': repetition, **outcome})
            executions.append({'slot': name, 'captured_files': len(entries), 'elapsed_seconds': process['elapsed_seconds'],
                               'inventory_sha256': sha((ROOT / (name + '-inventory.json')).read_bytes())})
    return {'schema': 'caplab.launcher-witness-verification/v1', 'plan_sha256': plan_hash,
        'verifier_sha256': sha(Path(__file__).read_bytes()), 'observations': observations, 'executions': executions,
        'all_named_properties_hold': all(row['all_named_properties_hold'] for row in observations),
        'semantic_repetitions_match': True, 'elapsed_seconds': completion['elapsed_seconds'],
        'ranking_eligible': False, 'limits': [
            'The recorder checks dispatch only; the original supervisor and native models were not executed.',
            'Named launch properties are bounded clean-control evidence, not proof that the whole change is defect-free.',
            'Sixteen executions cover one independently selected change, not sixteen independent cases.',
            'Historical source and requirement import creates no current authority or evidence admission.']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
