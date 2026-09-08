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


def build_code_agreement_report(document: object) -> dict:
    """Validate labels against planned slots; compute each world/code separately.

    Values are Boolean or explicit null (unavailable). Missing judgment records
    are counted separately. Neither source custody nor the expected population's
    freeze is verified by accepting this document.
    """
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
