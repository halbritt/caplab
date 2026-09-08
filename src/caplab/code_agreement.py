"""Descriptive two-coder agreement over an explicit expected population."""

from __future__ import annotations


def _fields(value: object, names: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != names:
        raise ValueError(f"{label}: expected exactly {sorted(names)}")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected a non-empty string")
    return value


def _identifiers(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}: expected a non-empty list")
    ids = [_identifier(item, label) for item in value]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label}: duplicate identifier")
    return ids


def _validated_document(document: object) -> tuple:
    """Read judgments against explicit slots without modifying source records."""
    source = _fields(document, {"schema_version", "coder_ids", "worlds",
                                "slots", "judgments"}, "input")
    if source["schema_version"] != "caplab-code-agreement-input/1":
        raise ValueError("unsupported code-agreement input schema")
    coders = _identifiers(source["coder_ids"], "coder_ids")
    if len(coders) != 2:
        raise ValueError("exactly two distinct coder_ids are required")
    if not isinstance(source["worlds"], dict) or not source["worlds"]:
        raise ValueError("worlds: expected a non-empty object")
    worlds = {_identifier(world, "world"): _identifiers(codes, "code_ids")
              for world, codes in source["worlds"].items()}
    if not isinstance(source["slots"], list):
        raise ValueError("slots: expected a list")
    slots = {}
    world_slots = {world: [] for world in worlds}
    for assignment in source["slots"]:
        assignment = _fields(assignment, {"slot", "world"}, "assignment")
        slot = _identifier(assignment["slot"], "slot")
        world = _identifier(assignment["world"], "world")
        if slot in slots:
            raise ValueError(f"duplicate slot: {slot}")
        if world not in worlds:
            raise ValueError(f"slot {slot}: unknown world {world}")
        slots[slot] = world
        world_slots[world].append(slot)
    if not isinstance(source["judgments"], list):
        raise ValueError("judgments: expected a list")
    judgments = {}
    for judgment in source["judgments"]:
        judgment = _fields(judgment, {"slot", "coder_id", "code_id", "value"},
                           "judgment")
        slot = _identifier(judgment["slot"], "judgment slot")
        coder = _identifier(judgment["coder_id"], "coder_id")
        code = _identifier(judgment["code_id"], "code_id")
        if slot not in slots or coder not in coders or code not in worlds[slots[slot]]:
            raise ValueError(f"judgment outside expected population: {slot}/{coder}/{code}")
        key = (slot, coder, code)
        if key in judgments:
            raise ValueError(f"duplicate judgment: {slot}/{coder}/{code}")
        value = judgment["value"]
        if value is not None and type(value) is not bool:
            raise ValueError(f"{slot}/{coder}/{code}: value must be Boolean or null")
        judgments[key] = value

    return coders, worlds, slots, world_slots, judgments


def _agreement_report(validated: tuple) -> dict:
    coders, worlds, slots, world_slots, judgments = validated

    reports = []
    for world in sorted(worlds):
        for code in sorted(worlds[world]):
            joint = {"00": 0, "01": 0, "10": 0, "11": 0}
            missing = dict.fromkeys(coders, 0)
            unavailable = dict.fromkeys(coders, 0)
            for slot in world_slots[world]:
                pair = []
                for coder in coders:
                    key = (slot, coder, code)
                    if key not in judgments:
                        missing[coder] += 1
                    elif judgments[key] is None:
                        unavailable[coder] += 1
                    else:
                        pair.append(judgments[key])
                if len(pair) == 2:
                    joint[f"{int(pair[0])}{int(pair[1])}"] += 1
            count = sum(joint.values())
            observed = chance = kappa = None
            reason = "no-complete-pairs"
            if count:
                agreeing = joint["00"] + joint["11"]
                expected = ((joint["00"] + joint["01"]) * (joint["00"] + joint["10"])
                            + (joint["10"] + joint["11"]) * (joint["01"] + joint["11"]))
                observed = agreeing / count
                chance = expected / (count * count)
                if expected == count * count:
                    reason = "chance-agreement-is-one"
                else:
                    kappa = (agreeing * count - expected) / (count * count - expected)
                    reason = None
            reports.append({
                "world": world, "code_id": code,
                "expected_pairs": len(world_slots[world]),
                "complete_pairs": count,
                "incomplete_pairs": len(world_slots[world]) - count,
                "missing_judgments": missing, "unavailable_judgments": unavailable,
                "joint_counts": joint, "observed_agreement": observed,
                "chance_agreement": chance, "kappa": kappa,
                "kappa_unavailable_reason": reason,
            })
    return {
        "schema_version": "caplab-code-agreement-report/1",
        "coder_ids": list(coders), "expected_slots": len(slots), "codes": reports,
        "interpretation": (
            "agreement on complete paired judgments only; does not establish accuracy, "
            "coder independence, blinding, population completeness, or study readiness; "
            "no threshold or acceptance decision is applied"),
    }


