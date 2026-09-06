#!/usr/bin/env python3
"""Generate the local CAPLAB capability board (static HTML).

Reads the claims ledger, the run rows behind the claims, the matched
contrasts, the control adjudications, the striatum declarations, the
planning runs, the production-fate harvest and — when the quartermaster repo
is present — the derived projections, and writes one self-contained HTML
file. No external assets, no network, no publishing: the page is a repo
artifact viewed locally.

What the page is for: a reader who has to decide something about a binding
should find, in this order, (1) where every measured binding stands today on
the one comparable review cohort, with intervals and audit status; (2) which
pairwise separations are established and which are not; (3) what each binding
catches and misses, by defect class; (4) what striatum currently declares
about it, beside what was measured; (5) the planning gate, presented as the
gate it is; (6) the production fate covariate. Everything historical or
derived is below a fold.

The comparability rule is unchanged: numbers compare only within one
instrument, one custody class, one case seed, and one execution environment.
The page never merges cohorts; it chooses one to put first.
"""

from __future__ import annotations

import datetime as _dt
import glob as _glob
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
BACKENDS_ROOT = os.path.expanduser("~/git/striatum-next/backends")
FATE = os.path.join(REPO, "advisory", "pool-runs", "planning-production-fate-20260904", "summary.json")

#: The cohort that answers "where does this binding stand today": the latest
#: environment version on the seed every current subject shares. Change this
#: when a new environment or seed becomes the one new bindings are measured on.
CURRENT_COHORT = ("caplab-advisory", "synthetic-contract", "20260819", "iso-v1")

#: Two-way defect-class grouping. STRUCTURAL defects remove, corrupt, or
#: mis-reference content (detection = noticing what is absent or inconsistent
#: in form); SEMANTIC defects assert something false (detection = reading
#: claims against content). Reported because a scalar hid it: one subject
#: measured 7/7 semantic against 0/5 structural inside a 0.042 aggregate.
STRUCTURAL = ["hash_mismatch", "base_dropped", "dropped_section", "hollow_delivery",
              "truncated_tail", "duplicated_section", "swapped_section_bodies",
              "dangling_reference", "broken_internal_crossref", "decorative_check"]
SEMANTIC = ["contradicted_clause", "refuted_conclusion", "requirement_inversion",
            "overclaimed_level", "scope_violation", "unearned_verification_claim"]
RUN_ROOTS = [
    os.path.join(REPO, "advisory", "pool-runs"),
    os.path.join(REPO, "advisory", "runs"),
    os.path.expanduser("~/git/striatum-tuner/eval-runs"),
]
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
V2_CUTOVER = "2026-08-22"


# ------------------------------------------------------------------ helpers

def esc(x):
    return html.escape(str(x))


def pct(x, digits=0):
    return "—" if x is None else f"{100 * x:.{digits}f}%"


def load_yaml(path):
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def declaration(binding_id: str) -> dict:
    """What striatum currently declares about a binding: identity + review class."""
    path = os.path.join(BACKENDS_ROOT, binding_id, "backend.yaml")
    d = load_yaml(path) if os.path.isfile(path) else None
    if not d:
        return {"exists": False}
    command = ((d.get("adapter") or {}).get("command")) or []
    model = None
    for flag in ("-model", "--model"):
        if flag in command:
            model = str(command[command.index(flag) + 1])
    effort = None
    for flag in ("--effort", "-reasoning-effort-plain", "-reasoning-effort"):
        if flag in command:
            effort = str(command[command.index(flag) + 1])
    for c in command:
        if isinstance(c, str) and c.startswith("model_reasoning_effort="):
            effort = c.split("=", 1)[1]
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
    quality = d.get("quality") or {}
    caps = d.get("capabilities") or {}
    return {
        "exists": True, "model": model, "effort": effort, "harness": harness,
        "status": str(d.get("status") or "?"),
        "review_class": (quality.get("classes") or {}).get("review"),
        "basis": quality.get("basis"),
        "quality_as_of": str(quality.get("as_of") or ""),
        "review_admitted": "review" in (caps.get("supported_pass_types") or []),
        "aliasing": (d.get("aliasing") or {}).get("aliasing_class"),
    }


def declared_identity(binding_id: str):
    d = declaration(binding_id)
    return d.get("model"), d.get("harness")


def run_rows(run_name: str) -> list[dict]:
    for root in RUN_ROOTS:
        path = os.path.join(root, run_name, "results.jsonl")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return [json.loads(l) for l in f if l.strip()]
    return []


def load_claims():
    """Review claims, one row each, with the per-class detail from their runs."""
    with open(os.path.join(REPO, "advisory", "claims.jsonl"), encoding="utf-8") as f:
        claims = [json.loads(l) for l in f if l.strip()]
    rows = []
    for c in claims:
        if c.get("construct", "review.defect_discrimination/1") != "review.defect_discrimination/1":
            continue
        m = c.get("metrics", {})

        def val(key):
            entry = m.get(key)
            return entry.get("value") if isinstance(entry, dict) else None

        def ci(key):
            entry = m.get(key)
            return tuple(entry.get("ci95") or ()) if isinstance(entry, dict) else ()

        seeds, instruments, environments, pairs, runs = set(), set(), set(), 0, []
        for e in c.get("evidence", []):
            if isinstance(e, dict):
                if e.get("sweep_seed"):
                    seeds.add(str(e["sweep_seed"]))
                if e.get("instrument"):
                    instruments.add(e["instrument"])
                if e.get("environment"):
                    environments.add(e["environment"])
                pairs += e.get("rows_used") or 0
                if e.get("run"):
                    runs.append(e["run"])
        fa = m.get("false_alarm_rate") if isinstance(m.get("false_alarm_rate"), dict) else {}
        by_class: dict[str, list] = {}
        for run in runs:
            for row in run_rows(run):
                if not row.get("usable") or row.get("anchor"):
                    continue
                cls = row.get("defect_class")
                cell = by_class.setdefault(cls, [0, 0, 0])
                cell[1] += 1
                cell[0] += bool(row.get("caught"))
                cell[2] += bool(row.get("false_alarm"))
        split = {"structural": [0, 0], "semantic": [0, 0]}
        for cls, (caught, n, _) in by_class.items():
            group = "structural" if cls in STRUCTURAL else "semantic" if cls in SEMANTIC else None
            if group:
                split[group][0] += caught
                split[group][1] += n
        rows.append({
            "claim_id": c.get("claim_id"),
            "subject": c["subject"]["source_id"],
            "as_of": c["as_of"][:10],
            "as_of_full": c["as_of"],
            "custody": c.get("custody"),
            "seed": ",".join(sorted(seeds)) or "?",
            "instrument": ("synthetic-contract" if any("synthetic" in i for i in instruments)
                           else "dispatch-prompt"),
            "environment": (",".join(sorted(environments)) if environments else "(pre-isolation)"),
            "pairs": pairs, "runs": runs,
            "catch": val("catch_rate"), "catch_ci": ci("catch_rate"),
            "fa": val("false_alarm_rate"), "fa_ci": ci("false_alarm_rate"),
            "fa_denominator": fa.get("denominator"),
            "fa_excluded": fa.get("excluded_defective_controls"),
            "fa_unaudited": fa.get("unaudited_refusals"),
            "fa_audit": fa.get("audit_status"),
            "disc": val("discrimination"),
            "anchored": val("anchored_detection"),
            "structural": tuple(split["structural"]), "semantic": tuple(split["semantic"]),
            "by_class": by_class,
        })
    return rows


def best_per_binding(rows):
    """Newest, widest claim per Binding within one cohort."""
    keep = {}
    for r in rows:
        cur = keep.get(r["subject"])
        if cur is None or (r["pairs"], r["as_of_full"]) > (cur["pairs"], cur["as_of_full"]):
            keep[r["subject"]] = r
    return sorted(keep.values(), key=lambda r: -(r["disc"] if r["disc"] is not None else -9))


def load_contrasts():
    out = []
    comp = os.path.join(REPO, "advisory", "comparisons")
    for name in sorted(os.listdir(comp)):
        if name.endswith(".json"):
            with open(os.path.join(comp, name), encoding="utf-8") as f:
                d = json.load(f)
            d["_file"] = name
            out.append(d)
    return out


