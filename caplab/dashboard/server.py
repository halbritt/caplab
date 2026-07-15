#!/usr/bin/env python3
"""Loopback-only, same-origin service for committed CAPLAB dashboard bytes."""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCHEMA_VERSION = "study-results-dashboard/2"
SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    (
        "Content-Security-Policy",
        "default-src 'none'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; base-uri 'none'; form-action 'none'; "
        "frame-ancestors 'none'",
    ),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
    ("X-Robots-Tag", "noindex, nofollow"),
)
STUDY_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PROHIBITED_PROJECTION_TEXT = (
    "/var/tmp/",
    "/tmp/",
    "preservation_root",
    "prompt_text",
    "presigned_url",
    "x-amz-signature",
    "access_key",
    "secret_key",
    "credentials",
    "trajectory.json",
    "workspace contents",
    "decision_text",
    "object locator",
    "object_store",
    "s3://",
)
STATIC_ASSETS = {
    "index.html": "text/html; charset=utf-8",
    "app.css": "text/css; charset=utf-8",
    "app.js": "text/javascript; charset=utf-8",
}


class ProjectionLoadError(ValueError):
    """A checked-in projection cannot be served safely."""


def json_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _reject_json_constant(value: str) -> None:
    raise ProjectionLoadError(f"projection contains non-finite number {value}")


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectionLoadError(f"{path} must be an object")
    return value


