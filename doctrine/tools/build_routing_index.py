#!/usr/bin/env python3
"""Build the selective-retrieval index from doctrine routing metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def dump(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=1000)


def concept_inventory() -> tuple[list[dict[str, Any]], dict[str, str]]:
    concepts: list[dict[str, Any]] = []
    artifacts: dict[str, str] = {}
    for path in sorted((ROOT / "concepts").glob("*.yaml")):
        for concept in load(path).get("concepts", []):
            concepts.append(concept)
            artifacts[concept["id"]] = str(path.relative_to(ROOT))
    return concepts, artifacts


ALIASES = {
    "coding-agent": {"implementation-agent"},
    "architecture-agent": {"architectural-agent", "domain-design-agent"},
    "legacy-code-agent": {"legacy-agent"},
    "debugging-and-repair-agent": {"repair-agent", "debugging-agent"},
}


def role_matches(expected: str, actual: list[str]) -> bool:
    return expected in actual or bool(ALIASES.get(expected, set()) & set(actual))


ROLE_PROCEDURES = {
    "coding-agent": [
        "proc-plan-implementation",
        "proc-place-new-behavior",
        "proc-determine-abstraction-earned",
        "proc-review-api",
        "proc-establish-preservation-boundaries",
        "proc-determine-tests-characterization",
        "proc-assess-authority-to-act",
    ],
    "architecture-agent": [
        "proc-assess-architectural-pressure",
        "proc-select-architectural-boundary",
        "proc-identify-domain-boundaries",
        "proc-rank-engineering-risks",
        "proc-assess-authority-to-act",
        "proc-decide-leave-code-alone",
    ],
    "refactoring-agent": [
        "proc-determine-refactoring-earned",
        "proc-select-first-refactoring-campaign",
        "proc-establish-preservation-boundaries",
        "proc-determine-tests-characterization",
        "proc-evaluate-duplication",
        "proc-evaluate-module-depth",
        "proc-stop-and-escalate",
    ],
    "legacy-code-agent": [
        "proc-work-poorly-characterized-code",
        "proc-establish-preservation-boundaries",
        "proc-determine-tests-characterization",
        "proc-distinguish-repair-structural",
        "proc-stop-and-escalate",
    ],
    "performance-agent": [
        "proc-decide-performance-justified",
        "proc-establish-preservation-boundaries",
        "proc-rank-engineering-risks",
        "proc-stop-and-escalate",
    ],
    "review-agent": [
        "proc-review-api",
        "proc-rank-engineering-risks",
        "proc-distinguish-repair-structural",
        "proc-assess-authority-to-act",
    ],
    "debugging-and-repair-agent": [
        "proc-distinguish-repair-structural",
        "proc-establish-preservation-boundaries",
        "proc-determine-tests-characterization",
        "proc-rank-engineering-risks",
        "proc-stop-and-escalate",
    ],
    "repository-assessment-agent": [
        "proc-assess-architectural-pressure",
        "proc-determine-refactoring-earned",
        "proc-rank-engineering-risks",
        "proc-decide-leave-code-alone",
        "proc-assess-authority-to-act",
    ],
}


TASK_BUNDLES = {
    "implementation": {
        "procedures": ["proc-plan-implementation", "proc-place-new-behavior", "proc-determine-abstraction-earned", "proc-determine-tests-characterization"],
        "concept_categories": ["universal", "implementation", "agent-conduct"],
        "conditional_categories": ["domain", "architecture", "performance", "legacy"],
        "evidence": ["evidence-explicit-user-requirements", "evidence-repository-contracts", "evidence-static-source-structure", "evidence-tests"],
    },
    "api-review": {
        "procedures": ["proc-review-api", "proc-establish-preservation-boundaries", "proc-rank-engineering-risks"],
        "concept_categories": ["universal", "implementation", "review", "agent-conduct"],
        "conditional_categories": ["domain", "architecture", "performance"],
        "evidence": ["evidence-repository-contracts", "evidence-static-source-structure", "evidence-tests", "evidence-explicit-user-requirements"],
    },
    "architecture-assessment": {
        "procedures": ["proc-assess-architectural-pressure", "proc-select-architectural-boundary", "proc-rank-engineering-risks", "proc-decide-leave-code-alone"],
        "concept_categories": ["universal", "architecture", "agent-conduct"],
        "conditional_categories": ["domain", "performance", "legacy"],
        "evidence": ["evidence-accepted-design-decisions", "evidence-operational-constraints", "evidence-runtime-observation", "evidence-version-history", "evidence-explicit-user-requirements"],
    },
    "domain-design": {
        "procedures": ["proc-identify-domain-boundaries", "proc-place-new-behavior", "proc-select-architectural-boundary"],
        "concept_categories": ["universal", "domain", "architecture"],
        "conditional_categories": ["implementation", "legacy"],
        "evidence": ["evidence-domain-language", "evidence-explicit-user-requirements", "evidence-static-source-structure", "evidence-version-history"],
    },
    "refactoring": {
        "procedures": ["proc-determine-refactoring-earned", "proc-select-first-refactoring-campaign", "proc-establish-preservation-boundaries", "proc-determine-tests-characterization"],
        "concept_categories": ["universal", "refactoring", "agent-conduct"],
        "conditional_categories": ["legacy", "implementation", "architecture"],
        "evidence": ["evidence-static-source-structure", "evidence-tests", "evidence-version-history", "evidence-co-change", "evidence-incidents"],
    },
    "legacy-change": {
        "procedures": ["proc-work-poorly-characterized-code", "proc-establish-preservation-boundaries", "proc-determine-tests-characterization", "proc-stop-and-escalate"],
        "concept_categories": ["universal", "legacy", "refactoring", "agent-conduct"],
        "conditional_categories": ["implementation", "architecture"],
        "evidence": ["evidence-static-source-structure", "evidence-tests", "evidence-runtime-observation", "evidence-incidents"],
    },
    "defect-repair": {
        "procedures": ["proc-distinguish-repair-structural", "proc-establish-preservation-boundaries", "proc-determine-tests-characterization", "proc-rank-engineering-risks"],
        "concept_categories": ["universal", "implementation", "review", "agent-conduct"],
        "conditional_categories": ["legacy", "performance", "architecture"],
        "evidence": ["evidence-tests", "evidence-runtime-observation", "evidence-incidents", "evidence-static-source-structure"],
    },
    "performance-optimization": {
        "procedures": ["proc-decide-performance-justified", "proc-establish-preservation-boundaries", "proc-rank-engineering-risks"],
        "concept_categories": ["universal", "performance", "agent-conduct"],
        "conditional_categories": ["implementation", "architecture"],
        "evidence": ["evidence-profiling", "evidence-benchmarks", "evidence-runtime-observation", "evidence-operational-constraints", "evidence-tests"],
    },
    "repository-assessment": {
        "procedures": ["proc-assess-architectural-pressure", "proc-determine-refactoring-earned", "proc-rank-engineering-risks", "proc-decide-leave-code-alone"],
        "concept_categories": ["universal", "review", "agent-conduct"],
        "conditional_categories": ["architecture", "refactoring", "legacy", "performance", "domain", "implementation"],
        "evidence": ["evidence-repository-contracts", "evidence-static-source-structure", "evidence-version-history", "evidence-co-change", "evidence-tests", "evidence-generated-artifacts"],
    },
}


def build() -> dict[str, Any]:
    concepts, artifacts = concept_inventory()
    lenses = load(ROOT / "context-lenses.yaml")["lenses"]
    conflicts = load(ROOT / "conflicts.yaml")["conflicts"]
    concept_by_id = {item["id"]: item for item in concepts}

    concept_routes = []
    for concept in sorted(concepts, key=lambda item: item["id"]):
        route = dict(concept["routing"])
        concept_routes.append({"concept_id": concept["id"], "artifact": artifacts[concept["id"]], **route})

    role_bundles = []
    for role, procedure_ids in ROLE_PROCEDURES.items():
        activated = [item for item in concepts if role_matches(role, item["routing"]["activate_for_roles"])]
        core = sorted(item["id"] for item in activated if item["category"] == "universal" and item["routing"]["retrieval_priority"] == "core")
        defaults = sorted(item["id"] for item in activated if item["id"] not in core and item["routing"]["retrieval_priority"] in {"core", "high"})
        conditional = sorted(item["id"] for item in activated if item["id"] not in core and item["id"] not in defaults)
        role_bundles.append({
            "role": role,
            "core_concepts": core,
            "default_concepts": defaults,
            "conditional_concepts": conditional,
            "procedures": procedure_ids,
            "context_lenses": sorted(lens["id"] for lens in lenses if role_matches(role, lens["routing"]["roles"])),
            "conflicts": sorted(item["conflict_id"] for item in conflicts if role_matches(role, item["roles_affected"])),
            "initial_retrieval_budget_hint": min(9000, sum(item["routing"]["retrieval_budget_hint"] for item in activated if item["id"] in set(core + defaults))),
        })

    task_bundles = []
    for task, spec in TASK_BUNDLES.items():
        primary = sorted(item["id"] for item in concepts if item["category"] in spec["concept_categories"] and item["routing"]["retrieval_priority"] in {"core", "high"})
        conditional = sorted(item["id"] for item in concepts if item["category"] in spec["conditional_categories"])
        task_bundles.append({"task": task, "primary_concepts": primary, "conditional_concepts": conditional, **{key: value for key, value in spec.items() if key not in {"concept_categories", "conditional_categories"}}})

    language_bundles = []
    for language in ("Go", "Python"):
        ids = sorted(item["id"] for item in concepts if language in item["routing"]["activate_for_languages"] or language.lower() in [value.lower() for value in item["routing"]["activate_for_languages"]])
        language_bundles.append({"language": language, "concepts": ids, "context_lenses": [f"lens-{language.lower()}"], "activation_gate": "repository language/toolchain and supported-version evidence"})

    risk_routes: dict[str, list[str]] = {}
    for concept in concepts:
        for risk in concept["routing"]["activate_for_risk_classes"]:
            risk_routes.setdefault(risk, []).append(concept["id"])

    return {
        "schema_version": "agent-doctrine-routing-index/1",
        "selection_order": [
            "apply explicit authority and repository-contract precedence",
            "select role bundle",
            "intersect task bundle",
            "activate repository context lenses",
            "activate language and risk routes",
            "apply concept exclusions and prerequisites as hard filters",
            "load related conflicts before choosing a contested position",
        ],
        "always_load": {
            "artifacts": ["universal-doctrine.md", "authority-model.yaml", "change-types.yaml"],
            "concepts": sorted(item["id"] for item in concepts if item["category"] == "universal" and item["routing"]["retrieval_priority"] == "core"),
        },
        "concept_routes": concept_routes,
        "role_bundles": role_bundles,
        "task_bundles": task_bundles,
        "language_bundles": language_bundles,
        "risk_routes": [{"risk_class": risk, "concepts": sorted(ids)} for risk, ids in sorted(risk_routes.items())],
        "routing_guards": [
            "Do not load a specialist concept merely from keyword overlap.",
            "Do not route architecture or performance doctrine to a coding task unless role, signal, language, or risk activation matches.",
            "Exclude generated and vendored targets from ordinary implementation/refactoring routes unless generation or vendor integration is the task.",
            "Missing required evidence routes the agent to evidence collection, a bounded experiment, no change, or escalation—not to lower the threshold.",
            "Routing selects guidance; it never grants selection, execution, verification, or acceptance authority.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = dump(build())
    path = ROOT / "routing-index.yaml"
    if args.check:
        if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
            print("STALE: routing-index.yaml", file=sys.stderr)
            return 1
        print("OK: routing index is current")
        return 0
    path.write_text(rendered, encoding="utf-8")
    print(f"UPDATED: {path.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