def load_planning():
    """Latest planning.finishability/1 claim per subject."""
    keep = {}
    with open(os.path.join(REPO, "advisory", "claims.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            if c.get("construct") != "planning.finishability/1":
                continue
            s = c["subject"]["source_id"]
            if s not in keep or c["as_of"] > keep[s]["as_of"]:
                keep[s] = c
    rows = []
    for s, c in keep.items():
        m = c["metrics"]
        g = lambda k: (m.get(k) or {}).get("value")  # noqa: E731
        rows.append({"subject": s, "finish": g("finishability_pass_rate"),
                     "ci": tuple((m.get("finishability_pass_rate") or {}).get("ci95") or ()),
                     "yield": g("graph_yield_rate"), "packets": g("median_packets"),
                     "dxw": g("median_depth_width_product"), "n": g("n_pairs"),
                     "as_of": c["as_of"][:10]})
    return sorted(rows, key=lambda r: (-(r["packets"] or 0), -(r["finish"] or 0)))


def all_projections(limit=10):
    if not os.path.isdir(QUARTERMASTER):
        return []
    env = dict(os.environ, PYTHONPATH=os.path.join(QUARTERMASTER, "src"))
    out = []
    for path in sorted(_glob.glob(os.path.join(QUARTERMASTER, "objectives", "**", "*.json"),
                                  recursive=True)):
        try:
            raw = subprocess.run([sys.executable, "-m", "quartermaster", "project",
                                  "--objective", path], capture_output=True, text=True,
                                 cwd=QUARTERMASTER, env=env, timeout=60)
            if raw.returncode != 0:
                continue
            p = json.loads(raw.stdout)
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
            construct = next(iter(spec.get("constructs") or {}), "?")
            ranked = []
            for e in p.get("ranked", [])[:limit]:
                c = next(iter(e["constructs"].values()), {})
                ranked.append({"rank": e.get("rank"), "label": e.get("label"),
                               "score": c.get("score"), "custody": c.get("custody"),
                               "seeds": ",".join(c.get("case_sets") or []), "n": c.get("n")})
            if ranked:
                out.append({"name": os.path.splitext(os.path.basename(path))[0],
                            "construct": construct, "status": spec.get("status", ""),
                            "lead": (p.get("lead_comparability") or {}).get("reading", ""),
                            "ranked": ranked, "total": len(p.get("ranked") or []),
                            "excluded": len(p.get("excluded") or [])})
        except Exception:
            continue
    order = {"review": 0, "build": 1}
    out.sort(key=lambda o: (order.get(o["name"], 2), o["name"]))
    return out


# ---------------------------------------------------------------- rendering

def short_name(binding: str) -> str:
    return binding


def identity_cell(binding: str) -> str:
    d = declaration(binding)
    bits = []
    if d.get("model") and d["model"].lower().replace(" ", "-") not in binding.lower():
        bits.append(esc(d["model"]))
    if d.get("harness"):
        bits.append(esc(d["harness"]))
    sub = f'<br><span class="sub">{" · ".join(bits)}</span>' if bits else ""
    return f'<span class="mono">{esc(binding)}</span>{sub}'


def audit_badge(r) -> str:
    if r.get("fa_audit") == "established":
        return '<span class="badge good" title="every control refusal is adjudicated">audited</span>'
    n = r.get("fa_unaudited")
    if r.get("fa_audit") == "contains-unaudited-refusals":
        return (f'<span class="badge note" title="false-alarm rate is an upper bound until '
                f'the remaining control refusals are adjudicated">{esc(n)} unaudited</span>')
    if r["instrument"] == "synthetic-contract" and r["as_of"] < V2_CUTOVER:
        return ('<span class="badge warn" title="~35% of breadth cases ran the quarantined '
                'v1 change-set contract (erratum 2026-08-22)">v1-changeset rows</span>')
    return '<span class="badge muted-badge" title="audit status not recorded on this claim">unaudited</span>'


def missing_from_current(claims, current) -> str:
    """Bindings measured on some cohort but not on the current one — named, so an
    absence reads as a gap in coverage rather than as a verdict."""
    on_board = {r["subject"] for r in current}
    latest: dict[str, dict] = {}
    for r in claims:
        if r["subject"] in on_board:
            continue
        cur = latest.get(r["subject"])
        if cur is None or r["as_of_full"] > cur["as_of_full"]:
            latest[r["subject"]] = r
    if not latest:
        return ""
    items = sorted(latest.values(), key=lambda r: -(r["disc"] if r["disc"] is not None else -9))
    bits = [f'<span class="mono">{esc(r["subject"])}</span> <span class="sub">({"—" if r["disc"] is None else f"{r[chr(100)+chr(105)+chr(115)+chr(99)]:+.2f}"} on '
            f'{esc(COHORT_SHORT.get((r["custody"], r["instrument"], r["seed"], r["environment"]), r["seed"]))})</span>'
            for r in items]
    return ('<p class="lead" style="margin-top:.6rem"><strong>Not yet measured on this cohort</strong> — their numbers '
            'elsewhere do not compare to the table above: ' + "; ".join(bits) + '.</p>')


def audit_mark(r) -> str:
    """Compact audit status for narrow tables: ✓ audited, ◌n unaudited, ⚠ v1 rows."""
    if r.get("fa_audit") == "established":
        return '<span class="badge good" title="every control refusal is adjudicated">✓</span>'
    if r.get("fa_audit") == "contains-unaudited-refusals":
        return (f'<span class="badge note" title="{esc(r.get("fa_unaudited"))} unaudited refusal(s): '
                f'FA is an upper bound">◌{esc(r.get("fa_unaudited"))}</span>')
    if r["instrument"] == "synthetic-contract" and r["as_of"] < V2_CUTOVER:
        return '<span class="badge warn" title="v1-changeset rows (erratum 2026-08-22)">⚠</span>'
    return '<span class="badge muted-badge" title="audit status not recorded">?</span>'


def interval_chart(rows) -> str:
    """Dot-and-interval plot: catch and false alarm per binding on one 0–100% axis.

    One axis, two rate series (slots 1 and 2), direct value labels, a legend,
    and the discrimination figure at the row's end. A table view follows."""
    if not rows:
        return ""
    left, right, top, row_h = 300, 70, 28, 34
    width = 980
    plot_w = width - left - right
    height = top + row_h * len(rows) + 30

    def x(v):
        return left + plot_w * max(0.0, min(1.0, v))

    parts = [f'<svg class="viz" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
             f'role="img" aria-label="catch and false-alarm rates with 95% intervals per binding">']
    for tick in (0, .25, .5, .75, 1):
        parts.append(f'<line class="grid" x1="{x(tick):.1f}" y1="{top - 8}" x2="{x(tick):.1f}" '
                     f'y2="{height - 26}"/>'
                     f'<text class="tick" x="{x(tick):.1f}" y="{height - 10}" text-anchor="middle">'
                     f'{int(tick * 100)}%</text>')
    for i, r in enumerate(rows):
        cy = top + row_h * i + row_h / 2
        d = declaration(r["subject"])
        label = r["subject"]
        parts.append(f'<text class="rowlabel" x="{left - 12}" y="{cy + 4}" text-anchor="end">{esc(label)}</text>')
        if d.get("harness"):
            parts.append(f'<text class="rowsub" x="{left - 12}" y="{cy + 15}" text-anchor="end">'
                         f'{esc(d["harness"])}</text>')
        # false alarm first (behind), then catch
        for key, cikey, cls, dy in (("fa", "fa_ci", "fa", 6), ("catch", "catch_ci", "catch", -6)):
            v = r.get(key)
            if v is None:
                continue
            lo, hi = (r.get(cikey) or (v, v))[:2] if len(r.get(cikey) or ()) == 2 else (v, v)
            title = (f'{"false alarm" if key == "fa" else "catch"} {pct(v)} '
                     f'[{pct(lo)}, {pct(hi)}]')
            parts.append(f'<g class="mark {cls}"><title>{esc(title)}</title>'
                         f'<line class="whisker" x1="{x(lo):.1f}" y1="{cy + dy}" x2="{x(hi):.1f}" y2="{cy + dy}"/>'
                         f'<circle cx="{x(v):.1f}" cy="{cy + dy}" r="5"/>'
                         f'<text class="val" x="{x(hi) + 7:.1f}" y="{cy + dy + 4}">{esc(pct(v))}</text></g>')
        disc = r.get("disc")
        parts.append(f'<text class="disc" x="{width - 8}" y="{cy + 4}" text-anchor="end">'
                     f'{"—" if disc is None else f"{disc:+.2f}"}</text>')
    parts.append(f'<text class="axis-title" x="{width - 8}" y="{top - 12}" text-anchor="end">catch − FA</text>')
    parts.append(f'<g class="legend" transform="translate({left},{top - 16})">'
                 f'<circle class="catch" cx="0" cy="0" r="5"/><text x="10" y="4">catch</text>'
                 f'<circle class="fa" cx="70" cy="0" r="5"/><text x="80" y="4">false alarm</text>'
                 f'<line class="whisker-legend" x1="180" y1="0" x2="210" y2="0"/><text x="216" y="4">95% Wilson interval</text></g>')
    parts.append("</svg>")
    return "\n".join(parts)


def standing_table(rows) -> str:
    out = ['<table class="data"><thead><tr><th>binding</th><th>pairs</th><th>catch</th>'
           '<th title="control refusals over adjudicated-sound controls">false alarm</th>'
           '<th>catch − FA</th><th title="structural defects caught / measured">structural</th>'
           '<th title="semantic defects caught / measured">semantic</th>'
           '<th title="share of catches whose finding named the injected element">anchored</th>'
           '<th>FA audit</th><th>declared</th><th>claim</th></tr></thead><tbody>']
    for r in rows:
        d = declaration(r["subject"])
        declared = ("—" if not d.get("exists") else
                    f'{esc(d.get("review_class") or "none")}<br><span class="sub">{esc(d.get("status"))}'
                    + ("" if d.get("review_admitted") else " · no review") + "</span>")
        s, n = r["structural"]
        sem, semn = r["semantic"]
        out.append(
            f'<tr><td>{identity_cell(r["subject"])}</td><td class="num">{r["pairs"]}</td>'
            f'<td class="num">{pct(r["catch"], 1)}<span class="sub"> [{pct(r["catch_ci"][0]) if r["catch_ci"] else "—"}, {pct(r["catch_ci"][1]) if r["catch_ci"] else "—"}]</span></td>'
            f'<td class="num">{pct(r["fa"], 1)}<span class="sub"> /{esc(r["fa_denominator"] or "—")}</span></td>'
            f'<td class="num"><strong>{"—" if r["disc"] is None else f"{r[chr(100)+chr(105)+chr(115)+chr(99)]:+.2f}"}</strong></td>'
            f'<td class="num">{s}/{n}</td><td class="num">{sem}/{semn}</td>'
            f'<td class="num">{pct(r["anchored"])}</td><td>{audit_badge(r)}</td>'
            f'<td>{declared}</td><td class="sub mono" title="{esc(r["claim_id"] or "")}">{esc((r["claim_id"] or "")[:11])}<br>{esc(r["as_of"])}</td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out)


def match_label(label: str, bindings: list[str]) -> str | None:
    for b in bindings:
        if b == label or b.endswith(label) or label.endswith(b):
            return b
    return None


def head_to_head(rows, contrasts) -> str:
    """k×k matrix of matched contrasts on the current cohort (iso runs only)."""
    bindings = [r["subject"] for r in rows]
    cells: dict[tuple, dict] = {}
    for d in contrasts:
        if not d["_file"].startswith("iso-") or "discordant_pairs" not in d:
            continue
        a, b = match_label(d["a"], bindings), match_label(d["b"], bindings)
        if not a or not b or a == b:
            continue
        key = (a, b)
        if key in cells and cells[key]["_file"] > d["_file"]:
            continue
        cells[key] = d
        cells[(b, a)] = {**d, "a": d["b"], "b": d["a"], "a_only_caught": d["b_only_caught"],
                         "b_only_caught": d["a_only_caught"], "a_false_alarms": d["b_false_alarms"],
                         "b_false_alarms": d["a_false_alarms"], "a_only_false_alarm": d["b_only_false_alarm"],
                         "b_only_false_alarm": d["a_only_false_alarm"], "_mirror": True}
    if not cells:
        return ""
    out = ['<table class="matrix"><thead><tr><th>row beats column on catch →</th>']
    for b in bindings:
        out.append(f'<th class="col"><span>{esc(b)}</span></th>')
    out.append('</tr></thead><tbody>')
    for a in bindings:
        out.append(f'<tr><th class="rowhead mono">{esc(a)}</th>')
        for b in bindings:
            if a == b:
                out.append('<td class="diag"></td>')
                continue
            d = cells.get((a, b))
            if not d:
                out.append('<td class="empty" title="no matched contrast recorded">·</td>')
                continue
            ao, bo, p = d["a_only_caught"], d["b_only_caught"], d.get("sign_test_p")
            sig = d.get("significant_at_05")
            fap = d.get("false_alarm_sign_test_p")
            fa_against_row = fap is not None and fap < 0.05 and d["a_only_false_alarm"] > d["b_only_false_alarm"]
            fa_for_row = fap is not None and fap < 0.05 and d["a_only_false_alarm"] < d["b_only_false_alarm"]
            if sig and ao > bo and fa_against_row:
                cls = "split"
            elif sig and bo > ao and fa_for_row:
                cls = "split"
            else:
                cls = ("win" if (sig and ao > bo) or (not sig and fa_for_row)
                       else "loss" if (sig and bo > ao) or (not sig and fa_against_row) else "tie")
            title = (f'{d["a"]} vs {d["b"]}: catch discordant {ao}–{bo}, p={p:.3f}; '
                     f'false alarms {d["a_false_alarms"]} vs {d["b_false_alarms"]}, '
                     f'discordant {d["a_only_false_alarm"]}–{d["b_only_false_alarm"]}, p={fap:.3f} '
                     f'({d.get("false_alarm_audit_status")}); {d["shared_cases"]} shared cases')
            out.append(f'<td class="{cls}" title="{esc(title)}">{ao}–{bo}<br>'
                       f'<span class="sub">p={p:.3f}</span></td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def class_heatmap(rows) -> str:
    classes = [c for c in STRUCTURAL + SEMANTIC
               if any(c in r["by_class"] for r in rows)]
    if not classes:
        return ""
    out = ['<div class="scroll"><table class="heat"><thead><tr><th>binding</th>']
    for c in classes:
        group = "S" if c in STRUCTURAL else "M"
        out.append(f'<th class="col" title="{esc(c)} ({"structural" if group == "S" else "semantic"})">'
                   f'<span>{esc(c.replace("_", " "))}</span></th>')
    out.append('</tr></thead><tbody>')
    for r in rows:
        out.append(f'<tr><th class="rowhead mono">{esc(r["subject"])}</th>')
        for c in classes:
            cell = r["by_class"].get(c)
            if not cell:
                out.append('<td class="empty">·</td>')
                continue
            caught, n, fa = cell
            frac = caught / n if n else 0
            fa_mark = f' <span class="famark" title="{fa} control refusal(s) in this class">⚑{fa}</span>' if fa else ""
            out.append(f'<td class="cell" style="--v:{frac:.2f}" title="{esc(c)}: {caught} of {n} caught'
                       f'{f", {fa} false alarm(s)" if fa else ""}">{caught}/{n}{fa_mark}</td>')
        out.append('</tr>')
    out.append('</tbody></table></div>')
    out.append('<p class="sub">Structural classes first (hash mismatch through broken crossref), then '
               'semantic. Cell shade is the caught share (one hue, light → dark); ⚑n marks control '
               'refusals in that class before adjudication. Cells with n &lt; 5 are one sweep draw — read '
               'the row, not the cell.</p>')
    return "\n".join(out)


def declared_vs_measured(rows) -> str:
    out = ['<table class="data"><thead><tr><th>binding</th><th>striatum status</th>'
           '<th>declared review class</th><th>basis · as of</th><th>admitted for review</th>'
           '<th>measured catch − FA (iso-v1)</th><th>note</th></tr></thead><tbody>']
    for r in rows:
        d = declaration(r["subject"])
        if not d.get("exists"):
            out.append(f'<tr><td class="mono">{esc(r["subject"])}</td><td colspan="6" class="sub">no declaration in striatum-next/backends</td></tr>')
            continue
        note = []
        if d.get("basis") == "measured" and d.get("quality_as_of") and d["quality_as_of"] < "2026-08-23":
            note.append("declared class rests on a pre-isolation measurement")
        if d.get("basis") == "declared":
            note.append("class is a fail-closed placeholder, not a measurement")
        if d.get("status") != "accepted":
            note.append(f"status {d['status']}: not routed")
        out.append(
            f'<tr><td>{identity_cell(r["subject"])}</td>'
            f'<td><span class="badge {"good" if d["status"] == "accepted" else "muted-badge"}">{esc(d["status"])}</span></td>'
            f'<td>{esc(d.get("review_class") or "none")}</td>'
            f'<td class="sub">{esc(d.get("basis") or "—")} · {esc(d.get("quality_as_of") or "—")}</td>'
            f'<td>{"yes" if d.get("review_admitted") else "no"}</td>'
            f'<td class="num"><strong>{"—" if r["disc"] is None else f"{r[chr(100)+chr(105)+chr(115)+chr(99)]:+.2f}"}</strong></td>'
            f'<td class="sub">{esc("; ".join(note))}</td></tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def planning_section(rows) -> str:
    if not rows:
        return ""
    out = ['<table class="data"><thead><tr><th>binding</th><th>tasks</th>'
           '<th title="graphs that parse, index, and resolve — a gate, not a score">clears the gate</th>'
           '<th>yield</th><th title="median packets per graph — the decomposition the rate punishes">median packets</th>'
           '<th>median depth × width</th><th>as of</th></tr></thead><tbody>']
    for r in rows:
        lo, hi = (r["ci"] + (None, None))[:2] if r["ci"] else (None, None)
        out.append(f'<tr><td>{identity_cell(r["subject"])}</td><td class="num">{esc(r["n"])}</td>'
                   f'<td class="num">{pct(r["finish"])}<span class="sub"> [{pct(lo)}, {pct(hi)}]</span></td>'
                   f'<td class="num">{pct(r["yield"])}</td><td class="num">{esc(r["packets"])}</td>'
                   f'<td class="num">{esc(r["dxw"])}</td><td class="sub">{esc(r["as_of"])}</td></tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def fate_section() -> str:
    if not os.path.isfile(FATE):
        return ""
    s = json.load(open(FATE, encoding="utf-8"))
    prods = [(k, v) for k, v in s["producers"].items() if v["packets_first_pass"]["n"] >= 8]
    prods.sort(key=lambda kv: -kv[1]["packets_first_pass"]["n"])
    out = ['<table class="data"><thead><tr><th>producer</th><th>plans</th><th>accepted</th>'
           '<th title="implementation-plan-finishability pass / fail">finishability</th>'
           '<th title="implementation-plan-review pass / fail">plan review</th>'
           '<th>packets</th><th>first-pass checks</th><th>packet-review fail</th></tr></thead><tbody>']
    for k, v in prods:
        g = v["plan_gates"]
        fp = v["packets_first_pass"]
        pr = v["packet_review"]
        out.append(f'<tr><td class="mono">{esc(k)}</td><td class="num">{v["plans_produced"]}</td>'
                   f'<td class="num">{v["plans_accepted"]}</td>'
                   f'<td class="num">{g["implementation-plan-finishability"].get("pass", 0)} / {g["implementation-plan-finishability"].get("fail", 0)}</td>'
                   f'<td class="num">{g["implementation-plan-review"].get("pass", 0)} / {g["implementation-plan-review"].get("fail", 0)}</td>'
                   f'<td class="num">{fp["n"]}</td><td class="num">{pct(fp["rate"])}</td>'
                   f'<td class="num">{pct(pr["fail_rate"])}</td></tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def cohort_table(rows) -> str:
    out = ['<table class="data"><thead><tr><th>binding</th><th>pairs</th><th>catch</th>'
           '<th>false alarm</th><th>catch − FA</th><th>structural</th><th>semantic</th>'
           '<th>anchored</th><th>as of</th><th>flags</th></tr></thead><tbody>']
    for r in rows:
        s, n = r["structural"]
        sem, semn = r["semantic"]
        out.append(f'<tr><td>{identity_cell(r["subject"])}</td><td class="num">{r["pairs"]}</td>'
                   f'<td class="num">{pct(r["catch"], 1)}</td><td class="num">{pct(r["fa"], 1)}</td>'
                   f'<td class="num">{"—" if r["disc"] is None else f"{r[chr(100)+chr(105)+chr(115)+chr(99)]:+.2f}"}</td>'
                   f'<td class="num">{s}/{n}</td><td class="num">{sem}/{semn}</td>'
                   f'<td class="num">{pct(r["anchored"])}</td><td class="sub">{esc(r["as_of"])}</td>'
                   f'<td>{audit_badge(r)}</td></tr>')
    out.append('</tbody></table>')
    return "\n".join(out)


def contrast_rows(contrasts):
    out = []
    for d in contrasts:
        if "discordant_pairs" not in d:
            continue
        seed = str(d.get("sweep_seed") or "?")
        key = (d["a"], d["b"], seed)
        note = ERRATA.get(key, "")
        verdict = "separates" if d.get("significant_at_05") else "not established"
        if d.get("case_selection") == "targeted-reproduction":
            verdict = "targeted reproduction (gate, not discovery)"
        if key in ERRATA and "WITHDRAWN" in ERRATA[key]:
            verdict = "withdrawn"
        out.append({"a": d["a"], "b": d["b"], "seed": seed, "file": d["_file"],
                    "shared": d.get("shared_cases"),
                    "disc": f'{d.get("a_only_caught")}–{d.get("b_only_caught")}',
                    "p": d.get("sign_test_p"), "fa": f'{d.get("a_false_alarms")} vs {d.get("b_false_alarms")}',
                    "fap": d.get("false_alarm_sign_test_p"), "verdict": verdict, "note": note})
    out.sort(key=lambda r: (r["seed"], r["a"], r["b"]))
    return out



# ------------------------------------------------------ conclusions & history

def dominance(rows, contrasts):
    """Established leads on the current cohort: {binding: {"beats": set, "beaten_by": set}}.

    A lead is established when the exact sign test on shared cases clears
    p < 0.05 (`significant_at_05`). Nothing else counts: intervals that do not
    overlap are not a lead, and a larger point estimate is not a lead."""
    bindings = [r["subject"] for r in rows]
    rel = {b: {"beats": set(), "beaten_by": set(), "open": set()} for b in bindings}
    seen = set()
    for d in sorted(contrasts, key=lambda d: d["_file"], reverse=True):
        if not d["_file"].startswith("iso-") or "discordant_pairs" not in d:
            continue
        a, b = match_label(d["a"], bindings), match_label(d["b"], bindings)
        if not a or not b or a == b or frozenset((a, b)) in seen:
            continue
        seen.add(frozenset((a, b)))
        catch_sig = bool(d.get("significant_at_05"))
        fa_sig = (d.get("false_alarm_sign_test_p") is not None
                  and d["false_alarm_sign_test_p"] < 0.05)
        catch_w = (a if d["a_only_caught"] > d["b_only_caught"] else b) if catch_sig else None
        # Fewer false alarms wins the FA axis; ties in direction are not leads.
        fa_w = None
        if fa_sig:
            fa_w = a if d["a_only_false_alarm"] < d["b_only_false_alarm"] else b
        if catch_w and fa_w and catch_w != fa_w:
            # One binding catches more, the other refuses less: no lead either
            # way. Recorded as a split so the verdict can say so out loud.
            rel[a].setdefault("split", set()).add(b)
            rel[b].setdefault("split", set()).add(a)
        elif catch_w or fa_w:
            w = catch_w or fa_w
            l = b if w == a else a
            rel[w]["beats"].add(l)
            rel[l]["beaten_by"].add(w)
        else:
            rel[a]["open"].add(b)
            rel[b]["open"].add(a)
    for r in rel.values():
        r.setdefault("split", set())
    return rel


def tiers(rel):
    """Layer the partial order: tier 1 is beaten by nobody; tier k+1 is beaten
    only by bindings in tiers <= k. Bindings with no contrasts at all sit last."""
    remaining = set(rel)
    placed: dict[str, int] = {}
    level = 1
    while remaining:
        layer = {b for b in remaining if rel[b]["beaten_by"] <= set(placed)}
        if not layer:                       # a cycle of established leads; report flat
            layer = set(remaining)
        for b in layer:
            placed[b] = level
        remaining -= layer
        level += 1
    return placed


def conclusions_html(rows, contrasts) -> str:
    """The board's verdicts, derived mechanically and labelled by assertion type."""
    if len(rows) < 2:
        return ""
    rel = dominance(rows, contrasts)
    tier_of = tiers(rel)
    disc = {r["subject"]: r["disc"] for r in rows}
    by_tier: dict[int, list] = {}
    for b, t in tier_of.items():
        by_tier.setdefault(t, []).append(b)
    parts = ['<div class="verdicts">']
    parts.append('<p class="sub">[Observation] A lead is an established separation (exact sign test on shared cases, '
                 'p &lt; 0.05) on catch or on false alarm that the other axis does not reverse; when one binding catches '
                 'more and the other refuses less, both established, the pair is a <em>split</em> and neither leads. Tiers '
                 'are the layers of that partial order: a binding is in tier 1 when no measured binding has a lead over it. '
                 'Within a tier the order is the point estimate and is not established.</p>')
    parts.append('<ol class="tiers">')
    for t in sorted(by_tier):
        members = sorted(by_tier[t], key=lambda b: -(disc.get(b) or -9))
        items = []
        for b in members:
            beats = sorted(rel[b]["beats"], key=lambda x: -(disc.get(x) or -9))
            open_ = sorted(rel[b]["open"] & {m for m in by_tier[t]}, key=lambda x: -(disc.get(x) or -9))
            splits = sorted(rel[b]["split"], key=lambda x: -(disc.get(x) or -9))
            detail = []
            if beats:
                detail.append("leads " + ", ".join(f"<span class=\"mono\">{esc(x)}</span>" for x in beats))
            if splits:
                detail.append("<strong>split</strong> (catches more, refuses more) with "
                              + ", ".join(f"<span class=\"mono\">{esc(x)}</span>" for x in splits))
            if open_:
                detail.append("not separated from " + ", ".join(f"<span class=\"mono\">{esc(x)}</span>" for x in open_))
            d = disc.get(b)
            items.append(f'<li><span class="mono"><strong>{esc(b)}</strong></span> '
                         f'<span class="num">{"—" if d is None else f"{d:+.2f}"}</span>'
                         + (f' <span class="sub">— {"; ".join(detail)}</span>' if detail else "") + '</li>')
        parts.append(f'<li class="tier"><span class="tierlabel">tier {t}</span><ul>{"".join(items)}</ul></li>')
    parts.append('</ol>')

    # Inferences the reader would otherwise have to assemble by hand.
    notes = []
    top = by_tier.get(1, [])
    if len(top) == 1:
        b = top[0]
        notes.append(f'<span class="mono">{esc(b)}</span> is the only binding no other binding has an established '
                     f'lead over, and it leads {len(rel[b]["beats"])} of the other {len(rows) - 1}.')
    elif len(top) > 1:
        notes.append("Tier 1 has " + ", ".join(f'<span class="mono">{esc(b)}</span>' for b in sorted(top))
                     + ": none of them separates from the others on shared cases at this sample size, so the board "
                       "does not order them.")
    for r in rows:
        if r.get("fa") is not None and r["fa"] >= 0.5:
            n_split = len(rel[r["subject"]]["split"])
            notes.append(f'<span class="mono">{esc(r["subject"])}</span> refuses {pct(r["fa"])} of adjudicated-sound '
                         f'controls (catch {pct(r["catch"])}, catch − FA {r["disc"]:+.2f}). It catches more than '
                         f'{n_split} bindings and refuses more than all of them, established both ways: under this '
                         f'environment it is a rejecter, not a discriminating reviewer, and its catch rate says nothing '
                         f'on its own.')
        d = declaration(r["subject"])
        if not d.get("exists"):
            continue
        beaten_by_weaker = [w for w in rel[r["subject"]]["beaten_by"]
                            if (declaration(w).get("review_class") or "none") in ("baseline", "none")
                            and (d.get("review_class") or "none") in ("strong", "frontier")]
        if beaten_by_weaker:
            notes.append(f'<span class="mono">{esc(r["subject"])}</span> is declared <em>{esc(d["review_class"])}</em> '
                         f'yet has an established deficit to ' + ", ".join(
                             f'<span class="mono">{esc(w)}</span> (declared {esc(declaration(w).get("review_class") or "none")})'
                             for w in sorted(beaten_by_weaker)) + ": the declaration and the measurement disagree.")
        if d.get("status") != "accepted" and rel[r["subject"]]["beats"] & {
                x for x in rel if declaration(x).get("status") == "accepted"}:
            acc = sorted(x for x in rel[r["subject"]]["beats"] if declaration(x).get("status") == "accepted")
            notes.append(f'<span class="mono">{esc(r["subject"])}</span> is <em>{esc(d["status"])}</em> in striatum but has an '
                         f'established lead over accepted ' + ", ".join(f'<span class="mono">{esc(x)}</span>' for x in acc) + ".")
        if d.get("basis") == "measured" and d.get("quality_as_of") and d["quality_as_of"] < "2026-08-23":
            notes.append(f'<span class="mono">{esc(r["subject"])}</span>\'s declared class rests on a pre-isolation '
                         f'measurement; under isolation it measures {r["disc"]:+.2f}.')
    unaudited = [r["subject"] for r in rows if r.get("fa_audit") == "contains-unaudited-refusals"]
    if unaudited:
        notes.append("False alarms are upper bounds for " + ", ".join(f'<span class="mono">{esc(b)}</span>' for b in unaudited)
                     + " until their remaining control refusals are adjudicated.")
    if notes:
        parts.append('<p class="sub" style="margin-top:.8rem">[Inference] What follows from the observations above and the current declarations:</p>')
        parts.append('<ul class="notes">' + "".join(f"<li>{n}</li>" for n in notes) + "</ul>")
    parts.append('<p class="sub">These are readings of the evidence, not decisions: a declaration changes only by a Principal ruling on the claim.</p>')
    parts.append('</div>')
    return "\n".join(parts)


COHORT_SHORT = {
    ("caplab-advisory", "synthetic-contract", "20260819", "iso-v1"): "iso-v1 · 0819",
    ("caplab-advisory", "synthetic-contract", "20260819", "(pre-isolation)"): "pre-iso · 0819",
    ("caplab-advisory", "synthetic-contract", "20260817", "(pre-isolation)"): "pre-iso · 0817",
    ("caplab-advisory", "synthetic-contract", "20260823", "(pre-isolation)"): "pre-iso · 0823",
    ("caplab-advisory", "dispatch-prompt", "20260815", "(pre-isolation)"): "dispatch · 0815",
    ("historical-seed", "dispatch-prompt", "20260807", "(pre-isolation)"): "tuner · 0807",
}


def history_html(claims) -> str:
    """Per-binding history: every cohort a binding was measured on, in time order.

    Small multiples share one y-axis (catch − FA, 0 to 1) and one x-order (the
    cohort's newest claim date), so a reader compares shape across bindings;
    each point is the newest, widest claim of that binding on that cohort."""
    per: dict[str, dict[tuple, dict]] = {}
    for r in claims:
        key = (r["custody"], r["instrument"], r["seed"], r["environment"])
        cur = per.setdefault(r["subject"], {}).get(key)
        if cur is None or (r["pairs"], r["as_of_full"]) > (cur["pairs"], cur["as_of_full"]):
            per[r["subject"]][key] = r
    # x-order: cohorts by their earliest claim date across all bindings
    cohort_first: dict[tuple, str] = {}
    for b, cs in per.items():
        for key, r in cs.items():
            cohort_first[key] = min(cohort_first.get(key, "9"), r["as_of_full"])
    order = sorted(cohort_first, key=lambda k: cohort_first[k])
    xpos = {k: i for i, k in enumerate(order)}
    w, h, pad_l, pad_r, pad_b = 320, 110, 30, 34, 30
    step = (w - pad_l - pad_r) / max(1, len(order) - 1)
    tiny = {"dispatch · 0815": "0815·dsp", "pre-iso · 0817": "0817", "pre-iso · 0819": "0819",
            "pre-iso · 0823": "0823", "iso-v1 · 0819": "0819·iso", "tuner · 0807": "0807·tuner"}

    def x(k):
        return pad_l + xpos[k] * step

    def y(v):
        v = max(0.0, min(1.0, v if v is not None else 0))
        return 8 + (1 - v) * (h - pad_b - 8)

    cards = []
    for b in sorted(per, key=lambda b: -(max((r["disc"] or -9) for r in per[b].values()))):
        cs = per[b]
        if len(cs) < 2:
            continue
        pts = sorted(cs.items(), key=lambda kv: xpos[kv[0]])
        d = declaration(b)
        svg = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" class="spark" role="img" '
               f'aria-label="{esc(b)} discrimination across cohorts">']
        for v in (0, .5, 1):
            svg.append(f'<line class="grid" x1="{pad_l}" y1="{y(v):.1f}" x2="{w - 8}" y2="{y(v):.1f}"/>'
                       f'<text class="tick" x="{pad_l - 4}" y="{y(v) + 4:.1f}" text-anchor="end">{v:.1f}</text>')
        path = " ".join(f'{"M" if i == 0 else "L"}{x(k):.1f},{y(r["disc"]):.1f}' for i, (k, r) in enumerate(pts))
        svg.append(f'<path class="line" d="{path}"/>')
        for k, r in pts:
            iso = k[3] == "iso-v1"
            title = (f'{COHORT_SHORT.get(k, " · ".join(k))}: catch {pct(r["catch"])}, FA {pct(r["fa"])}, '
                     f'catch − FA {r["disc"]:+.2f}, n={r["pairs"]}, {r["as_of"]}')
            svg.append(f'<g><title>{esc(title)}</title><circle class="{"iso" if iso else "pre"}" cx="{x(k):.1f}" '
                       f'cy="{y(r["disc"]):.1f}" r="4.5"/><text class="val" x="{x(k):.1f}" y="{y(r["disc"]) - 8:.1f}" '
                       f'text-anchor="middle">{r["disc"]:+.2f}</text></g>')
        for k in order:
            if k in cs:
                lab = tiny.get(COHORT_SHORT.get(k, ""), k[2])
                dy = h - 16 if xpos[k] % 2 else h - 5      # staggered so neighbours never collide
                svg.append(f'<text class="tick" x="{x(k):.1f}" y="{dy}" text-anchor="middle">{esc(lab)}</text>')
        svg.append('</svg>')
        rows_html = "".join(
            f'<tr><td class="sub">{esc(COHORT_SHORT.get(k, " · ".join(k)))}</td><td class="num">{r["pairs"]}</td>'
            f'<td class="num">{pct(r["catch"])}</td><td class="num">{pct(r["fa"])}</td>'
            f'<td class="num"><strong>{r["disc"]:+.2f}</strong></td><td>{audit_mark(r)}</td></tr>'
            for k, r in pts)
        cards.append(f'<div class="card"><div class="cardhead"><span class="mono"><strong>{esc(b)}</strong></span>'
                     f'<span class="sub"> {esc(d.get("harness") or "")}</span></div>{"".join(svg)}'
                     f'<table class="data mini"><thead><tr><th>cohort</th><th>n</th><th>catch</th><th>FA</th>'
                     f'<th>c − FA</th><th></th></tr></thead><tbody>{rows_html}</tbody></table></div>')
    if not cards:
        return ""
    return ('<p class="lead">Every cohort a binding was measured on, oldest to newest, same y-axis (catch − FA) on every card. '
            'Filled points are isolation runs (the base withheld); hollow points saw the live checkout. A drop from a hollow to a '
            'filled point is the environment, not the model; only filled-to-filled moves compare. Bindings measured on one cohort '
            'only appear in the standing table alone.</p><div class="cards">' + "".join(cards) + '</div>')


# ------------------------------------------------------------------- page

CSS = """
:root { color-scheme: light;
  --surface: #fcfcfb; --surface-2: #f1f0ee; --surface-3: #e7e5e1;
  --ink: #0b0b0b; --ink-2: #52514e; --ink-3: #8a8880; --line: #dedcd7;
  --catch: #2a78d6; --fa: #eb6834; --heat: 42 120 214;
  --good-bg: #e3f3e3; --good-ink: #0d5c0d; --warn-bg: #fdeaea; --warn-ink: #8f1f1e;
  --note-bg: #f1ead6; --note-ink: #6a5510; --win-bg: #e3f3e3; --loss-bg: #fdeaea; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark;
  --surface: #1a1a19; --surface-2: #242423; --surface-3: #2e2e2c;
  --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880; --line: #3a3a38;
  --catch: #3987e5; --fa: #d95926; --heat: 57 135 229;
  --good-bg: #1f3a1f; --good-ink: #9fdc9f; --warn-bg: #3a1d1d; --warn-ink: #f0a9a8;
  --note-bg: #33301f; --note-ink: #e0c771; --win-bg: #1f3a1f; --loss-bg: #3a1d1d; } }
:root[data-theme="dark"] { color-scheme: dark;
  --surface: #1a1a19; --surface-2: #242423; --surface-3: #2e2e2c;
  --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880; --line: #3a3a38;
  --catch: #3987e5; --fa: #d95926; --heat: 57 135 229;
  --good-bg: #1f3a1f; --good-ink: #9fdc9f; --warn-bg: #3a1d1d; --warn-ink: #f0a9a8;
  --note-bg: #33301f; --note-ink: #e0c771; --win-bg: #1f3a1f; --loss-bg: #3a1d1d; }
* { box-sizing: border-box; }
body { margin: 0 auto; max-width: 1080px; padding: 1.6rem 1.2rem 4rem; background: var(--surface);
  color: var(--ink); font: 15px/1.5 system-ui, sans-serif; }
h1 { font-size: 1.45rem; margin: 0 0 .2rem; }
h2 { font-size: 1.1rem; margin: 2.4rem 0 .4rem; padding-bottom: .3rem; border-bottom: 1px solid var(--line); }
h2 .k { color: var(--ink-3); font-weight: 400; font-size: .85rem; margin-left: .5rem; }
p.lead { color: var(--ink-2); margin: .2rem 0 .8rem; }
.sub { color: var(--ink-3); font-size: .8rem; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .86rem; }
nav.toc { display: flex; flex-wrap: wrap; gap: .4rem 1rem; margin: .8rem 0 0; font-size: .88rem; }
nav.toc a { color: var(--ink-2); text-decoration: none; border-bottom: 1px dotted var(--ink-3); }
.rule { background: var(--surface-2); border-left: 3px solid var(--ink-3); padding: .55rem .9rem;
  margin: .8rem 0 1rem; color: var(--ink-2); font-size: .9rem; }
table.data, table.matrix, table.heat { border-collapse: collapse; width: 100%; font-size: .9rem; }
th { text-align: left; color: var(--ink-2); font-weight: 600; border-bottom: 1px solid var(--line);
  padding: .3rem .5rem; vertical-align: bottom; }
td { padding: .32rem .5rem; border-bottom: 1px solid var(--line); vertical-align: top; }
table.data td:first-child, table.data td.mono { white-space: nowrap; }
table.data { font-size: .86rem; }
td.num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.badge { display: inline-block; border-radius: 4px; padding: 0 .4rem; font-size: .76rem; white-space: nowrap; }
.badge.good { background: var(--good-bg); color: var(--good-ink); }
.badge.warn { background: var(--warn-bg); color: var(--warn-ink); }
.badge.note { background: var(--note-bg); color: var(--note-ink); }
.badge.muted-badge { background: var(--surface-3); color: var(--ink-2); }
svg.viz { display: block; max-width: 100%; height: auto; margin: .4rem 0 .8rem; font: 12px system-ui, sans-serif; }
svg.viz .grid { stroke: var(--line); stroke-width: 1; }
svg.viz .tick, svg.viz .rowsub, svg.viz .axis-title { fill: var(--ink-3); font-size: 11px; }
svg.viz .rowlabel { fill: var(--ink); font-family: ui-monospace, monospace; font-size: 12px; }
svg.viz .val { fill: var(--ink-2); font-size: 11px; font-variant-numeric: tabular-nums; }
svg.viz .disc { fill: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }
svg.viz .mark.catch circle, svg.viz .legend .catch { fill: var(--catch); stroke: var(--surface); stroke-width: 2; }
svg.viz .mark.fa circle, svg.viz .legend .fa { fill: var(--fa); stroke: var(--surface); stroke-width: 2; }
svg.viz .mark.catch .whisker { stroke: var(--catch); stroke-width: 2; }
svg.viz .mark.fa .whisker { stroke: var(--fa); stroke-width: 2; }
svg.viz .legend text { fill: var(--ink-2); font-size: 11px; }
svg.viz .whisker-legend { stroke: var(--ink-3); stroke-width: 2; }
table.matrix th.col span, table.heat th.col span { writing-mode: vertical-rl; transform: rotate(180deg);
  display: inline-block; max-height: 150px; font-weight: 500; font-size: .78rem; color: var(--ink-2); }
table.matrix td, table.heat td { text-align: center; font-variant-numeric: tabular-nums; font-size: .86rem; }
table.matrix th.rowhead, table.heat th.rowhead { text-align: left; font-weight: 500; white-space: nowrap; }
table.matrix td.win { background: var(--win-bg); }
table.matrix td.loss { background: var(--loss-bg); }
table.matrix td.split { background: var(--note-bg); }
table.matrix td.diag { background: var(--surface-2); }
table.matrix td.empty, table.heat td.empty { color: var(--ink-3); }
table.heat td.cell { background: rgb(var(--heat) / calc(var(--v) * .55)); }
.famark { color: var(--fa); font-size: .78rem; }
.scroll { overflow-x: auto; }
details { margin: 1.2rem 0; }
details > summary { cursor: pointer; color: var(--ink-2); font-weight: 600; font-size: 1rem;
  padding: .3rem 0; border-bottom: 1px solid var(--line); }
details h3 { font-size: .95rem; margin: 1.2rem 0 .3rem; }
.verdicts { background: var(--surface-2); border-left: 3px solid var(--catch); padding: .7rem 1rem; margin: .6rem 0 1rem; }
ol.tiers { list-style: none; padding: 0; margin: .3rem 0; }
ol.tiers li.tier { display: flex; gap: .8rem; align-items: baseline; padding: .25rem 0; border-top: 1px solid var(--line); }
ol.tiers li.tier:first-child { border-top: 0; }
.tierlabel { flex: 0 0 4.2rem; font-size: .8rem; color: var(--ink-3); text-transform: uppercase; letter-spacing: .04em; }
ol.tiers ul { list-style: none; margin: 0; padding: 0; }
ol.tiers ul li { padding: .08rem 0; }
ul.notes { margin: .2rem 0 .4rem 1.1rem; padding: 0; font-size: .9rem; }
ul.notes li { margin: .15rem 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }
.card { border: 1px solid var(--line); border-radius: 6px; padding: .6rem .7rem; background: var(--surface); }
.cardhead { margin-bottom: .2rem; }
svg.spark { display: block; width: 100%; height: auto; font: 10px system-ui, sans-serif; }
svg.spark .grid { stroke: var(--line); }
svg.spark .tick { fill: var(--ink-3); font-size: 9px; }
svg.spark .line { fill: none; stroke: var(--ink-3); stroke-width: 1.5; }
svg.spark circle.iso { fill: var(--catch); stroke: var(--surface); stroke-width: 1.5; }
svg.spark circle.pre { fill: var(--surface); stroke: var(--catch); stroke-width: 2; }
svg.spark .val { fill: var(--ink-2); font-size: 9px; font-variant-numeric: tabular-nums; }
table.mini { font-size: .78rem; margin-top: .3rem; }
table.mini td, table.mini th { padding: .15rem .35rem; }
footer { margin-top: 3rem; color: var(--ink-3); font-size: .85rem; }
"""


def main() -> int:
    claims = load_claims()
    contrasts = load_contrasts()
    adjudications, sources = advisory_control_context()
    planning = load_planning()

    cohorts: dict[tuple, list] = {}
    for r in claims:
        cohorts.setdefault((r["custody"], r["instrument"], r["seed"], r["environment"]), []).append(r)
    current = best_per_binding(cohorts.get(CURRENT_COHORT, []))
    generated = max((r["as_of_full"] for r in claims), default="?")[:16].replace("T", " ")
    n_adjudicated = len(adjudications)

    # ---- historical cohorts (below the fold)
    def cohort_sort_key(item):
        (custody, instrument, seed, environment), _ = item
        return (custody != "caplab-advisory", instrument, seed != "20260819", seed, environment)

    history = []
    for key, rows in sorted(cohorts.items(), key=cohort_sort_key):
        if key == CURRENT_COHORT:
            continue
        custody, instrument, seed, environment = key
        env_label = "" if environment == "(pre-isolation)" else f" · env {esc(environment)}"
        history.append(f"<h3>{esc(custody)} · {esc(instrument)} · seed {esc(seed)}{env_label}"
                       f' <span class="sub">({len(rows)} claims)</span></h3>{cohort_table(best_per_binding(rows))}')

    # ---- contrasts (full list) and promotion gate
    contrast_html = ['<table class="data"><thead><tr><th>contrast</th><th>seed</th><th>shared</th>'
                     '<th>catch discordance</th><th>p</th><th>false alarms</th><th>FA p</th>'
                     '<th>verdict</th><th>note</th></tr></thead><tbody>']
    for r in contrast_rows(contrasts):
        cls = "withdrawn" if r["verdict"] == "withdrawn" else ""
        contrast_html.append(
            f'<tr class="{cls}"><td class="mono">{esc(r["a"])} vs {esc(r["b"])}</td>'
            f'<td class="num">{esc(r["seed"])}</td><td class="num">{esc(r["shared"])}</td>'
            f'<td class="num">{esc(r["disc"])}</td>'
            f'<td class="num">{"—" if r["p"] is None else f"{r[chr(112)]:.3f}"}</td>'
            f'<td class="num">{esc(r["fa"])}</td>'
            f'<td class="num">{"—" if r["fap"] is None else f"{r[chr(102)+chr(97)+chr(112)]:.3f}"}</td>'
            f'<td>{esc(r["verdict"])}</td><td class="sub">{esc(r["note"])}</td></tr>')
    contrast_html.append("</tbody></table>")

    gate_docs = []
    for name in PROMOTION_CONTRASTS:
        path = os.path.join(REPO, "advisory", "comparisons", name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                gate_docs.append(json.load(f))
    promotion = promotion_candidates(gate_docs, adjudications, substrate_sources=sources)
    promoted_html = ['<table class="data"><thead><tr><th>substrate</th><th>defect class</th>'
                     '<th>pair</th><th>sweeps</th></tr></thead><tbody>']
    for p in promotion["promoted"]:
        promoted_html.append(f'<tr><td class="mono">{esc(p["substrate_id"])}</td><td>{esc(p["defect_class"])}</td>'
                             f'<td>{esc(p["pair"][0])} &gt; {esc(p["pair"][1])}</td>'
                             f'<td class="num">{esc(", ".join(map(str, p["sweeps"])))}</td></tr>')
    promoted_html.append("</tbody></table>")

    # ---- quartermaster projections
    projections = all_projections()
    projection_html = ""
    if projections:
        parts = []
        for proj in projections:
            parts.append(f'<h3>{esc(proj["name"])} <span class="sub">— {esc(proj["construct"])}'
                         f'{" · " + esc(proj["status"]) if proj["status"] else ""}</span></h3>')
            if proj["lead"]:
                parts.append(f'<p class="sub">{esc(proj["lead"])}</p>')
            rows_html = ['<table class="data"><thead><tr><th>rank</th><th>binding</th><th>score</th>'
                         '<th>custody</th><th>seed</th><th>n</th></tr></thead><tbody>']
            for e in proj["ranked"]:
                score = "—" if e["score"] is None else f'{e["score"]:.3f}'
                rows_html.append(f'<tr><td class="num">{esc(e["rank"])}</td><td>{identity_cell(e["label"])}</td>'
                                 f'<td class="num">{score}</td><td>{esc(e["custody"])}</td>'
                                 f'<td class="num">{esc(e["seeds"])}</td><td class="num">{esc(e["n"])}</td></tr>')
            rows_html.append("</tbody></table>")
            if proj["total"] > len(proj["ranked"]) or proj["excluded"]:
                rows_html.append(f'<p class="sub">showing {len(proj["ranked"])} of {proj["total"]} ranked; '
                                 f'{proj["excluded"]} below floors.</p>')
            parts.append("\n".join(rows_html))
        projection_html = "\n".join(parts)

    # ---- production constructs (Tier A/B) compact
    production: dict[str, list] = {}
    with open(os.path.join(REPO, "advisory", "claims.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            construct = c.get("construct") or ""
            if construct.startswith("review.defect_discrimination") or construct.startswith("planning.finishability"):
                continue
            m = c["metrics"]
            primary = next(((k, v) for k, v in m.items() if k != "n_pairs"), None)
            if not primary:
                continue
            production.setdefault(construct, []).append(
                (c["subject"]["source_id"], primary[1].get("value"), primary[1].get("denominator"), primary[0]))
    tier_html = []
    for construct, rows_ in sorted(production.items()):
        rows_ = [r for r in rows_ if r[2]]
        if not rows_:
            continue
        rows_.sort(key=lambda r: -(r[1] or 0))
        metric = rows_[0][3]
        cells = [f'<h3>{esc(construct)} <span class="sub">— {esc(metric)}</span></h3>',
                 '<table class="data"><thead><tr><th>binding</th><th>rate</th><th>n</th></tr></thead><tbody>']
        for s_, pv, pn, _k in rows_:
            dim = ' style="opacity:.55"' if pn < 10 else ""
            cells.append(f'<tr{dim}><td>{identity_cell(s_)}</td><td class="num">{pct(pv)}</td>'
                         f'<td class="num">{esc(pn)}</td></tr>')
        cells.append("</tbody></table>")
        tier_html.append("\n".join(cells))

    custody, instrument, seed, environment = CURRENT_COHORT
    n_current = len(current)
    established = sum(1 for d in contrasts if d["_file"].startswith("iso-") and d.get("significant_at_05"))

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CAPLAB capability board</title>
<style>{CSS}</style></head><body>
<h1>CAPLAB capability board</h1>
<p class="lead">What has been measured about each binding, on the one cohort that compares today.
Newest evidence {esc(generated)} UTC · {len(claims)} review claims · {n_adjudicated} adjudicated controls ·
local page, not published.</p>
<nav class="toc"><a href="#standing">standing</a><a href="#verdict">what it says</a><a href="#h2h">head-to-head</a>
<a href="#classes">by defect class</a><a href="#declared">declared vs measured</a>
<a href="#planning">planning gate</a><a href="#fate">production fate</a>
<a href="#bindings">per-binding history</a><a href="#history">earlier cohorts</a><a href="#derived">derived &amp; harvested</a></nav>

<h2 id="standing">Review capability — current standing
<span class="k">{esc(custody)} · {esc(instrument)} · seed {esc(seed)} · {esc(environment)} · {n_current} bindings</span></h2>
<p class="lead">Matched-pair defect injection under isolation (the base tree withheld, <code>~/git</code> masked).
<strong>Catch</strong> is the share of injected defects the binding refused; <strong>false alarm</strong> is the share
of adjudicated-sound controls it refused. Rows sort by catch − FA. Intervals are 95% Wilson. A binding
with unaudited refusals wears its false alarm as an upper bound.</p>
{interval_chart(current)}
{standing_table(current)}
{missing_from_current(claims, current)}
<div class="rule"><strong>Reading it.</strong> Two bindings separate only where the head-to-head below says so; overlapping
intervals here are not a tie and non-overlapping ones are not a proof. Structural defects (removed, corrupted or
mis-referenced content) are where every binding is weakest under isolation because the base is withheld;
<em>hash_mismatch</em> needs the tree and no one catches it. The binary false-alarm metric rewards silence — a binding
emitting near-zero findings scores a spotless FA for the wrong reason — so read <em>anchored</em> beside it.</div>

<h2 id="verdict">What this board says</h2>
{conclusions_html(current, contrasts)}

<h2 id="h2h">Head-to-head on shared cases <span class="k">{established} established separations</span></h2>
<p class="lead">Exact sign test on the discordant cases two bindings share. A cell reads <em>row-only caught – column-only caught</em>;
green is an established lead for the row, red for the column, amber is a split (one catches more, the other
refuses less — both established), plain is not established. Hover for the false-alarm contrast.</p>
{head_to_head(current, contrasts)}

<h2 id="classes">What each binding catches, by defect class</h2>
{class_heatmap(current)}

<h2 id="declared">Declared vs measured</h2>
<p class="lead">What <code>striatum-next/backends</code> says about each measured binding right now, beside the number.
A declared class is placement policy; a measured number is evidence. The note says when they rest on different eras.</p>
{declared_vs_measured(current)}

<h2 id="planning">Planning gate <span class="k">planning.finishability/1 · plan-v2 · design-only · seed 20260827</span></h2>
<p class="lead">This is a <strong>gate, not a ranking</strong>. Every graph of five packets or fewer clears it, and the only check that
fails (<em>scope_overlap</em>) fires more often the more a binding decomposes — so the rate falls with median packets.
Read yield (did the binding answer) and median packets (did it plan) before the rate. Council disposition 2026-09-04:
routing among admitted planners is operational, not measured here.</p>
{planning_section(planning)}

<h2 id="fate">Production fate <span class="k">covariate, not a claim</span></h2>
<p class="lead">From striatum's own ledger: what happened downstream of each producer's accepted implementation plans. Scheduler-routed —
different tasks per producer, different builders per packet — so this informs a routing objective and a regression alarm,
never a qualification claim. Producers with fewer than 8 attributed packets omitted.</p>
{fate_section()}

<h2 id="bindings">Per-binding history <span class="k">every cohort, oldest to newest</span></h2>
{history_html(claims)}

<details id="history"><summary>Earlier cohorts ({len(cohorts) - (1 if CURRENT_COHORT in cohorts else 0)}) — comparable only within themselves</summary>
<p class="sub">Pre-isolation runs saw the live checkout (ambient tree access moved one arm's catch by ~25 points); seeds 20260815/17
used other case draws; the historical seed is the 2026-08 tuner sweep. Nothing here compares to the standing table above.</p>
{"".join(history)}</details>

<details id="derived"><summary>Derived and harvested — contrasts, promoted corpus, Quartermaster projections, production constructs</summary>
<h3>All matched contrasts</h3>{"".join(contrast_html)}
<h3>Promoted discrimination corpus ({len(promotion["promoted"])} cells)</h3>
<p class="sub">Cells that separated the same pair in the same direction in two independent sweeps, on adjudicated-sound controls,
under clean contracts.</p>{"".join(promoted_html)}
{('<h3>Quartermaster projections</h3><p class="sub">One derived ranking per consumer objective — regenerable, never stored facts.</p>' + projection_html) if projection_html else ""}
<h3>Production constructs (Tier A / Tier B harvest)</h3>
<p class="sub">Per-pass delivery, mechanical gate and independent-family acceptance rates, custody striatum-production.
Deferrals excluded; rows below n=10 dimmed. Model-relative labels where a reviewer judged.</p>
{"".join(tier_html)}</details>

<footer>Regenerate: <code>make leaderboard</code> · claims <code>advisory/claims.jsonl</code> · adjudications
<code>advisory/control-adjudications.jsonl</code> · records <code>docs/records/</code> · built {esc(_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M"))} UTC</footer>
</body></html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT} ({len(page)} bytes; {len(claims)} claims, {len(cohorts)} cohorts, "
          f"{n_current} bindings on the current cohort)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
