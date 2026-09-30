"""Validate retrieval specs and operate retained experiment evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class ArgumentError(ValueError):
    """An invalid command-line invocation."""


class Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:
        raise ArgumentError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(prog="python -m caplab.retrieval", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate and normalize a frozen spec")
    validate.add_argument("--spec", type=Path, required=True)
    run = commands.add_parser("run", help="execute the sealed roster into a new evidence directory")
    run.add_argument("--spec", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    report = commands.add_parser("report", help="verify retained evidence before reporting")
    report.add_argument("--run", type=Path, required=True)
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    compare = commands.add_parser("compare", help="compare verified paired runs or selected arms")
    compare.add_argument("--left", type=Path, required=True)
    compare.add_argument("--right", type=Path, required=True)
    compare.add_argument("--left-arm")
    compare.add_argument("--right-arm")
    task = commands.add_parser("import-task", help="retain a native task run without regrading or replay")
    task.add_argument("--report", type=Path, required=True)
    task.add_argument("--plan", type=Path, required=True)
    task.add_argument("--corpus", type=Path, required=True)
    task.add_argument("--cairn-checkout", type=Path, required=True)
    task.add_argument("--output", type=Path, required=True)
    task_report = commands.add_parser("report-task", help="verify retained native task evidence before reading it")
    task_report.add_argument("--run", type=Path, required=True)
    task_report.add_argument("--trusted-parser-checkout", type=Path,
                             help="replay delivery parsing with explicitly trusted, byte-matching Cairn source")
    return parser


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError("duplicate JSON object key")
        document[key] = value
    return document


def _nonfinite(_value: str) -> None:
    raise ValueError("nonfinite JSON number")


def read_spec(path: Path) -> dict[str, Any]:
    from .contracts import validate_spec

    document = json.loads(path.read_bytes(), object_pairs_hook=_object_pairs, parse_constant=_nonfinite)
    return validate_spec(document)


def emit(document: Any, *, stderr: bool = False) -> None:
    stream = sys.stderr if stderr else sys.stdout
    stream.write(json.dumps(document, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    stream.flush()


def incomplete(report: dict[str, Any]) -> bool:
    return not report["run"]["finished"] or report["run"]["status"] != "complete"


def execute(args: argparse.Namespace) -> int:
    if args.command == "validate":
        emit(read_spec(args.spec))
        return 0
    if args.command == "import-task":
        from .native_task import import_task_run

        emit(import_task_run(args.report, plan_path=args.plan, corpus_path=args.corpus,
                             cairn_checkout=args.cairn_checkout, output=args.output))
        return 0
    if args.command == "report-task":
        from .native_task import verify_task_run

        emit(verify_task_run(args.run, trusted_parser_checkout=args.trusted_parser_checkout)["evidence"])
        return 0
    if args.command == "run":
        from .runner import AdapterError, RunnerCleanupError, run_experiment

        try:
            report = run_experiment(read_spec(args.spec), args.output)["report"]
        except AdapterError as error:
            emit(error_document(error), stderr=True)
            return 2
        except RunnerCleanupError as error:
            emit({**error_document(error), "output": str(error.output), "failures": error.failures}, stderr=True)
            return 2
        emit(report)
        return 1 if incomplete(report) else 0
    if args.command == "report":
        from .artifacts import verify_run
        from .report import render_markdown

        report = verify_run(args.run, allow_unfinished=True)["report"]
        if args.format == "markdown":
            sys.stdout.write(render_markdown(report))
            sys.stdout.flush()
        else:
            emit(report)
        return 1 if incomplete(report) else 0
    if args.command == "compare":
        from .compare import compare_runs

        emit(compare_runs(args.left, args.right, left_arm=args.left_arm, right_arm=args.right_arm))
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def error_document(error: Exception) -> dict[str, Any]:
    if isinstance(error, ArgumentError):
        default_code = "argument_error"
    elif isinstance(error, OSError):
        default_code = "filesystem_error"
    else:
        default_code = "invalid_input"
    return {"schema_version": "caplab-retrieval-cli-error/1",
            "code": getattr(error, "code", default_code),
            "error_type": type(error).__name__, "message": str(error)[:4096],
            "path": getattr(error, "path", None)}


def main(argv: list[str] | None = None) -> int:
    try:
        return execute(build_parser().parse_args(argv))
    except (OSError, ValueError, UnicodeError) as error:
        emit(error_document(error), stderr=True)
        return 2
    except KeyboardInterrupt:
        emit({"schema_version": "caplab-retrieval-cli-error/1", "code": "interrupted"}, stderr=True)
        return 130
    except Exception as error:
        # Terminal classification preserves exit 1 for retained incomplete runs.
        document = error_document(error)
        document["code"] = "internal_error"
        emit(document, stderr=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
