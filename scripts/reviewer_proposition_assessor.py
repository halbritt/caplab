"""Bind the unchanged bounded native executor to the frozen v2 challenge."""
from pathlib import Path

import reviewer_evidence_assessor as executor
from reviewer_timeout_witness import write_new

ROOT = Path('/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/proposition-assessor-1')
REPO = Path(__file__).resolve().parents[1]


def main():
    executor.ROOT = ROOT
    executor.AUTH = REPO / 'docs/records/authorization-2026-09-10-reviewer-proposition-assessor.md'
    executor.PROMPT = (ROOT / 'prompt.txt').read_text()
    executor.FIXTURE_SHA = '59bc7f1bb471b02bb3fc882bd57c30afc814e76025b5a2ee14f6f27d08f863b3'
    executor.SUPPORT = [*executor.SUPPORT, executor.AUTH, Path(__file__),
        REPO / 'scripts/reviewer_proposition_fixture.py',
        REPO / 'scripts/reviewer_proposition_assessment.py',
        REPO / 'src/caplab/native_review_report.py', REPO / 'src/caplab/codex_events.py',
        REPO / 'docs/product/studies/reviewer-ranking-001/EVIDENCE-ASSESSMENT-V2.md',
        REPO / 'requirements-test.lock']
    write_new(ROOT / 'wrapper.py', Path(__file__).read_bytes())
    executor.main()


if __name__ == '__main__':
    main()