def build_code_agreement_report(document: object) -> dict:
    """Report agreement on complete pairs; do not qualify coders or references."""
    return _agreement_report(_validated_document(document))


def _reference_labels(reference: object, worlds: dict, slots: dict) -> tuple:
    source = _fields(reference, {"schema_version", "reference_id", "judgments"}, "reference")
    if source["schema_version"] != "caplab-code-reference-input/1":
        raise ValueError("unsupported code-reference input schema")
    reference_id = _identifier(source["reference_id"], "reference_id")
    if not isinstance(source["judgments"], list):
        raise ValueError("reference judgments: expected a list")
    labels = {}
    for label in source["judgments"]:
        label = _fields(label, {"slot", "code_id", "value", "evidence_locator"}, "reference judgment")
        slot = _identifier(label["slot"], "reference slot")
        code = _identifier(label["code_id"], "reference code_id")
        _identifier(label["evidence_locator"], "reference evidence_locator")
        if slot not in slots or code not in worlds[slots[slot]]:
            raise ValueError(f"reference outside expected population: {slot}/{code}")
        key = (slot, code)
        if key in labels:
            raise ValueError(f"duplicate reference judgment: {slot}/{code}")
        if label["value"] is not None and type(label["value"]) is not bool:
            raise ValueError(f"{slot}/{code}: reference must be Boolean or null")
        labels[key] = label["value"]
    return reference_id, labels


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _compare_coder(judgments: dict, known: dict, coder: str, code: str) -> dict:
    joint = {"00": 0, "01": 0, "10": 0, "11": 0}
    missing = unavailable = 0
    for slot, reference in known.items():
        key = (slot, coder, code)
        if key not in judgments:
            missing += 1
        elif judgments[key] is None:
            unavailable += 1
        else:
            joint[f"{int(reference)}{int(judgments[key])}"] += 1
    count = sum(joint.values())
    return {
        "coder_id": coder, "compared_labels": count,
        "missing_judgments_on_known_references": missing,
        "unavailable_judgments_on_known_references": unavailable,
        "reference_joint_counts": joint,
        "reference_coverage": _ratio(count, len(known)),
        "reference_agreement": _ratio(joint["00"] + joint["11"], count),
        "positive_reference_agreement": _ratio(joint["11"], joint["10"] + joint["11"]),
        "negative_reference_agreement": _ratio(joint["00"], joint["00"] + joint["01"]),
    }


def build_code_reference_report(document: object, reference: object) -> dict:
    """Compare supplied labels; their truth, provenance and independence are unverified."""
    validated = _validated_document(document)
    coders, worlds, slots, world_slots, judgments = validated
    reference_id, labels = _reference_labels(reference, worlds, slots)
    rows = []
    for world in sorted(worlds):
        for code in sorted(worlds[world]):
            expected = world_slots[world]
            known = {slot: labels[(slot, code)] for slot in expected
                     if (slot, code) in labels and labels[(slot, code)] is not None}
            reference_counts = {
                "world": world, "code_id": code, "expected_labels": len(expected),
                "missing_reference_labels": sum((slot, code) not in labels for slot in expected),
                "unavailable_reference_labels": sum((slot, code) in labels and labels[(slot, code)] is None
                                                    for slot in expected),
                "known_reference_labels": len(known),
                "positive_reference_labels": sum(known.values()),
                "negative_reference_labels": len(known) - sum(known.values()),
            }
            for coder in coders:
                rows.append({**reference_counts, **_compare_coder(judgments, known, coder, code)})
    return {
        "schema_version": "caplab-code-reference-report/1", "reference_id": reference_id,
        "agreement": _agreement_report(validated), "reference_comparisons": rows,
        "reference_joint_axes": ["reference", "coder"],
        "interpretation": (
            "comparison against supplied, unverified reference labels on comparable observations only; "
            "does not establish reference truth, independence, human authorship, blinding, "
            "representativeness, coder accuracy qualification or study readiness; no threshold is applied"),
    }
