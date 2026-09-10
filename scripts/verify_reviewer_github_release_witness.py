#!/usr/bin/env python3
"""Check recorded HTTP inputs separately from the desired release outcome."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import urllib.parse


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_slot(root: Path, role: str, condition: str, repetition: int) -> dict:
    plan = json.loads((root / "plan.json").read_text())
    assert sha(root / "criteria.json") == plan["criteria_sha256"], "criteria drift"
    criteria = json.loads((root / "criteria.json").read_text())
    slot = root / f"{role}-{condition}-{repetition}"
    launch = json.loads((slot / "launch.json").read_text())
    result = json.loads((slot / "completion.json").read_text())
    assert launch["plan_sha256"] == sha(root / "plan.json"), "launch plan mismatch"
    assert result["returncode"] == 0 and result["termination"] == "exit", "process did not complete"
    for name in ("stdout", "stderr"):
        assert sha(slot / name) == result[name + "_sha256"], "output hash mismatch"
    output = json.loads((slot / "stdout").read_text())
    assert output["condition"] == condition, "condition mismatch"
    defaults = criteria["default_scans"][role]
    search_count = len(defaults["TOPICS"]) + len(defaults["VELOCITY_TOPICS"])
    release_repos = defaults["RELEASE_REPOS"] if condition == "ordinary" else defaults["RELEASE_REPOS"][:1]
    requests = output["requests"]
    assert len(requests) == search_count + len(release_repos), "request count mismatch"
    for request in requests:
        assert request["status"] == 200 and request["host"] == "api.github.com", "fixture not reached successfully"
        assert request["authorization_present"] is False, "unexpected credential"
    for request, topic in zip(requests[:search_count], defaults["TOPICS"] + defaults["VELOCITY_TOPICS"], strict=True):
        url = urllib.parse.urlsplit(request["path"])
        params = urllib.parse.parse_qs(url.query)
        assert url.path == "/search/repositories" and params["q"][0].startswith(f"topic:{topic} "), "wrong search path"
        assert request["remaining"] == "50" and request["body"] == {"items": []}, "search fixture mismatch"
    published = datetime.fromisoformat(output["published_at"])
    observed_now = published + timedelta(hours=1)
    assert launch["started_at"] <= observed_now.timestamp() <= launch["started_at"] + result["elapsed_seconds"] + 1, "publication clock outside process"
    for request, repo in zip(requests[search_count:], release_repos, strict=True):
        assert request["path"] == f"/repos/{repo}/releases?per_page=3", "wrong release path"
        assert request["remaining"] == ("50" if condition == "ordinary" else "1"), "wrong quota"
        body = request["body"]
        eligible_repo = repo in defaults["RELEASE_REPOS"][:2]
        if condition == "low-empty" or not eligible_repo:
            assert body == [], "empty control contains a release"
        else:
            assert len(body) == 1 and body[0]["draft"] is (condition == "low-draft"), "draft condition mismatch"
            assert body[0]["prerelease"] is False and body[0]["published_at"] == output["published_at"], "release eligibility mismatch"
            assert body[0]["html_url"] == f"https://github.com/{repo}/releases/tag/v1.0.0", "release identity mismatch"
    assert output["state"]["repos"] == {}, "unexpected baseline contents"
    saved = datetime.fromisoformat(output["state"]["last_run"]).timestamp()
    assert launch["started_at"] <= saved <= launch["started_at"] + result["elapsed_seconds"] + 1, "state not updated in process"
    actual = sorted(article["url"] for article in output["articles"])
    for article in output["articles"]:
        assert article["source_class"] == "github" and article["source_name"] == "GitHub/Releases", "wrong article kind"
        assert article["published_at"] == output["published_at"], "wrong article date"
    expected = sorted(criteria[condition]["article_urls"])
    satisfies = actual == expected
    predicted = not (role in {"introduction", "base"} and condition == "low-eligible")
    return {"slot": slot.name, "administration_valid": True, "satisfies_preservation_or_control": satisfies,
            "matches_predicted_contrast": satisfies == predicted,
            "expected_article_urls": expected, "actual_article_urls": actual,
            "request_count": len(requests), "elapsed_seconds": result["elapsed_seconds"],
            "files": {name: sha(slot / name) for name in ("launch.json", "process.json", "completion.json", "stdout", "stderr")}}


def verify(root: Path) -> dict:
    plan = json.loads((root / "plan.json").read_text())
    rows = [check_slot(root, role, condition, repetition) for role in plan["snapshots"]
            for condition in plan["conditions"] for repetition in range(1, plan["repetitions"] + 1)]
    expected = {row["slot"] for row in rows} | {"preflight"}
    assert {p.parent.name for p in root.glob("*/launch.json")} == expected, "unexpected or missing launches"
    preflight = json.loads((root / "preflight/completion.json").read_text())
    assert preflight["returncode"] == 0 and preflight["termination"] == "exit", "preflight failed"
    for role, snapshot in plan["snapshots"].items():
        for entry in snapshot["files"]:
            assert sha(root / role / entry["path"]) == entry["sha256"], "source drift"
    for entry in plan["fixture"] + plan["runtime"]:
        assert sha(Path(entry["path"])) == entry["sha256"], "runtime or fixture drift"
    assert sum(row["elapsed_seconds"] for row in rows) + preflight["elapsed_seconds"] <= plan["total_seconds"], "budget exceeded"
    return {"schema": "caplab.github-release-preservation-verification/v1", "custody_root": str(root),
            "plan_sha256": sha(root / "plan.json"), "criteria_sha256": sha(root / "criteria.json"),
            "verifier_sha256": sha(Path(__file__)), "observations": rows,
            "all_administrations_valid": True, "all_contrasts_as_predicted": all(row["matches_predicted_contrast"] for row in rows),
            "source_and_runtime_hashes_unchanged": True,
            "interpretation": "One development defect family; no reviewer score, whole-change clean label or ranking"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
