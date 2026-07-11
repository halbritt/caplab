#!/usr/bin/env python3
"""Build the selective-retrieval index from doctrine routing metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]

SAFETY_KERNEL = (
    "agent-conduct-authority-bounded-action",
    "universal-evidence-before-intervention",
    "universal-no-change-option",
    "universal-preserve-behavior-by-default",
    "universal-repository-contract-precedence",
    "universal-separate-semantic-structural-change",
)

DEFAULT_RETRIEVAL_BUDGET = 5000


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected mapping")
    return document


def dump_yaml(document: dict[str, Any]) -> str:
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=1000)


def concept_inventory() -> tuple[list[dict[str, Any]], dict[str, str]]:
    concepts: list[dict[str, Any]] = []
    concept_artifacts: dict[str, str] = {}
    for path in sorted((ROOT / "concepts").glob("*.yaml")):
        for concept in load_yaml(path).get("concepts", []):
            concepts.append(concept)
            concept_artifacts[concept["id"]] = str(path.relative_to(ROOT))
    return concepts, concept_artifacts


ROLE_ALIASES = {
    "coding-agent": {"implementation-agent"},
    "architecture-agent": {"architectural-agent", "domain-design-agent"},
    "legacy-code-agent": {"legacy-agent"},
    "review-agent": {"dependency-agent"},
    "debugging-and-repair-agent": {"repair-agent", "debugging-agent"},
}

TASK_ALIASES = {
    "implementation": {"feature-implementation"},
    "api-review": {"api-design-review"},
    "architecture-assessment": {"architecture-review"},
    "domain-design": {"domain-modeling"},
    "refactoring": {"structural-refactoring"},
    "legacy-change": {"legacy-code-change"},
    "defect-repair": {"repair"},
    "performance-optimization": {"performance-work"},
    "repository-assessment": {"repo-assessment"},
}


def role_matches(expected: str, declared_roles: list[str]) -> bool:
    return expected in declared_roles or bool(
        ROLE_ALIASES.get(expected, set()) & set(declared_roles)
    )


def canonical_role(role: str) -> str:
    for canonical, aliases in ROLE_ALIASES.items():
        if role == canonical or role in aliases:
            return canonical
    return role


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
        "procedures": [
            "proc-plan-implementation",
            "proc-place-new-behavior",
            "proc-determine-abstraction-earned",
            "proc-determine-tests-characterization",
        ],
        "change_types": ["change-feature-implementation"],
        "concept_categories": ["universal", "implementation", "agent-conduct"],
        "conditional_categories": ["domain", "architecture", "performance", "legacy"],
        "evidence": [
            "evidence-explicit-user-requirements",
            "evidence-repository-contracts",
            "evidence-static-source-structure",
            "evidence-tests",
        ],
    },
    "api-review": {
        "procedures": [
            "proc-review-api",
            "proc-establish-preservation-boundaries",
            "proc-rank-engineering-risks",
        ],
        "change_types": [],
        "concept_categories": [
            "universal",
            "implementation",
            "review",
            "agent-conduct",
        ],
        "conditional_categories": ["domain", "architecture", "performance"],
        "evidence": [
            "evidence-repository-contracts",
            "evidence-static-source-structure",
            "evidence-tests",
            "evidence-explicit-user-requirements",
        ],
    },
    "architecture-assessment": {
        "procedures": [
            "proc-assess-architectural-pressure",
            "proc-select-architectural-boundary",
            "proc-rank-engineering-risks",
            "proc-decide-leave-code-alone",
        ],
        "change_types": ["change-architectural-restructuring"],
        "concept_categories": ["universal", "architecture", "agent-conduct"],
        "conditional_categories": ["domain", "performance", "legacy"],
        "evidence": [
            "evidence-accepted-design-decisions",
            "evidence-operational-constraints",
            "evidence-runtime-observation",
            "evidence-version-history",
            "evidence-explicit-user-requirements",
        ],
    },
    "domain-design": {
        "procedures": [
            "proc-identify-domain-boundaries",
            "proc-place-new-behavior",
            "proc-select-architectural-boundary",
        ],
        "change_types": [
            "change-feature-implementation",
            "change-architectural-restructuring",
        ],
        "concept_categories": ["universal", "domain", "architecture"],
        "conditional_categories": ["implementation", "legacy"],
        "evidence": [
            "evidence-domain-language",
            "evidence-explicit-user-requirements",
            "evidence-static-source-structure",
            "evidence-version-history",
        ],
    },
    "refactoring": {
        "procedures": [
            "proc-determine-refactoring-earned",
            "proc-select-first-refactoring-campaign",
            "proc-establish-preservation-boundaries",
            "proc-determine-tests-characterization",
        ],
        "change_types": ["change-refactoring"],
        "concept_categories": ["universal", "refactoring", "agent-conduct"],
        "conditional_categories": ["legacy", "implementation", "architecture"],
        "evidence": [
            "evidence-static-source-structure",
            "evidence-tests",
            "evidence-version-history",
            "evidence-co-change",
            "evidence-incidents",
        ],
    },
    "legacy-change": {
        "procedures": [
            "proc-work-poorly-characterized-code",
            "proc-establish-preservation-boundaries",
            "proc-determine-tests-characterization",
            "proc-stop-and-escalate",
        ],
        "change_types": [
            "change-feature-implementation",
            "change-defect-repair",
            "change-refactoring",
        ],
        "concept_categories": ["universal", "legacy", "refactoring", "agent-conduct"],
        "conditional_categories": ["implementation", "architecture"],
        "evidence": [
            "evidence-static-source-structure",
            "evidence-tests",
            "evidence-runtime-observation",
            "evidence-incidents",
        ],
    },
    "defect-repair": {
        "procedures": [
            "proc-distinguish-repair-structural",
            "proc-establish-preservation-boundaries",
            "proc-determine-tests-characterization",
            "proc-rank-engineering-risks",
        ],
        "change_types": ["change-defect-repair"],
        "concept_categories": [
            "universal",
            "implementation",
            "review",
            "agent-conduct",
        ],
        "conditional_categories": ["legacy", "performance", "architecture"],
        "evidence": [
            "evidence-tests",
            "evidence-runtime-observation",
            "evidence-incidents",
            "evidence-static-source-structure",
        ],
    },
    "performance-optimization": {
        "procedures": [
            "proc-decide-performance-justified",
            "proc-establish-preservation-boundaries",
            "proc-rank-engineering-risks",
        ],
        "change_types": ["change-optimization"],
        "concept_categories": ["universal", "performance", "agent-conduct"],
        "conditional_categories": ["implementation", "architecture"],
        "evidence": [
            "evidence-profiling",
            "evidence-benchmarks",
            "evidence-runtime-observation",
            "evidence-operational-constraints",
            "evidence-tests",
        ],
    },
    "repository-assessment": {
        "procedures": [
            "proc-assess-architectural-pressure",
            "proc-determine-refactoring-earned",
            "proc-rank-engineering-risks",
            "proc-decide-leave-code-alone",
        ],
        "change_types": [],
        "concept_categories": ["universal", "review", "agent-conduct"],
        "conditional_categories": [
            "architecture",
            "refactoring",
            "legacy",
            "performance",
            "domain",
            "implementation",
        ],
        "evidence": [
            "evidence-repository-contracts",
            "evidence-static-source-structure",
            "evidence-version-history",
            "evidence-co-change",
            "evidence-tests",
            "evidence-generated-artifacts",
        ],
    },
}


def build() -> dict[str, Any]:
    concepts, concept_artifacts = concept_inventory()
    lenses = load_yaml(ROOT / "context-lenses.yaml")["lenses"]
    conflicts = load_yaml(ROOT / "conflicts.yaml")["conflicts"]

    task_primary: dict[str, set[str]] = {}
    task_conditional: dict[str, set[str]] = {}
    for task, spec in TASK_BUNDLES.items():
        task_primary[task] = {
            concept["id"]
            for concept in concepts
            if concept["category"] in spec["concept_categories"]
            and concept["routing"]["retrieval_priority"] in {"core", "high"}
        }
        task_conditional[task] = {
            concept["id"]
            for concept in concepts
            if concept["category"] in spec["conditional_categories"]
            or (
                concept["category"] in spec["concept_categories"]
                and concept["id"] not in task_primary[task]
            )
        }

    concept_routes = []
    for concept in sorted(concepts, key=lambda candidate: candidate["id"]):
        route = dict(concept["routing"])
        route["activate_for_role_families"] = sorted(
            {canonical_role(role) for role in route["activate_for_roles"]}
        )
        route["activate_for_task_families"] = sorted(
            task for task, members in task_primary.items() if concept["id"] in members
        )
        route["conditional_for_task_families"] = sorted(
            task
            for task, members in task_conditional.items()
            if concept["id"] in members
        )
        concept_routes.append(
            {
                "concept_id": concept["id"],
                "artifact": concept_artifacts[concept["id"]],
                **route,
            }
        )

    role_bundles = []
    for role, procedure_ids in ROLE_PROCEDURES.items():
        activated = [
            concept
            for concept in concepts
            if role_matches(role, concept["routing"]["activate_for_roles"])
        ]
        core = sorted(
            concept["id"]
            for concept in activated
            if concept["category"] == "universal"
            and concept["routing"]["retrieval_priority"] == "core"
        )
        defaults = sorted(
            concept["id"]
            for concept in activated
            if concept["id"] not in core
            and concept["routing"]["retrieval_priority"] in {"core", "high"}
        )
        conditional = sorted(
            concept["id"]
            for concept in activated
            if concept["id"] not in core and concept["id"] not in defaults
        )
        role_bundles.append(
            {
                "role": role,
                "core_concepts": core,
                "default_concepts": defaults,
                "conditional_concepts": conditional,
                "procedures": procedure_ids,
                "context_lenses": sorted(
                    lens["id"]
                    for lens in lenses
                    if role_matches(role, lens["routing"]["roles"])
                ),
                "conflicts": sorted(
                    conflict["conflict_id"]
                    for conflict in conflicts
                    if role_matches(role, conflict["roles_affected"])
                ),
                "initial_retrieval_budget_hint": min(
                    DEFAULT_RETRIEVAL_BUDGET,
                    sum(
                        concept["routing"]["retrieval_budget_hint"]
                        for concept in activated
                        if concept["id"] in set(core + defaults)
                    ),
                ),
            }
        )

    task_bundles = []
    for task, spec in TASK_BUNDLES.items():
        primary = sorted(
            concept["id"]
            for concept in concepts
            if concept["category"] in spec["concept_categories"]
            and concept["routing"]["retrieval_priority"] in {"core", "high"}
        )
        conditional = sorted(
            concept["id"]
            for concept in concepts
            if concept["category"] in spec["conditional_categories"]
        )
        task_bundles.append(
            {
                "task": task,
                "primary_concepts": primary,
                "conditional_concepts": conditional,
                **{
                    setting: setting_value
                    for setting, setting_value in spec.items()
                    if setting not in {"concept_categories", "conditional_categories"}
                },
            }
        )

    role_registry = [
        {"role": role, "aliases": sorted(ROLE_ALIASES.get(role, set()))}
        for role in ROLE_PROCEDURES
    ]
    task_registry = []
    for task in TASK_BUNDLES:
        variants = sorted(
            {
                variant
                for concept in concepts
                if concept["id"] in task_primary[task] | task_conditional[task]
                for variant in concept["routing"]["activate_for_tasks"]
            }
        )
        task_registry.append(
            {
                "family": task,
                "aliases": sorted(TASK_ALIASES.get(task, set())),
                "variants": variants,
            }
        )

    language_bundles = []
    for language in ("Go", "Python"):
        ids = sorted(
            concept["id"]
            for concept in concepts
            if language in concept["routing"]["activate_for_languages"]
            or language.lower()
            in [
                declared_language.lower()
                for declared_language in concept["routing"]["activate_for_languages"]
            ]
        )
        language_bundles.append(
            {
                "language": language,
                "concepts": ids,
                "context_lenses": [f"lens-{language.lower()}"],
                "activation_gate": "repository language/toolchain and supported-version evidence",
            }
        )

    risk_routes: dict[str, list[str]] = {}
    for concept in concepts:
        for risk in concept["routing"]["activate_for_risk_classes"]:
            risk_routes.setdefault(risk, []).append(concept["id"])

    return {
        "schema_version": "agent-doctrine-routing-index/1",
        "role_registry": role_registry,
        "task_registry": task_registry,
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
            "artifacts": [
                "universal-doctrine.md",
                "authority-model.yaml",
                "change-types.yaml",
            ],
            "policy": "universal-safety-kernel",
            "concepts": list(SAFETY_KERNEL),
        },
        "concept_routes": concept_routes,
        "role_bundles": role_bundles,
        "task_bundles": task_bundles,
        "language_bundles": language_bundles,
        "risk_routes": [
            {"risk_class": risk, "concepts": sorted(ids)}
            for risk, ids in sorted(risk_routes.items())
        ],
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
    rendered = dump_yaml(build())
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
