"""Verify native report administration and preserve units without scoring them."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from caplab.native_review_report import inspect_report
from verify_reviewer_natural_output import verify as verify_native, sha

ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/finding-units-review-1')


def verify():
    native = verify_native(ROOT)
    plan = json.loads((ROOT / 'plan.json').read_text())
    command = plan['actual_command']
    if command.count('--output-schema') != 1 or command[command.index('--output-schema') + 1] != '/task/review-report.schema.json':
        raise ValueError('native report schema was not administered as planned')
    schema = json.loads((ROOT / 'task/review-report.schema.json').read_text())
    if schema['properties']['schema']['enum'] != ['caplab.native-code-review-report/v1']:
        raise ValueError('unexpected native report version')
    inspection = inspect_report((ROOT / 'capture/final-message.txt').read_bytes(), ROOT / 'task/current')
    if inspection['raw_report_sha256'] != native['final_sha256']:
        raise ValueError('finding units detached from native final output')
    return {'schema': 'caplab.finding-units-development-verification/v1', 'native': native,
        'inspection': inspection, 'report_schema_sha256': sha(ROOT / 'task/review-report.schema.json'),
        'inspector_sha256': sha(Path(__file__).resolve().parents[1] / 'src/caplab/native_review_report.py'),
        'verifier_sha256': sha(Path(__file__)), 'ranking_eligible': False,
        'limits': ['This checks authentic report representation and source locators, not whether findings are correct.',
                   'Explicit acceptance effects are reviewer judgments, not independent acceptance decisions.',
                   'This repeats an exposed development task with a changed report administration; no paired performance inference.']}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
