#!/usr/bin/env python3
"""Generate the local review-capability leaderboard (static HTML).

Reads the claims ledger, the contrast documents, the promotion gate, and —
when the quartermaster repo is present — the derived projection, and writes
one self-contained HTML file. No external assets, no network, no publishing:
the page is a repo artifact viewed locally (file:// or a local server).

The page's first rule is the campaign's: numbers compare only within one
instrument, one custody class, and one case seed. There is deliberately no
single all-Bindings ranking — cohorts are ranked internally and never
merged. Within a cohort the newest, widest claim per Binding is shown.
"""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from caplab.advisory.discrimination import promotion_candidates  # noqa: E402
from caplab.advisory.executor import advisory_control_context    # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "docs", "leaderboard", "index.html")
QUARTERMASTER = os.path.expanduser("~/git/quartermaster")

#: Two-way defect-class grouping for the split columns. STRUCTURAL defects
#: remove, corrupt, or mis-reference content (detection = noticing what is
#: absent or inconsistent in form); SEMANTIC defects assert something false
#: (detection = reading claims against content). The split is reported
#: because a scalar hid it: one subject measured 7/7 semantic against 0/5
#: structural inside a 0.042 aggregate.
STRUCTURAL = {"dropped_section", "truncated_tail", "duplicated_section",
              "swapped_section_bodies", "hollow_delivery", "base_dropped",
              "dangling_reference", "broken_internal_crossref",
              "hash_mismatch", "decorative_check"}
SEMANTIC = {"contradicted_clause", "refuted_conclusion",
            "requirement_inversion", "overclaimed_level", "scope_violation",
            "unearned_verification_claim"}
RUN_ROOTS = [
    os.path.join(REPO, "advisory", "pool-runs"),
    os.path.join(REPO, "advisory", "runs"),
    os.path.expanduser("~/git/striatum-tuner/eval-runs"),
]
BACKENDS_ROOT = os.path.expanduser("~/git/striatum-next/backends")


def declared_identity(binding_id: str) -> tuple[str | None, str | None]:
    """(model, harness) from the binding's declaration.

    The model pin keeps a terse historical id ('glm', 'local-qwen') from
    reading as a different model's row. The harness label carries the
    affordance difference the structural split turns on: an agentic harness
    can enumerate and compute over an artifact; a one-shot lane can only
    read the prompt it was handed.
    """
    path = os.path.join(BACKENDS_ROOT, binding_id, "backend.yaml")
    if not os.path.isfile(path):
        return None, None
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            declaration = yaml.safe_load(f)
        command = ((declaration.get("adapter") or {}).get("command")) or []
        model = None
        for flag in ("-model", "--model"):
            if flag in command:
                model = str(command[command.index(flag) + 1])
        joined = " ".join(str(c) for c in command)
        if "striatum-openai-lane" in joined:
            harness = "lane · no tools"
        elif " codex " in f" {joined} " or "codex exec" in joined:
            harness = "codex · tools"
        elif " agy " in f" {joined} ":
            harness = "agy · tools"
        elif " claude " in f" {joined} " or "claude -p" in joined:
            harness = "claude-code · tools"
        elif "opencode" in joined:
            harness = "opencode · tools"
        else:
            harness = None
        return model, harness
    except Exception:
        return None, None

PROMOTION_CONTRASTS = [
    "gemini-3-7-flash-high-vs-medium-20260817.json",
    "gemini-3-7-flash-high-vs-medium-20260819.json",
    "gemini-3-7-flash-high-vs-medium-20260820-replay.json",
    "sol-high-vs-flash-high-20260819.json",
    "sol-high-vs-flash-medium-20260819.json",
]

#: Contrast verdicts amended by a written erratum. The record named is the
#: source of truth; the page must not show a headline a record has withdrawn.
ERRATA = {
    ("codex-sol-high", "agy-gemini-3-7-flash-high", "20260819"):
        ("WITHDRAWN — clean-contract cases only: 6–1, p=0.125 (erratum "
         "2026-08-22: v1-changeset quarantine)"),
    ("agy-gemini-3-7-flash-high", "agy-gemini-3-7-flash-medium", "20260819"):
        ("clean-contract cases only: 5–0, p=0.062 (marginal; per-cell "
         "reproduction unaffected — erratum 2026-08-22)"),
}
#: Synthetic-contract claims whose sweeps predate the v2 change-set contract
#: carry v1-changeset rows (~35% of breadth) and wear a contamination badge.
V2_CUTOVER = "2026-08-22"


