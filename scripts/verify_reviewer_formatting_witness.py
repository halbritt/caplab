"""Keep formatter equivalence and actual original test outcomes separate."""
import json
from pathlib import Path
import re

from reviewer_formatting_witness import ROOT, COMMITS, TARGET, TESTS, verify_inputs
from reviewer_timeout_witness import sha
from verify_reviewer_scheduler_witness import check_process


def read(path):
    return json.loads(path.read_text())


def assess_format(base, change, base_formatted, change_formatted):
    return {'original_bytes_differ': base != change,
            'base_is_formatted': base == base_formatted,
            'change_is_formatted': change == change_formatted,
            'canonical_outputs_equal': base_formatted == change_formatted,
            'canonical_sha256': sha(change_formatted)}


def passed_tests(output, expected):
    rows = re.findall(r'^--- (PASS|FAIL|SKIP): (\S+) \(', output, flags=re.MULTILINE)
    if sorted(name for status, name in rows) != sorted(expected) or any(status != 'PASS' for status, name in rows) or not output.rstrip().endswith('PASS'):
        raise ValueError('exact original tests did not all run and pass')
    return [name for status, name in rows]


def verify():
    plan = read(ROOT / 'plan.json')
    plan_hash = sha((ROOT / 'plan.json').read_bytes())
    completion = read(ROOT / 'completion.json')
    if completion['failures'] or completion['plan_sha256'] != plan_hash or read(ROOT / 'run-started.json')['plan_sha256'] != plan_hash:
        raise ValueError('execution incomplete or detached from plan')
    verify_inputs(plan)
    if plan['changed_paths'] != [TARGET] or sha((ROOT / 'change.diff').read_bytes()) != plan['diff_sha256']:
        raise ValueError('change boundary drift')
    executions = []
    for role in COMMITS:
        check_process(ROOT / (role + '-format'))
        build = check_process(ROOT / (role + '-compile'))
        binary = ROOT / 'builds' / role / 'tests'
        if sha(binary.read_bytes()) != read(binary.parent / 'binary.json')['sha256']:
            raise ValueError('original test binary drift')
        for repetition in (1, 2):
            slot = ROOT / f'{role}-test-{repetition}'
            process = check_process(slot)
            passed = passed_tests((slot / 'stdout').read_text(), TESTS)
            executions.append({'role': role, 'repetition': repetition, 'tests_passed': passed,
                'binary_sha256': sha(binary.read_bytes()), 'elapsed_seconds': process['elapsed_seconds'],
                'stdout_sha256': process['stdout_sha256'], 'build_elapsed_seconds': build['elapsed_seconds']})
    formatting = assess_format((ROOT / 'base' / TARGET).read_bytes(), (ROOT / 'change' / TARGET).read_bytes(),
                               (ROOT / 'base-format/stdout').read_bytes(), (ROOT / 'change-format/stdout').read_bytes())
    return {'schema': 'caplab.formatting-witness-verification/v1', 'plan_sha256': plan_hash,
        'verifier_sha256': sha(Path(__file__).read_bytes()), 'formatting': formatting,
        'executions': executions, 'elapsed_seconds': completion['elapsed_seconds'],
        'named_properties_hold': formatting['canonical_outputs_equal'] and formatting['change_is_formatted'],
        'ranking_eligible': False, 'limits': [
            'Only the two affected original tests execute; the whole original package is compiled.',
            'The formatting comparison and test preservation do not independently validate the historical tests assumptions.',
            'Historical declaration assertions are not current model availability, capability or ranking evidence.',
            'One selected change is investigated; repetitions do not create independent cases.']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