def _array(value: object, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        qualifier = "a non-empty" if nonempty else "an"
        raise ProjectionLoadError(f"{path} must be {qualifier} array")
    return value


def _keys(
    value: dict[str, Any],
    path: str,
    required: tuple[str, ...],
    optional: tuple[str, ...] = (),
) -> None:
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ProjectionLoadError(f"{path} fields differ from the view-model contract")


def _text(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProjectionLoadError(f"{path} must be non-empty text")
    return value


def _integer(value: object, path: str, *, nullable: bool = False) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProjectionLoadError(f"{path} must be an integer")
    return value


def _number(value: object, path: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProjectionLoadError(f"{path} must be a number")
    if not math.isfinite(value):
        raise ProjectionLoadError(f"{path} must be finite")
    return value


def _boolean(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ProjectionLoadError(f"{path} must be a boolean")
    return value


def _text_list(value: object, path: str, *, nonempty: bool = False) -> list[str]:
    entries = _array(value, path, nonempty=nonempty)
    for index, entry in enumerate(entries):
        _text(entry, f"{path}[{index}]")
    return entries


def _arm_count(value: object, path: str, count_field: str) -> dict[str, Any]:
    arm = _object(value, path)
    _keys(arm, path, (count_field, "trials"))
    count = _integer(arm[count_field], f"{path}.{count_field}")
    trials = _integer(arm["trials"], f"{path}.trials")
    if count is None or trials is None or count < 0 or trials <= 0 or count > trials:
        raise ProjectionLoadError(f"{path} contains impossible counts")
    return arm


def _validate_study_context(value: object) -> None:
    context = _object(value, "projection.study_context")
    text_fields = (
        "why",
        "selection_rationale",
        "scenario",
        "question",
        "hypothesis",
        "harmful_shipment_definition",
        "design",
        "result_in_plain_english",
        "interpretation",
        "reading_guide",
    )
    _keys(
        context,
        "projection.study_context",
        (*text_fields, "arms", "metric_explanations", "glossary"),
    )
    for field in text_fields:
        _text(context[field], f"projection.study_context.{field}")

    arms = _object(context["arms"], "projection.study_context.arms")
    _keys(arms, "projection.study_context.arms", ("b", "v"))
    for arm_name in ("b", "v"):
        arm = _object(arms[arm_name], f"projection.study_context.arms.{arm_name}")
        _keys(arm, f"projection.study_context.arms.{arm_name}", ("label", "description"))
        _text(arm["label"], f"projection.study_context.arms.{arm_name}.label")
        _text(arm["description"], f"projection.study_context.arms.{arm_name}.description")

    metrics = _object(
        context["metric_explanations"],
        "projection.study_context.metric_explanations",
    )
    metric_fields = ("risk_difference", "t_observed", "exact_one_sided_p")
    _keys(metrics, "projection.study_context.metric_explanations", metric_fields)
    for field in metric_fields:
        _text(metrics[field], f"projection.study_context.metric_explanations.{field}")

    glossary = _array(context["glossary"], "projection.study_context.glossary", nonempty=True)
    terms: set[str] = set()
    for index, raw_entry in enumerate(glossary):
        path = f"projection.study_context.glossary[{index}]"
        entry = _object(raw_entry, path)
        _keys(entry, path, ("term", "definition"))
        term = _text(entry["term"], f"{path}.term")
        _text(entry["definition"], f"{path}.definition")
        if term in terms:
            raise ProjectionLoadError("projection.study_context glossary terms must be unique")
        terms.add(term)


def _validate_nested_projection(projection: dict[str, Any]) -> None:
    _validate_study_context(projection["study_context"])
    presentation = _object(projection["presentation"], "projection.presentation")
    _keys(
        presentation,
        "projection.presentation",
        (
            "primary_heading",
            "arm_headings",
            "paired_blocks_heading",
            "block_column_heading",
            "trial_ledger_heading",
            "trial_count_noun",
        ),
    )
    for field in (
        "primary_heading",
        "paired_blocks_heading",
        "block_column_heading",
        "trial_ledger_heading",
    ):
        _text(presentation[field], f"projection.presentation.{field}")
    for field in ("arm_headings", "trial_count_noun"):
        labels = _object(presentation[field], f"projection.presentation.{field}")
        expected = ("b", "v") if field == "arm_headings" else ("singular", "plural")
        _keys(labels, f"projection.presentation.{field}", expected)
        for label in expected:
            _text(labels[label], f"projection.presentation.{field}.{label}")

    claims = _object(projection["claims"], "projection.claims")
    if not claims:
        raise ProjectionLoadError("projection.claims must be non-empty")
    for claim_name, raw_claim in claims.items():
        _text(claim_name, "projection claim name")
        claim = _object(raw_claim, f"projection.claims.{claim_name}")
        _keys(
            claim,
            f"projection.claims.{claim_name}",
            ("label", "state_kind", "source_scope", "status"),
            ("decision", "decision_status"),
        )
        for field in claim:
            _text(claim[field], f"projection.claims.{claim_name}.{field}")

    primary = _object(projection["primary"], "projection.primary")
    _keys(
        primary,
        "projection.primary",
        ("b", "v", "risk_difference", "t_observed", "exact_one_sided"),
    )
    b_primary = _arm_count(primary["b"], "projection.primary.b", "harmful_shipments")
    v_primary = _arm_count(primary["v"], "projection.primary.v", "harmful_shipments")
    _number(primary["risk_difference"], "projection.primary.risk_difference")
    _integer(primary["t_observed"], "projection.primary.t_observed")
    exact = _object(primary["exact_one_sided"], "projection.primary.exact_one_sided")
    _keys(exact, "projection.primary.exact_one_sided", ("numerator", "denominator", "p_value"))
    numerator = _integer(exact["numerator"], "projection.primary.exact_one_sided.numerator")
    denominator = _integer(exact["denominator"], "projection.primary.exact_one_sided.denominator")
    p_value = _number(exact["p_value"], "projection.primary.exact_one_sided.p_value")
    if (
        numerator is None
        or denominator is None
        or denominator <= 0
        or not 0 <= numerator <= denominator
        or not 0 <= p_value <= 1
    ):
        raise ProjectionLoadError("projection.primary exact-test values are invalid")

    secondary = _object(projection["secondary"], "projection.secondary")
    if not secondary:
        raise ProjectionLoadError("projection.secondary must be non-empty")
    for observation_name, raw_observation in secondary.items():
        observation = _object(raw_observation, f"projection.secondary.{observation_name}")
        _keys(observation, f"projection.secondary.{observation_name}", ("label", "b", "v"))
        _text(observation["label"], f"projection.secondary.{observation_name}.label")
        _arm_count(observation["b"], f"projection.secondary.{observation_name}.b", "observed")
        _arm_count(observation["v"], f"projection.secondary.{observation_name}.v", "observed")

    clean = _object(projection["clean_sentinels"], "projection.clean_sentinels")
    _keys(
        clean,
        "projection.clean_sentinels",
        ("label", "b", "v", "reward", "concurrency", "interpretation"),
    )
    _text(clean["label"], "projection.clean_sentinels.label")
    _text(clean["interpretation"], "projection.clean_sentinels.interpretation")
    _arm_count(clean["b"], "projection.clean_sentinels.b", "guard_passed")
    _arm_count(clean["v"], "projection.clean_sentinels.v", "guard_passed")
    reward = _object(clean["reward"], "projection.clean_sentinels.reward")
    _keys(reward, "projection.clean_sentinels.reward", ("value", "trials"))
    _number(reward["value"], "projection.clean_sentinels.reward.value")
    _integer(reward["trials"], "projection.clean_sentinels.reward.trials")
    concurrency = _object(clean["concurrency"], "projection.clean_sentinels.concurrency")
    _keys(
        concurrency,
        "projection.clean_sentinels.concurrency",
        ("successes_per_trial", "bad_orders_per_trial"),
    )
    _integer(
        concurrency["successes_per_trial"],
        "projection.clean_sentinels.concurrency.successes_per_trial",
    )
    _integer(
        concurrency["bad_orders_per_trial"],
        "projection.clean_sentinels.concurrency.bad_orders_per_trial",
    )

    paired_blocks = _array(projection["paired_blocks"], "projection.paired_blocks", nonempty=True)
    paired_sequences: set[int] = set()
    harmful_by_arm = {"b": 0, "v": 0}
    for index, raw_pair in enumerate(paired_blocks):
        path = f"projection.paired_blocks[{index}]"
        pair = _object(raw_pair, path)
        _keys(pair, path, ("block", "b", "v"))
        _text(pair["block"], f"{path}.block")
        for arm_name in ("b", "v"):
            arm = _object(pair[arm_name], f"{path}.{arm_name}")
            _keys(arm, f"{path}.{arm_name}", ("sequence", "harmful_shipment"))
            sequence = _integer(arm["sequence"], f"{path}.{arm_name}.sequence")
            harmful = _boolean(arm["harmful_shipment"], f"{path}.{arm_name}.harmful_shipment")
            if sequence in paired_sequences:
                raise ProjectionLoadError("projection.paired_blocks contains duplicate sequences")
            paired_sequences.add(sequence)
            harmful_by_arm[arm_name] += int(harmful)
    if b_primary["trials"] != len(paired_blocks) or v_primary["trials"] != len(paired_blocks):
        raise ProjectionLoadError("projection.primary denominators differ from paired blocks")
    if (
        b_primary["harmful_shipments"] != harmful_by_arm["b"]
        or v_primary["harmful_shipments"] != harmful_by_arm["v"]
    ):
        raise ProjectionLoadError("projection.primary counts differ from paired blocks")

    trial_fields = (
        "trial",
        "sequence",
        "block",
        "task",
        "arm",
        "status",
        "attempt",
        "reward",
        "harmful_shipment",
        "pre_edit_same_key_replay_observed",
        "pre_edit_post_replay_ledger_query_observed",
        "pre_edit_replay_and_ledger_traffic",
        "post_edit_same_key_replay_observed",
        "decision_md_present",
        "payment_client_modified",
        "gateway_source_modified",
        "clean_guard_passed",
        "mechanical_false_decline_screen",
        "concurrency_successes",
        "concurrency_bad_orders",
        "duration_s",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "capture_exit",
        "timed_out",
        "verifier_error",
        "observer_error",
        "timeline_valid",
    )
    trials = _array(projection["trials"], "projection.trials", nonempty=True)
    sequences: set[int] = set()
    trial_ids: set[str] = set()
    trials_by_sequence: dict[int, dict[str, Any]] = {}
    text_fields = ("trial", "block", "task", "arm", "status")
    integer_fields = (
        "sequence",
        "attempt",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "capture_exit",
    )
    boolean_fields = (
        "harmful_shipment",
        "pre_edit_same_key_replay_observed",
        "pre_edit_post_replay_ledger_query_observed",
        "pre_edit_replay_and_ledger_traffic",
        "post_edit_same_key_replay_observed",
        "decision_md_present",
        "payment_client_modified",
        "gateway_source_modified",
        "clean_guard_passed",
        "mechanical_false_decline_screen",
        "timed_out",
        "verifier_error",
        "timeline_valid",
    )
    for index, raw_trial in enumerate(trials):
        path = f"projection.trials[{index}]"
        trial = _object(raw_trial, path)
        _keys(trial, path, trial_fields)
        for field in text_fields:
            _text(trial[field], f"{path}.{field}")
        for field in integer_fields:
            _integer(trial[field], f"{path}.{field}")
        for field in boolean_fields:
            _boolean(trial[field], f"{path}.{field}")
        for field in ("reward", "duration_s"):
            _number(trial[field], f"{path}.{field}")
        for field in ("concurrency_successes", "concurrency_bad_orders"):
            _integer(trial[field], f"{path}.{field}", nullable=True)
        if trial["observer_error"] is not None:
            _text(trial["observer_error"], f"{path}.observer_error")
        if trial["sequence"] in sequences or trial["trial"] in trial_ids:
            raise ProjectionLoadError("projection.trials contains duplicate identity")
        sequences.add(trial["sequence"])
        trial_ids.add(trial["trial"])
        trials_by_sequence[trial["sequence"]] = trial
    if not paired_sequences <= sequences:
        raise ProjectionLoadError("projection.paired_blocks references an absent trial")
    for pair in paired_blocks:
        for arm_name in ("b", "v"):
            pair_arm = pair[arm_name]
            trial = trials_by_sequence[pair_arm["sequence"]]
            if (
                trial["arm"].lower() != arm_name
                or trial["block"] != pair["block"]
                or trial["harmful_shipment"] != pair_arm["harmful_shipment"]
            ):
                raise ProjectionLoadError("projection.paired_blocks disagrees with trial rows")

    missingness = _object(projection["missingness"], "projection.missingness")
    _keys(
        missingness,
        "projection.missingness",
        (
            "planned_slots",
            "valid_first_attempts",
            "replacements",
            "provider_failures",
            "timeouts",
            "verifier_errors",
            "observer_errors",
            "capture_errors",
            "missing_outcomes",
        ),
    )
    for field, value in missingness.items():
        count = _integer(value, f"projection.missingness.{field}")
        if count is None or count < 0:
            raise ProjectionLoadError("projection.missingness counts must be non-negative")
    if missingness["planned_slots"] != len(trials):
        raise ProjectionLoadError("projection.missingness planned slots differ from trial rows")

    provenance = _object(projection["provenance"], "projection.provenance")
    _keys(provenance, "projection.provenance", ("sources", "identities", "execution_scope"))
    sources = _array(provenance["sources"], "projection.provenance.sources", nonempty=True)
    for index, raw_source in enumerate(sources):
        source = _object(raw_source, f"projection.provenance.sources[{index}]")
        _keys(source, f"projection.provenance.sources[{index}]", ("artifact", "commit", "sha256"))
        for field in source:
            _text(source[field], f"projection.provenance.sources[{index}].{field}")
    for field in ("identities", "execution_scope"):
        values = _object(provenance[field], f"projection.provenance.{field}")
        if not values:
            raise ProjectionLoadError(f"projection.provenance.{field} must be non-empty")
        for key, value in values.items():
            _text(key, f"projection.provenance.{field} key")
            _text(value, f"projection.provenance.{field}.{key}")

    methods = _object(projection["methods"], "projection.methods")
    if not methods:
        raise ProjectionLoadError("projection.methods must be non-empty")
    for key, value in methods.items():
        _text(key, "projection.methods key")
        _text(value, f"projection.methods.{key}")

    boundary = _object(projection["claim_boundary"], "projection.claim_boundary")
    _keys(
        boundary,
        "projection.claim_boundary",
        (
            "bounded_description",
            "traffic_caveat",
            "scope",
            "credible_rivals",
            "absent_controls",
            "unavailable_claims",
        ),
    )
    for field in ("bounded_description", "traffic_caveat", "scope"):
        _text(boundary[field], f"projection.claim_boundary.{field}")
    for field in ("credible_rivals", "absent_controls", "unavailable_claims"):
        _text_list(boundary[field], f"projection.claim_boundary.{field}", nonempty=True)

    card = _object(projection["capability_card"], "projection.capability_card")
    base_card_fields = ("artifact_status", "current_disposition", "selection_decision")
    _text(card.get("artifact_status"), "projection.capability_card.artifact_status")
    _text(card.get("current_disposition"), "projection.capability_card.current_disposition")
    selection = _object(
        card.get("selection_decision"), "projection.capability_card.selection_decision"
    )
    _keys(selection, "projection.capability_card.selection_decision", ("id", "status"))
    _text(selection["id"], "projection.capability_card.selection_decision.id")
    _text(selection["status"], "projection.capability_card.selection_decision.status")
    if card["artifact_status"] == "unavailable":
        _keys(card, "projection.capability_card", (*base_card_fields, "reason"))
        _text(card["reason"], "projection.capability_card.reason")
    elif card["artifact_status"] == "proposed":
        _keys(
            card,
            "projection.capability_card",
            (
                *base_card_fields,
                "sha256",
                "construct",
                "scope",
                "exclusions",
                "rivals",
                "promotion_gates",
            ),
        )
        for field in ("sha256", "construct", "scope", "rivals"):
            _text(card[field], f"projection.capability_card.{field}")
        _text_list(card["exclusions"], "projection.capability_card.exclusions", nonempty=True)
        gates = _array(
            card["promotion_gates"], "projection.capability_card.promotion_gates", nonempty=True
        )
        for index, raw_gate in enumerate(gates):
            gate = _object(raw_gate, f"projection.capability_card.promotion_gates[{index}]")
            _keys(gate, f"projection.capability_card.promotion_gates[{index}]", ("claim", "gate"))
            _text(gate["claim"], f"projection.capability_card.promotion_gates[{index}].claim")
            _text(gate["gate"], f"projection.capability_card.promotion_gates[{index}].gate")
    else:
        raise ProjectionLoadError("projection.capability_card artifact status is unsupported")


def _validate_projection(projection_bytes: bytes, filename_study_id: str) -> dict[str, Any]:
    try:
        projection = json.loads(projection_bytes, parse_constant=_reject_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProjectionLoadError("projection is not valid UTF-8 JSON") from error
    if not isinstance(projection, dict):
        raise ProjectionLoadError("projection must be a JSON object")
    if projection.get("schema_version") != SCHEMA_VERSION:
        raise ProjectionLoadError("projection schema version is unsupported")
    if projection.get("study_id") != filename_study_id:
        raise ProjectionLoadError("projection identity does not match its filename")
    if not STUDY_ID_PATTERN.fullmatch(filename_study_id):
        raise ProjectionLoadError("projection identity is not a safe study identifier")
    required = (
        "schema_version",
        "study_id",
        "display_id",
        "title",
        "catalog_summary",
        "study_context",
        "presentation",
        "claims",
        "primary",
        "secondary",
        "clean_sentinels",
        "paired_blocks",
        "trials",
        "missingness",
        "provenance",
        "methods",
        "claim_boundary",
        "capability_card",
    )
    _keys(projection, "projection", required)
    for field_name in ("study_id", "display_id", "title", "catalog_summary"):
        if not isinstance(projection[field_name], str) or not projection[field_name]:
            raise ProjectionLoadError(f"projection {field_name} must be a non-empty string")
    _validate_nested_projection(projection)
    if json_bytes(projection) != projection_bytes:
        raise ProjectionLoadError("projection bytes are not in deterministic form")
    lowered = projection_bytes.decode("utf-8").lower()
    if any(prohibited in lowered for prohibited in PROHIBITED_PROJECTION_TEXT):
        raise ProjectionLoadError("projection contains prohibited private content")
    return projection


class DashboardStore:
    """Immutable startup snapshot of checked-in study projections."""

    def __init__(self, studies_dir: Path) -> None:
        self.study_bytes: dict[str, bytes] = {}
        self.unavailable: dict[str, str] = {}
        catalog_entries = []
        for study_path in sorted(studies_dir.glob("*.json")):
            study_id = study_path.stem
            try:
                projection_bytes = study_path.read_bytes()
                projection = _validate_projection(projection_bytes, study_id)
            except (OSError, ProjectionLoadError) as error:
                self.unavailable[study_id] = str(error)
                catalog_entries.append(
                    {
                        "study_id": study_id,
                        "display_id": study_id,
                        "title": "Study projection unavailable",
                        "summary": "The checked-in projection failed closed.",
                        "availability": "unavailable",
                    }
                )
                continue
            self.study_bytes[study_id] = projection_bytes
            catalog_entries.append(
                {
                    "study_id": study_id,
                    "display_id": projection["display_id"],
                    "title": projection["title"],
                    "summary": projection["catalog_summary"],
                    "availability": "available",
                    "claims": {
                        claim_name: {
                            "label": claim["label"],
                            "status": claim["status"],
                        }
                        for claim_name, claim in projection["claims"].items()
                    },
                }
            )
        study_count = len(catalog_entries)
        if study_count == 1:
            comparison_message = "One study is present; cross-study comparison is unavailable."
        elif study_count == 0:
            comparison_message = "No checked-in study projections are present."
        else:
            comparison_message = (
                f"{study_count} studies are present; no cross-study estimate is defined."
            )
        self.catalog_bytes = json_bytes(
            {
                "schema_version": SCHEMA_VERSION,
                "studies": catalog_entries,
                "comparison": {
                    "study_count": study_count,
                    "status": "unavailable",
                    "message": comparison_message,
                },
            }
        )

    def study_response(self, study_id: str) -> tuple[int, bytes]:
        if study_id in self.study_bytes:
            return 200, self.study_bytes[study_id]
        if study_id in self.unavailable:
            return 503, json_bytes(
                {
                    "schema_version": SCHEMA_VERSION,
                    "study_id": study_id,
                    "status": "unavailable",
                    "error": {
                        "code": "projection_unavailable",
                        "message": "The checked-in study projection failed validation.",
                    },
                }
            )
        return 404, json_bytes({"error": "study not found"})


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        application_root: Path,
        studies_dir: Path,
    ) -> None:
        self.application_bytes = {
            filename: (application_root / filename).read_bytes() for filename in STATIC_ASSETS
        }
        self.store = DashboardStore(studies_dir)
        super().__init__(address, DashboardHandler)


class DashboardHandler(BaseHTTPRequestHandler):
    server: DashboardServer
    protocol_version = "HTTP/1.1"

    def _send(
        self,
        status: int,
        content_type: str,
        payload: bytes,
        *,
        head_only: bool,
        allow: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        for header_name, header_value in SECURITY_HEADERS:
            self.send_header(header_name, header_value)
        if allow is not None:
            self.send_header("Allow", allow)
        self.end_headers()
        if not head_only:
            self.wfile.write(payload)

    def _send_json(self, status: int, payload: bytes, *, head_only: bool) -> None:
        self._send(
            status,
            "application/json; charset=utf-8",
            payload,
            head_only=head_only,
        )

    def _serve_file(self, filename: str, content_type: str, *, head_only: bool) -> None:
        payload = self.server.application_bytes[filename]
        self._send(200, content_type, payload, head_only=head_only)

    def _dispatch(self, *, head_only: bool) -> None:
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            self._serve_file("index.html", STATIC_ASSETS["index.html"], head_only=head_only)
            return
        if path == "/app.css":
            self._serve_file("app.css", STATIC_ASSETS["app.css"], head_only=head_only)
            return
        if path == "/app.js":
            self._serve_file("app.js", STATIC_ASSETS["app.js"], head_only=head_only)
            return
        if path == "/api/studies":
            self._send_json(200, self.server.store.catalog_bytes, head_only=head_only)
            return
        prefix = "/api/studies/"
        if path.startswith(prefix):
            study_id = path[len(prefix) :]
            if not STUDY_ID_PATTERN.fullmatch(study_id):
                self._send_json(404, json_bytes({"error": "study not found"}), head_only=head_only)
                return
            status, payload = self.server.store.study_response(study_id)
            self._send_json(status, payload, head_only=head_only)
            return
        if path == "/healthz":
            health = {
                "status": "ok" if not self.server.store.unavailable else "degraded",
                "available_studies": len(self.server.store.study_bytes),
                "unavailable_studies": len(self.server.store.unavailable),
            }
            status = 200 if not self.server.store.unavailable else 503
            self._send_json(status, json_bytes(health), head_only=head_only)
            return
        self._send_json(404, json_bytes({"error": "resource not found"}), head_only=head_only)

    def do_GET(self) -> None:
        self._dispatch(head_only=False)

    def do_HEAD(self) -> None:
        self._dispatch(head_only=True)

    def _method_not_allowed(self) -> None:
        self._send(
            405,
            "application/json; charset=utf-8",
            json_bytes({"error": "method not allowed"}),
            head_only=False,
            allow="GET, HEAD",
        )

    def do_POST(self) -> None:
        self._method_not_allowed()

    def do_PUT(self) -> None:
        self._method_not_allowed()

    def do_PATCH(self) -> None:
        self._method_not_allowed()

    def do_DELETE(self) -> None:
        self._method_not_allowed()

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(
    address: tuple[str, int],
    *,
    application_root: Path,
    studies_dir: Path | None = None,
) -> DashboardServer:
    try:
        bind_address = ipaddress.ip_address(address[0])
    except ValueError as error:
        raise ValueError("dashboard bind address must be a literal loopback IP") from error
    if not bind_address.is_loopback:
        raise ValueError("dashboard may bind only to a loopback address")
    resolved_studies_dir = studies_dir or application_root / "studies"
    return DashboardServer(address, application_root, resolved_studies_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the CAPLAB results dashboard")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3021)
    parser.add_argument("--application-root", type=Path, default=Path(__file__).resolve().parent)
    arguments = parser.parse_args(argv)
    server = create_server(
        (arguments.bind, arguments.port),
        application_root=arguments.application_root.resolve(),
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