def load_claims():
    claims = []
    with open(os.path.join(REPO, "advisory", "claims.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                claims.append(json.loads(line))
    rows = []
    for c in claims:
        if c.get("construct", "review.defect_discrimination/1") \
                != "review.defect_discrimination/1":
            continue
        m = c.get("metrics", {})

        def val(key):
            entry = m.get(key)
            return entry.get("value") if isinstance(entry, dict) else None

        seeds, instruments, pairs = set(), set(), 0
        for e in c.get("evidence", []):
            if isinstance(e, dict):
                if e.get("sweep_seed"):
                    seeds.add(str(e["sweep_seed"]))
                if e.get("instrument"):
                    instruments.add(e["instrument"])
                pairs += e.get("rows_used") or 0
        fa = m.get("false_alarm_rate") or {}
        split = {"structural": [0, 0], "semantic": [0, 0]}
        for e in c.get("evidence", []):
            run = e.get("run") if isinstance(e, dict) else None
            if not run:
                continue
            for root in RUN_ROOTS:
                path = os.path.join(root, run, "results.jsonl")
                if not os.path.isfile(path):
                    continue
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        if not row.get("usable") or row.get("anchor"):
                            continue
                        group = ("structural"
                                 if row.get("defect_class") in STRUCTURAL
                                 else "semantic"
                                 if row.get("defect_class") in SEMANTIC
                                 else None)
                        if group:
                            split[group][1] += 1
                            split[group][0] += bool(row.get("caught"))
                break
        rows.append({
            "subject": c["subject"]["source_id"],
            "as_of": c["as_of"][:10],
            "custody": c.get("custody"),
            "seed": ",".join(sorted(seeds)) or "?",
            "instrument": ("synthetic-contract"
                           if any("synthetic" in i for i in instruments)
                           else "dispatch-prompt"),
            "pairs": pairs,
            "catch": val("catch_rate"),
            "fa": val("false_alarm_rate"),
            "disc": val("discrimination"),
            "anchored": val("anchored_detection"),
            "fa_unaudited": (fa.get("unaudited_refusals")
                             if isinstance(fa, dict) else None),
            "fa_audit": (fa.get("audit_status")
                         if isinstance(fa, dict) else None),
            "structural": tuple(split["structural"]),
            "semantic": tuple(split["semantic"]),
        })
    return rows


def best_per_binding(rows):
    """Newest, widest claim per Binding within one cohort."""
    keep = {}
    for r in rows:
        cur = keep.get(r["subject"])
        if cur is None or (r["pairs"], r["as_of"]) > (cur["pairs"], cur["as_of"]):
            keep[r["subject"]] = r
    return sorted(keep.values(), key=lambda r: -(r["disc"] or -9))


def load_contrasts():
    out = []
    comp = os.path.join(REPO, "advisory", "comparisons")
    for name in sorted(os.listdir(comp)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(comp, name), encoding="utf-8") as f:
            d = json.load(f)
        out.append(d)
    return out


def all_projections(limit=10):
    """Every objective spec in the quartermaster registry, projected."""
    import glob as _glob
    if not os.path.isdir(QUARTERMASTER):
        return []
    env = dict(os.environ, PYTHONPATH=os.path.join(QUARTERMASTER, "src"))
    out = []
    for path in sorted(_glob.glob(os.path.join(
            QUARTERMASTER, "objectives", "**", "*.json"), recursive=True)):
        try:
            raw = subprocess.run(
                [sys.executable, "-m", "quartermaster", "project",
                 "--objective", path],
                capture_output=True, text=True, cwd=QUARTERMASTER, env=env,
                timeout=60)
            if raw.returncode != 0:
                continue
            p = json.loads(raw.stdout)
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
            construct = next(iter(spec.get("constructs") or {}), "?")
            ranked = []
            for e in p.get("ranked", [])[:limit]:
                c = next(iter(e["constructs"].values()), {})
                ranked.append({"rank": e.get("rank"),
                               "label": e.get("label"),
                               "score": c.get("score"),
                               "custody": c.get("custody"),
                               "seeds": ",".join(c.get("case_sets") or []),
                               "n": c.get("n")})
            if not ranked:
                continue
            out.append({
                "name": os.path.splitext(os.path.basename(path))[0],
                "construct": construct,
                "status": spec.get("status", ""),
                "lead": (p.get("lead_comparability") or {}).get("reading", ""),
                "ranked": ranked,
                "total": len(p.get("ranked") or []),
                "excluded": len(p.get("excluded") or []),
            })
        except Exception:
            continue
    order = {"review": 0, "build": 1}
    out.sort(key=lambda o: (order.get(o["name"], 2), o["name"]))
    return out


def esc(x):
    return html.escape(str(x))


def pct(x):
    return "—" if x is None else f"{100 * x:.0f}%"


def bar(value, kind="disc"):
    """Inline magnitude bar. Discrimination spans [-1, 1]; rates span [0, 1]."""
    if value is None:
        return '<span class="muted">—</span>'
    if kind == "disc":
        width = max(0.0, min(1.0, (value + 1) / 2)) * 100
        label = f"{value:+.2f}"
    else:
        width = max(0.0, min(1.0, value)) * 100
        label = pct(value)
    return (f'<span class="bar" title="{esc(label)}">'
            f'<span class="bar-fill bar-{kind}" style="width:{width:.0f}%"></span>'
            f'</span><span class="bar-label">{esc(label)}</span>')


def claim_badges(r):
    badges = []
    if (r["instrument"] == "synthetic-contract" and r["as_of"] < V2_CUTOVER):
        badges.append('<span class="badge badge-warn" title="~35% of breadth '
                      'cases ran the quarantined v1 change-set contract — see '
                      'erratum 2026-08-22">⚠ v1-changeset rows</span>')
    if r["fa_audit"] == "contains-unaudited-refusals":
        n = r["fa_unaudited"]
        badges.append(f'<span class="badge badge-note" title="false-alarm rate '
                      f'is an upper bound until the control audit clears">'
                      f'◌ {esc(n)} unaudited FA</span>')
    return " ".join(badges)


def split_cell(hit_total):
    hits, total = hit_total
    if not total:
        return '<span class="muted">—</span>'
    frac = hits / total
    return (f'<span class="bar bar-narrow" title="{hits}/{total} caught">'
            f'<span class="bar-fill bar-rate" style="width:{frac * 100:.0f}%">'
            f'</span></span><span class="bar-label">{hits}/{total}</span>')


def cohort_table(rows):
    out = ['<table><thead><tr><th>Binding</th>'
           '<th title="agentic harness (workspace + shell) vs one-shot '
           'completion lane (no tools)">harness</th><th>pairs</th>'
           '<th>catch</th><th>false alarms</th><th>discrimination</th>'
           '<th title="structural defects caught / measured">structural</th>'
           '<th title="semantic defects caught / measured">semantic</th>'
           '<th>anchored</th><th>as of</th><th>flags</th></tr></thead><tbody>']
    for r in rows:
        model, harness = declared_identity(r["subject"])
        model_note = (f'<br><span class="model-note">{esc(model)}</span>'
                      if model and model.lower() not in r["subject"].lower()
                      else "")
        out.append(
            f'<tr><td class="name">{esc(r["subject"])}{model_note}</td>'
            f'<td class="harness">{esc(harness) if harness else "—"}</td>'
            f'<td class="num">{esc(r["pairs"])}</td>'
            f'<td>{bar(r["catch"], "rate")}</td>'
            f'<td>{bar(r["fa"], "fa")}</td>'
            f'<td>{bar(r["disc"], "disc")}</td>'
            f'<td>{split_cell(r["structural"])}</td>'
            f'<td>{split_cell(r["semantic"])}</td>'
            f'<td class="num">{pct(r["anchored"])}</td>'
            f'<td class="num">{esc(r["as_of"])}</td>'
            f'<td>{claim_badges(r)}</td></tr>')
    out.append("</tbody></table>")
    return "\n".join(out)


def contrast_rows(contrasts):
    out = []
    for d in contrasts:
        if "discordant_pairs" not in d:
            continue
        seed = str(d.get("sweep_seed") or "?")
        key = (d["a"], d["b"], seed)
        note = ERRATA.get(key, "")
        verdict = ("separates" if d.get("significant_at_05") else "not established")
        if d.get("case_selection") == "targeted-reproduction":
            verdict = "targeted reproduction (gate, not discovery)"
        if key in ERRATA and "WITHDRAWN" in ERRATA[key]:
            verdict = "withdrawn"
        out.append({
            "a": d["a"], "b": d["b"], "seed": seed,
            "shared": d.get("shared_cases"),
            "disc": f'{d.get("a_only_caught")}–{d.get("b_only_caught")}',
            "p": d.get("sign_test_p"),
            "verdict": verdict, "note": note,
        })
    out.sort(key=lambda r: (r["seed"], r["a"], r["b"]))
    return out


def main() -> int:
    claims = load_claims()
    contrasts = load_contrasts()
    adjudications, sources = advisory_control_context()
    gate_docs = []
    for name in PROMOTION_CONTRASTS:
        path = os.path.join(REPO, "advisory", "comparisons", name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                gate_docs.append(json.load(f))
    promotion = promotion_candidates(gate_docs, adjudications,
                                     substrate_sources=sources)
    projections = all_projections()
    generated = max((r["as_of"] for r in claims), default="?")

    cohorts = {}
    for r in claims:
        cohorts.setdefault(
            (r["custody"], r["instrument"], r["seed"]), []).append(r)

    def cohort_sort_key(item):
        (custody, instrument, seed), _ = item
        return (custody != "caplab-advisory", instrument, seed != "20260819",
                seed)

    sections = []
    for (custody, instrument, seed), rows in sorted(cohorts.items(),
                                                    key=cohort_sort_key):
        rows = best_per_binding(rows)
        sections.append(
            f"<section><h2>{esc(custody)} · {esc(instrument)} · seed "
            f"{esc(seed)}</h2>\n{cohort_table(rows)}</section>")

    contrast_html = ['<table><thead><tr><th>contrast</th><th>seed</th>'
                     '<th>shared</th><th>discordance</th><th>p</th>'
                     '<th>verdict</th><th>note</th></tr></thead><tbody>']
    for r in contrast_rows(contrasts):
        cls = ("withdrawn" if r["verdict"] == "withdrawn"
               else "sig" if r["verdict"] == "separates" else "")
        contrast_html.append(
            f'<tr class="{cls}"><td class="name">{esc(r["a"])} vs '
            f'{esc(r["b"])}</td><td class="num">{esc(r["seed"])}</td>'
            f'<td class="num">{esc(r["shared"])}</td>'
            f'<td class="num">{esc(r["disc"])}</td>'
            f'<td class="num">{"—" if r["p"] is None else f"{r[chr(112)]:.3f}"}</td>'
            f'<td>{esc(r["verdict"])}</td><td class="note">{esc(r["note"])}</td></tr>')
    contrast_html.append("</tbody></table>")

    promoted_html = ['<table><thead><tr><th>substrate</th><th>defect class</th>'
                     '<th>pair</th><th>sweeps</th></tr></thead><tbody>']
    for p in promotion["promoted"]:
        promoted_html.append(
            f'<tr><td class="name">{esc(p["substrate_id"])}</td>'
            f'<td>{esc(p["defect_class"])}</td>'
            f'<td>{esc(p["pair"][0])} &gt; {esc(p["pair"][1])}</td>'
            f'<td class="num">{esc(", ".join(map(str, p["sweeps"])))}</td></tr>')
    promoted_html.append("</tbody></table>")
    quarantined = sum(1 for w in promotion["withheld"]
                      if "quarantined" in w["reason"])
    single = sum(1 for w in promotion["withheld"]
                 if "reproduction not established" in w["reason"])

    projection_html = ""
    if projections:
        parts = [
            "<section><h2>Quartermaster projections (all objectives)</h2>"
            '<p class="muted">One derived ranking per consumer objective '
            "spec — regenerable, never stored facts. Same-model tuples on "
            "different accounts or harnesses are distinct Bindings and rank "
            "separately by design. The review objective pins the "
            "synthetic-contract instrument; Tier B objectives rank "
            "PRODUCERS under independent-family review (model-relative "
            "labels, reviewer-mix confound noted on the claims); draft "
            "objectives await consumer ratification.</p>"]
        for proj in projections:
            parts.append(
                f'<h3 style="font-size:.95rem;margin:1.2rem 0 .2rem">'
                f'{esc(proj["name"])} <span class="muted" '
                f'style="font-weight:400">— {esc(proj["construct"])}'
                f'{" · " + esc(proj["status"]) if proj["status"] else ""}'
                f'</span></h3>')
            if proj["lead"]:
                parts.append(f'<p class="muted" style="font-size:.85rem">'
                             f'{esc(proj["lead"])}</p>')
            rows_html = ['<table><thead><tr><th>rank</th><th>Binding</th>'
                         '<th>harness</th><th>score</th><th>custody</th>'
                         '<th>seed</th><th>n</th></tr></thead><tbody>']
            for e in proj["ranked"]:
                score = "—" if e["score"] is None else f'{e["score"]:.3f}'
                model, harness = declared_identity(e["label"])
                model_note = (
                    f'<br><span class="model-note">{esc(model)}</span>'
                    if model and model.lower() not in e["label"].lower()
                    else "")
                rows_html.append(
                    f'<tr><td class="num">{esc(e["rank"])}</td>'
                    f'<td class="name">{esc(e["label"])}{model_note}</td>'
                    f'<td class="harness">'
                    f'{esc(harness) if harness else "—"}</td>'
                    f'<td class="num">{score}</td><td>{esc(e["custody"])}</td>'
                    f'<td class="num">{esc(e["seeds"])}</td>'
                    f'<td class="num">{esc(e["n"])}</td></tr>')
            rows_html.append("</tbody></table>")
            shown = len(proj["ranked"])
            if proj["total"] > shown or proj["excluded"]:
                rows_html.append(
                    f'<p class="muted" style="font-size:.82rem">showing '
                    f'{shown} of {proj["total"]} ranked; '
                    f'{proj["excluded"]} below floors.</p>')
            parts.append("\n".join(rows_html))
        parts.append("</section>")
        projection_html = "\n".join(parts)

    production = {}
    for line in open(os.path.join(REPO, "advisory", "claims.jsonl"),
                     encoding="utf-8"):
        if not line.strip():
            continue
        c = json.loads(line)
        construct = c.get("construct") or ""
        if construct.startswith("review.defect_discrimination"):
            continue
        m = c["metrics"]
        primary = next((k, v) for k, v in m.items() if k != "n_pairs")
        production.setdefault(construct, []).append(
            (c["subject"]["source_id"], primary[1].get("value"),
             primary[1].get("denominator"), primary[0],
             (m.get("delivery_rate") or {}).get("value")
             if construct == "build.packet_delivery/1" else None))
    build_rows = [(s_, pv, pn, dv) for (s_, pv, pn, _k, dv)
                  in production.pop("build.packet_delivery/1", [])]
    tier_a_html = []
    for construct, rows_ in sorted(production.items()):
        rows_ = [r for r in rows_ if r[2]]
        if not rows_:
            continue
        rows_.sort(key=lambda r: -(r[1] or 0))
        metric = rows_[0][3]
        if len(rows_) == 1:
            s_, pv, pn, _k, _d = rows_[0]
            tier_a_html.append(
                f'<p class="muted"><strong>{esc(construct)}</strong> — '
                f'single production subject: {esc(s_)} {pct(pv)} '
                f'{esc(metric)} (n={esc(pn)}).</p>')
            continue
        cells = [f'<h3 style="font-size:.95rem;margin:1rem 0 .3rem">'
                 f'{esc(construct)}</h3>'
                 '<table><thead><tr><th>Binding</th><th>harness</th>'
                 f'<th>{esc(metric)}</th><th>n</th></tr></thead><tbody>']
        for s_, pv, pn, _k, _d in rows_:
            model, harness = declared_identity(s_)
            dim = ' style="opacity:.55"' if pn < 10 else ""
            cells.append(
                f'<tr{dim}><td class="name">{esc(s_)}</td>'
                f'<td class="harness">{esc(harness) if harness else "—"}</td>'
                f'<td>{bar(pv, "rate")}</td><td class="num">{esc(pn)}</td></tr>')
        cells.append("</tbody></table>")
        tier_a_html.append("\n".join(cells))
    build_html = ""
    if build_rows:
        build_rows.sort(key=lambda r: -(r[1] or 0) * (1 if (r[2] or 0) >= 10 else 0.001))
        cells = ['<table><thead><tr><th>Binding</th><th>harness</th>'
                 '<th>checks-pass</th><th>n</th><th>delivery</th>'
                 '</tr></thead><tbody>']
        for subject, pv, pn, dv in build_rows:
            if not pn:
                continue
            model, harness = declared_identity(subject)
            model_note = (f'<br><span class="model-note">{esc(model)}</span>'
                          if model and model.lower() not in subject.lower()
                          else "")
            dim = ' style="opacity:.55"' if pn < 10 else ""
            cells.append(
                f'<tr{dim}><td class="name">{esc(subject)}{model_note}</td>'
                f'<td class="harness">{esc(harness) if harness else "—"}</td>'
                f'<td>{bar(pv, "rate")}</td><td class="num">{esc(pn)}</td>'
                f'<td class="num">{pct(dv)}</td></tr>')
        cells.append("</tbody></table>")
        build_html = (
            "<section><h2>Build construct (production harvest)</h2>"
            '<p class="muted">build.packet_delivery/1 — mechanical '
            'packet-checks label from the striatum production ledger, '
            'custody striatum-production. Tree-moved base churn (64% of '
            'raw failures) and capacity deferrals are excluded, never '
            'scored. Dimmed rows sit below the n≥10 floor. A separate '
            'construct from review: rank on one, never both.</p>'
            + "\n".join(cells)
            + '<h2 style="margin-top:1.6rem">Other production constructs '
              '(Tier A harvest)</h2>'
              '<p class="muted">Per-pass delivery and mechanical gate rates, '
              'custody striatum-production. Deferrals excluded; dimmed rows '
              'below n=10. Verification, intent-capture, packetization and '
              'integration run on the deterministic local backend in '
              'production — one subject is the honest answer there.</p>'
            + "\n".join(tier_a_html) + "</section>")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CAPLAB Review Leaderboard</title>
<style>
:root {{
  color-scheme: light;
  --surface: #fcfcfb; --surface-2: #f1f0ee;
  --ink: #0b0b0b; --ink-2: #52514e; --ink-3: #8a8880;
  --bar-rate: #2a78d6; --bar-fa: #eb6834; --bar-disc: #1baf7a;
  --sig: #008300; --warn-bg: #fdeaea; --warn-ink: #8f1f1e;
  --note-bg: #f1ead6; --note-ink: #6a5510; --line: #dedcd7;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --surface: #1a1a19; --surface-2: #242423;
    --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880;
    --bar-rate: #3987e5; --bar-fa: #d95926; --bar-disc: #199e70;
    --sig: #4dbb4d; --warn-bg: #3a1d1d; --warn-ink: #f0a9a8;
    --note-bg: #33301f; --note-ink: #e0c771; --line: #3a3a38;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --surface: #1a1a19; --surface-2: #242423;
  --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880;
  --bar-rate: #3987e5; --bar-fa: #d95926; --bar-disc: #199e70;
  --sig: #4dbb4d; --warn-bg: #3a1d1d; --warn-ink: #f0a9a8;
  --note-bg: #33301f; --note-ink: #e0c771; --line: #3a3a38;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0 auto; max-width: 1100px; padding: 2rem 1.2rem 4rem;
  background: var(--surface); color: var(--ink);
  font: 15px/1.5 system-ui, sans-serif; }}
h1 {{ font-size: 1.5rem; margin: 0 0 .3rem; }}
h2 {{ font-size: 1.05rem; margin: 2.2rem 0 .6rem; color: var(--ink);
  border-bottom: 1px solid var(--line); padding-bottom: .3rem; }}
.muted {{ color: var(--ink-2); }}
.rule {{ background: var(--surface-2); border-left: 3px solid var(--ink-3);
  padding: .6rem .9rem; margin: 1rem 0; color: var(--ink-2);
  font-size: .92rem; }}
table {{ border-collapse: collapse; width: 100%; font-size: .92rem; }}
th {{ text-align: left; color: var(--ink-2); font-weight: 600;
  border-bottom: 1px solid var(--line); padding: .3rem .5rem; }}
td {{ padding: .28rem .5rem; border-bottom: 1px solid var(--line);
  vertical-align: middle; }}
td.name {{ font-family: ui-monospace, monospace; font-size: .88rem; }}
.model-note {{ color: var(--ink-3); font-size: .78rem; }}
td.harness {{ color: var(--ink-2); font-size: .82rem; white-space: nowrap; }}
td.num {{ font-variant-numeric: tabular-nums; }}
td.note {{ color: var(--ink-2); font-size: .85rem; }}
tr.sig td {{ }}
tr.withdrawn td {{ color: var(--ink-3); text-decoration-color: var(--ink-3); }}
.bar-narrow {{ width: 54px; }}
.bar {{ display: inline-block; width: 90px; height: 8px;
  background: var(--surface-2); border-radius: 4px; overflow: hidden;
  vertical-align: middle; margin-right: .45rem; }}
.bar-fill {{ display: block; height: 100%; border-radius: 4px 0 0 4px; }}
.bar-rate {{ background: var(--bar-rate); }}
.bar-fa {{ background: var(--bar-fa); }}
.bar-disc {{ background: var(--bar-disc); }}
.bar-label {{ font-variant-numeric: tabular-nums; font-size: .88rem; }}
.badge {{ display: inline-block; border-radius: 4px; padding: 0 .4rem;
  font-size: .78rem; white-space: nowrap; }}
.badge-warn {{ background: var(--warn-bg); color: var(--warn-ink); }}
.badge-note {{ background: var(--note-bg); color: var(--note-ink); }}
footer {{ margin-top: 3rem; color: var(--ink-3); font-size: .85rem; }}
</style></head><body>
<h1>CAPLAB review-capability leaderboard</h1>
<p class="muted">Construct <code>review.defect_discrimination/1</code> ·
generated from the claims ledger, newest evidence {esc(generated)} ·
local page, not published.</p>
<div class="rule"><strong>Comparability rule.</strong> Numbers compare only
within one instrument, one custody class, and one case seed — each section
below is one such cohort, ranked internally by discrimination
(catch − false alarms). There is deliberately no merged ranking. Newest,
widest claim per Binding shown; hover bars for values.
<br><strong>Split columns.</strong> <em>structural</em> = defects that
remove, corrupt, or mis-reference content (dropped/truncated/duplicated/
swapped sections, hollow delivery, dropped base, dangling reference, broken
crossref, hash mismatch); <em>semantic</em> = defects that assert something
false (contradicted clause, refuted conclusion, requirement inversion,
overclaimed level, scope violation, unearned verification). Reported
because a scalar hides it: one subject measured 7/7 semantic against 0/5
structural inside a 0.042 aggregate.
<br><strong>Emission caveat.</strong> The binary false-alarm metric rewards silence: a subject emitting near-zero findings scores a spotless FA for the wrong reason (finding: fa-rewards-silence, 2026-08-22). Read <em>anchored</em> first when comparing across emission styles.</div>
{"".join(sections)}
<section><h2>Matched contrasts</h2>
<p class="muted">Paired sign tests on shared cases. Withdrawn or amended
verdicts follow their errata, not their original headlines.</p>
{"".join(contrast_html)}</section>
<section><h2>Promoted discrimination corpus
({len(promotion["promoted"])} cells)</h2>
<p class="muted">Cells that separated the same pair in the same direction in
two independent sweeps, on adjudicated-sound controls, under clean
contracts. Withheld: {single} at one sweep, {quarantined} quarantined
(v1-changeset contract — erratum 2026-08-22).</p>
{"".join(promoted_html)}</section>
{projection_html}
{build_html}
<footer>Regenerate: <code>python3 scripts/build_leaderboard.py</code> ·
records in <code>docs/records/</code> ·
erratum: <code>erratum-2026-08-22-changeset-contract-quarantine.md</code>
</footer>
</body></html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT} ({len(page)} bytes; {len(claims)} claims, "
          f"{len(cohorts)} cohorts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
