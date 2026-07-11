#!/usr/bin/env python3
"""Build and validate the deterministic pending-human gold calibration queue."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import yaml


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
GOLD_RELATIVE = Path("doctrine/evaluations/gold")
QUEUE_SCHEMA = "queue.schema.json"
DISPOSITIONS_SCHEMA = "human-dispositions.schema.json"
INPUT_PATHS = (
    Path("doctrine/sources.yaml"),
    Path("doctrine/graph/edges.yaml"),
    Path("doctrine/graph/formulations.yaml"),
    Path("doctrine/authority-model.yaml"),
    Path("doctrine/context-lenses.yaml"),
)
OUTCOMES = ("abstention", "insufficient-evidence", "no-change")
AXES = (
    "source_ids",
    "edge_relations",
    "support_relationships",
    "agent_roles",
    "risk_classes",
    "authority_transitions",
    "outcomes",
)


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with open(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def load_json_mapping(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def schema_validator(path: Path) -> Draft202012Validator:
    schema = load_json_mapping(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_instance(
    value: object, validator: Draft202012Validator, label: str
) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    raise ValueError(f"{label} is invalid at {location}: {error.message}")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def empty_coverage() -> dict[str, list[str]]:
    return {axis: [] for axis in AXES}


def reference(kind: str, identifier: str) -> dict[str, str]:
    return {"kind": kind, "id": identifier}


def candidate_record(
    *,
    identifier: str,
    kind: str,
    question: str,
    target_kind: str,
    target_id: str,
    references: list[dict[str, str]],
    coverage: dict[str, list[str]],
    disposition_ids: set[str],
) -> dict[str, object]:
    if identifier in disposition_ids:
        human_disposition: dict[str, object] = {
            "status": "adjudicated-human",
            "reference": f"human-dispositions.json#candidate_id={identifier}",
        }
    else:
        human_disposition = {"status": "pending-human", "reference": None}
    return {
        "schema_version": "doctrine-gold-candidate/1",
        "id": identifier,
        "candidate": {
            "generated_only": True,
            "kind": kind,
            "adjudication_mode": (
                "direct-evidence-review"
                if kind in {"source-support", "edge-relation", "support-relationship"}
                else "scenario-construction-and-review"
            ),
            "question": question,
            "target": {
                "kind": target_kind,
                "id": target_id,
                "references": references,
            },
            "coverage": {axis: sorted(set(coverage.get(axis, []))) for axis in AXES},
        },
        "machine_screening": {"status": "not-run", "references": []},
        "human_disposition": human_disposition,
    }


def required_axes(inputs: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    sources = inputs["sources"]["sources"]
    edges = inputs["edges"]["edges"]
    formulations = inputs["formulations"]["formulations"]
    authority = inputs["authority"]
    lenses = inputs["lenses"]["lenses"]
    return {
        "source_ids": sorted(str(source["id"]) for source in sources),
        "edge_relations": sorted({str(edge["relation"]) for edge in edges}),
        "support_relationships": sorted(
            {
                str(mapping["relationship_to_canonical"])
                for formulation in formulations
                for mapping in formulation["mappings"]
            }
        ),
        "agent_roles": sorted(str(role) for role in authority["role_defaults"]),
        "risk_classes": sorted(
            {
                str(risk)
                for lens in lenses
                for risk in lens.get("routing", {}).get("risk_classes", [])
            }
        ),
        "authority_transitions": sorted(
            f"{transition['from']}->{transition['to']}"
            for transition in authority["transitions"]
        ),
        "outcomes": sorted(OUTCOMES),
    }


def build_source_records(
    sources: list[dict[str, Any]],
    formulations_by_source: dict[str, list[dict[str, Any]]],
    disposition_ids: set[str],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for source in sources:
        source_id = str(source["id"])
        formulations = formulations_by_source.get(source_id, [])
        if not formulations:
            raise ValueError(f"source {source_id} has no graph formulation")
        formulation = formulations[0]
        mapping = sorted(formulation["mappings"], key=lambda item: item["node_id"])[0]
        coverage = empty_coverage()
        coverage["source_ids"] = [source_id]
        coverage["support_relationships"] = [str(mapping["relationship_to_canonical"])]
        records.append(
            candidate_record(
                identifier=f"gold-source-{slug(source_id)}",
                kind="source-support",
                question=(
                    f"Does formulation {formulation['id']} support its mapping to "
                    f"{mapping['node_id']} under the recorded conditions and caveats?"
                ),
                target_kind="formulation",
                target_id=str(formulation["id"]),
                references=[
                    reference("source", source_id),
                    reference("formulation", str(formulation["id"])),
                    reference("node", str(mapping["node_id"])),
                ],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )
    return records


def build_records(
    inputs: dict[str, dict[str, Any]], disposition_ids: set[str]
) -> list[dict[str, object]]:
    sources = sorted(inputs["sources"]["sources"], key=lambda item: item["id"])
    edges = sorted(inputs["edges"]["edges"], key=lambda item: item["id"])
    formulations = sorted(
        inputs["formulations"]["formulations"], key=lambda item: item["id"]
    )
    authority = inputs["authority"]
    axes = required_axes(inputs)
    formulations_by_source: dict[str, list[dict[str, Any]]] = {}
    formulation_sources: dict[str, str] = {}
    for formulation in formulations:
        source_id = str(formulation["source_id"])
        formulations_by_source.setdefault(source_id, []).append(formulation)
        formulation_sources[str(formulation["id"])] = source_id

    records = build_source_records(sources, formulations_by_source, disposition_ids)

    for relation in axes["edge_relations"]:
        edge = next(edge for edge in edges if edge["relation"] == relation)
        coverage = empty_coverage()
        coverage["edge_relations"] = [relation]
        provenance = edge.get("provenance", [])
        coverage["source_ids"] = sorted(
            {
                formulation_sources[item]
                for item in provenance
                if item in formulation_sources
            }
        )
        references = [
            reference("edge", str(edge["id"])),
            reference("node", str(edge["from"])),
            reference("node", str(edge["to"])),
        ]
        references.extend(
            reference("source", source_id) for source_id in coverage["source_ids"]
        )
        records.append(
            candidate_record(
                identifier=f"gold-edge-relation-{slug(relation)}",
                kind="edge-relation",
                question=(
                    f"Do the edge claim, conditions, derivation, and provenance justify "
                    f"the {relation} relationship from {edge['from']} to {edge['to']}?"
                ),
                target_kind="edge",
                target_id=str(edge["id"]),
                references=references,
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    for relationship in axes["support_relationships"]:
        formulation, mapping = next(
            (formulation, mapping)
            for formulation in formulations
            for mapping in formulation["mappings"]
            if mapping["relationship_to_canonical"] == relationship
        )
        source_id = str(formulation["source_id"])
        target_id = f"{formulation['id']}--{mapping['node_id']}"
        coverage = empty_coverage()
        coverage["source_ids"] = [source_id]
        coverage["support_relationships"] = [relationship]
        records.append(
            candidate_record(
                identifier=f"gold-support-relationship-{slug(relationship)}",
                kind="support-relationship",
                question=(
                    f"Is {relationship} the correct provenance relationship between "
                    f"formulation {formulation['id']} and node {mapping['node_id']}?"
                ),
                target_kind="mapping",
                target_id=target_id,
                references=[
                    reference("source", source_id),
                    reference("formulation", str(formulation["id"])),
                    reference("node", str(mapping["node_id"])),
                ],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    for role in axes["agent_roles"]:
        default = authority["role_defaults"][role]
        coverage = empty_coverage()
        coverage["agent_roles"] = [role]
        records.append(
            candidate_record(
                identifier=f"gold-agent-role-{slug(role)}",
                kind="agent-role",
                question=(
                    f"Construct and adjudicate a scenario in which {role} must remain "
                    f"at or below its usual {default['usual_ceiling']} authority ceiling "
                    "while preserving the role-specific constraints."
                ),
                target_kind="role",
                target_id=role,
                references=[reference("role", role)],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    lenses = inputs["lenses"]["lenses"]
    for risk_class in axes["risk_classes"]:
        lens = next(
            lens
            for lens in lenses
            if risk_class in lens.get("routing", {}).get("risk_classes", [])
        )
        coverage = empty_coverage()
        coverage["risk_classes"] = [risk_class]
        records.append(
            candidate_record(
                identifier=f"gold-risk-class-{slug(risk_class)}",
                kind="risk-class",
                question=(
                    f"Construct and adjudicate a scenario where retrieval, evidence "
                    f"threshold, action scope, and verification must respond "
                    f"proportionally to {risk_class} risk."
                ),
                target_kind="risk-class",
                target_id=risk_class,
                references=[
                    reference("risk-class", risk_class),
                    reference("lens", str(lens["id"])),
                ],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    for transition_id in axes["authority_transitions"]:
        coverage = empty_coverage()
        coverage["authority_transitions"] = [transition_id]
        records.append(
            candidate_record(
                identifier=f"gold-authority-transition-{slug(transition_id)}",
                kind="authority-transition",
                question=(
                    f"Construct and adjudicate a scenario that tests every evidence and "
                    f"authority requirement for transition {transition_id}, including "
                    "any agent-default prohibition."
                ),
                target_kind="authority-transition",
                target_id=transition_id,
                references=[reference("authority-transition", transition_id)],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    outcome_questions = {
        "insufficient-evidence": (
            "Construct and adjudicate a scenario where supplied evidence fails the "
            "applicable proof obligation and should produce an explicit "
            "insufficient-evidence disposition rather than a recommendation."
        ),
        "abstention": (
            "Construct and adjudicate a scenario where unresolved evidence or authority "
            "gaps require abstention from selection or execution while preserving "
            "established observations."
        ),
        "no-change": (
            "Construct and adjudicate a scenario where evidence favors leaving the target "
            "unchanged, with a bounded rationale and a concrete revisit trigger."
        ),
    }
    outcome_nodes = {
        "insufficient-evidence": "universal-evidence-before-intervention",
        "abstention": "agent-conduct-authority-bounded-action",
        "no-change": "universal-no-change-option",
    }
    for outcome in axes["outcomes"]:
        coverage = empty_coverage()
        coverage["outcomes"] = [outcome]
        records.append(
            candidate_record(
                identifier=f"gold-outcome-{slug(outcome)}",
                kind="outcome",
                question=outcome_questions[outcome],
                target_kind="outcome",
                target_id=outcome,
                references=[
                    reference("outcome", outcome),
                    reference("node", outcome_nodes[outcome]),
                ],
                coverage=coverage,
                disposition_ids=disposition_ids,
            )
        )

    records.sort(key=lambda record: str(record["id"]))
    identifiers = [str(record["id"]) for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("generated gold candidate IDs are not unique")
    return records


def load_inputs(root: Path) -> dict[str, dict[str, Any]]:
    paths = {path.name: root / path for path in INPUT_PATHS}
    return {
        "sources": load_yaml_mapping(paths["sources.yaml"]),
        "edges": load_yaml_mapping(paths["edges.yaml"]),
        "formulations": load_yaml_mapping(paths["formulations.yaml"]),
        "authority": load_yaml_mapping(paths["authority-model.yaml"]),
        "lenses": load_yaml_mapping(paths["context-lenses.yaml"]),
    }


def validate_dispositions(
    document: dict[str, Any],
    validator: Draft202012Validator,
) -> set[str]:
    raw_dispositions = document.get("dispositions")
    if isinstance(raw_dispositions, list):
        for disposition in raw_dispositions:
            if not isinstance(disposition, dict):
                continue
            adjudicator = disposition.get("adjudicator")
            if not isinstance(adjudicator, dict) or adjudicator.get("kind") != "human":
                candidate_id = disposition.get("candidate_id", "<unknown>")
                raise ValueError(
                    f"human disposition {candidate_id} requires adjudicator.kind=human; "
                    "machine output is screening evidence, not human adjudication"
                )
    validate_instance(document, validator, "human-dispositions.json")
    identifiers = [
        str(disposition["candidate_id"]) for disposition in document["dispositions"]
    ]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("human-dispositions.json repeats a candidate_id")
    return set(identifiers)


def build_coverage(
    records: list[dict[str, object]],
    required: dict[str, list[str]],
) -> dict[str, object]:
    covered = {axis: set() for axis in AXES}
    kinds: Counter[str] = Counter()
    pending = 0
    adjudicated = 0
    machine_screenings = 0
    for record in records:
        candidate = record["candidate"]
        if not isinstance(candidate, dict):
            raise ValueError(f"candidate {record['id']} is malformed")
        kinds[str(candidate["kind"])] += 1
        record_coverage = candidate["coverage"]
        if not isinstance(record_coverage, dict):
            raise ValueError(f"candidate {record['id']} coverage is malformed")
        for axis in AXES:
            covered[axis].update(record_coverage[axis])
        disposition = record["human_disposition"]
        if not isinstance(disposition, dict):
            raise ValueError(f"candidate {record['id']} disposition is malformed")
        if disposition["status"] == "pending-human":
            pending += 1
        else:
            adjudicated += 1
        screening = record["machine_screening"]
        if isinstance(screening, dict) and screening["status"] == "recorded":
            machine_screenings += 1
    covered_lists = {axis: sorted(values) for axis, values in covered.items()}
    missing = {axis: sorted(set(required[axis]) - covered[axis]) for axis in AXES}
    if adjudicated == 0:
        status = "pending-human-adjudication"
    elif pending == 0:
        status = "human-adjudication-complete"
    else:
        status = "human-adjudication-partial"
    return {
        "schema_version": "doctrine-gold-coverage/1",
        "status": status,
        "candidate_count": len(records),
        "candidate_kind_counts": dict(sorted(kinds.items())),
        "required": required,
        "covered": covered_lists,
        "missing": missing,
        "pending_human_count": pending,
        "adjudicated_human_count": adjudicated,
        "machine_screening_count": machine_screenings,
    }


def input_fingerprints(root: Path, dispositions_path: Path) -> dict[str, str]:
    paths = [root / relative for relative in INPUT_PATHS]
    paths.append(dispositions_path)
    return {path.relative_to(root).as_posix(): sha256_file(path) for path in paths}


def expected_documents(
    root: Path,
    inputs: dict[str, dict[str, Any]],
    disposition_ids: set[str],
    dispositions_path: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    records = build_records(inputs, disposition_ids)
    known_ids = {str(record["id"]) for record in records}
    unknown_dispositions = sorted(disposition_ids - known_ids)
    if unknown_dispositions:
        raise ValueError(
            "human-dispositions.json references unknown candidates: "
            + ", ".join(unknown_dispositions)
        )
    queue = {
        "schema_version": "doctrine-gold-queue/1",
        "generation": {
            "tool": "doctrine/tools/build_gold_queue.py",
            "tool_sha256": sha256_file(Path(__file__).resolve()),
            "algorithm_version": "gold-queue-stratification/1",
            "input_sha256": input_fingerprints(root, dispositions_path),
        },
        "records": records,
    }
    coverage = build_coverage(records, required_axes(inputs))
    return queue, coverage


def check_static_files(gold: Path) -> tuple[Draft202012Validator, Draft202012Validator]:
    readme = gold / "README.md"
    if not readme.is_file():
        raise ValueError(f"{readme} is missing")
    queue_schema = gold / QUEUE_SCHEMA
    dispositions_schema = gold / DISPOSITIONS_SCHEMA
    if not queue_schema.is_file() or not dispositions_schema.is_file():
        raise ValueError("gold queue schema files are missing")
    return schema_validator(queue_schema), schema_validator(dispositions_schema)


def run(root: Path, *, write: bool) -> None:
    gold = root / GOLD_RELATIVE
    if write:
        gold.mkdir(parents=True, exist_ok=True)
    elif not gold.is_dir():
        raise ValueError(f"{gold} is missing")
    queue_validator, dispositions_validator = check_static_files(gold)
    dispositions_path = gold / "human-dispositions.json"
    if not dispositions_path.is_file():
        if not write:
            raise ValueError("human-dispositions.json is missing")
        atomic_write(
            dispositions_path,
            json_bytes(
                {
                    "schema_version": "doctrine-gold-human-dispositions/1",
                    "dispositions": [],
                }
            ),
        )
    dispositions = load_json_mapping(dispositions_path)
    disposition_ids = validate_dispositions(dispositions, dispositions_validator)
    inputs = load_inputs(root)
    queue, coverage = expected_documents(
        root, inputs, disposition_ids, dispositions_path
    )
    validate_instance(queue, queue_validator, "generated queue")
    queue_path = gold / "queue.json"
    coverage_path = gold / "coverage.json"
    expected_queue = json_bytes(queue)
    expected_coverage = json_bytes(coverage)
    if write:
        if not queue_path.is_file() or queue_path.read_bytes() != expected_queue:
            atomic_write(queue_path, expected_queue)
        if (
            not coverage_path.is_file()
            or coverage_path.read_bytes() != expected_coverage
        ):
            atomic_write(coverage_path, expected_coverage)
        print(
            f"gold queue: wrote {len(queue['records'])} candidate(s); "
            f"{coverage['pending_human_count']} pending human adjudication"
        )
        return
    if not queue_path.is_file():
        raise ValueError("queue.json is missing or stale")
    actual_queue = load_json_mapping(queue_path)
    validate_instance(actual_queue, queue_validator, "queue.json")
    if queue_path.read_bytes() != expected_queue:
        raise ValueError("queue.json is stale; run build_gold_queue.py --write")
    if not coverage_path.is_file() or coverage_path.read_bytes() != expected_coverage:
        raise ValueError("coverage.json is stale; run build_gold_queue.py --write")
    print(
        f"gold queue: current ({len(queue['records'])} candidate(s); "
        f"{coverage['pending_human_count']} pending human adjudication)"
    )


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--write", action="store_true", help="write generated queue files"
    )
    modes.add_argument(
        "--check", action="store_true", help="check generated queue drift"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv or sys.argv[1:])
    try:
        run(arguments.root.resolve(), write=arguments.write)
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as error:
        print(f"gold queue: error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
