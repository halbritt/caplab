#!/usr/bin/env python3
"""Extract agent-driving-striatum transcripts into a normalized JSONL corpus.

The lane corpus (extract.py) mines what *lanes* received and produced via the
exchange spool. This extractor mines the other role: the *driving* agent — the
interactive operator loop (Claude Code under ~/.claude and ~/.claude-harm,
Codex under ~/.codex/sessions) that issues `striatum request/drive/status/
resolve/...`, reads the compiler's answers, and decides what to do next.

Outputs (under --out, default corpus-driver/):
  sessions.jsonl        one record per transcript file that invokes striatum
  events.jsonl          normalized event stream for driver-role sessions
  striatum_calls.jsonl  one record per striatum CLI invocation with the
                        command, its output, and the decision context that
                        preceded it (the SFT-shaped grain)
  stats.json            corpus summary

Every record carries (file, line_no) pointers back to the raw transcript, so
truncated fields are recoverable losslessly. Nothing here writes to any graph
store; workstation tooling, same standing as extract.py.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

CORPUS_VERSION = 1

STRIATUM_VERBS = {
    "init", "request", "cancel", "drive", "status", "accept", "reject",
    "resolve", "revoke", "reconcile", "ledger",
    # historical / auxiliary verbs seen in older transcripts
    "escalations", "observe", "graph", "backends", "catalog", "verify",
}

RESOLVE_DISPOSITIONS = {"proceed", "cancel_request", "reissue", "redirect", "override"}

# a token that is the striatum binary: bare name or any path ending in /striatum
BIN_RE = re.compile(r"(?:^|[\s;&|()!`'\"=])((?:[\w~./+-]*/)?striatum)(\s|$)")

TEXT_CAP = 16000
OUTPUT_CAP = 8000
COMMAND_CAP = 4000
FIRST_USER_CAP = 600
PRE_TEXT_CAP = 2500


def cap(s, n):
    if s is None:
        return None, 0
    if not isinstance(s, str):
        s = json.dumps(s, ensure_ascii=False, default=str)
    ln = len(s)
    return (s if ln <= n else s[:n]), ln


def shlex_ish(cmd):
    """Cheap tokenizer good enough to find the striatum verb."""
    return re.findall(r"'[^']*'|\"[^\"]*\"|\S+", cmd)


def striatum_verb(cmd):
    """Return (verb, disposition) for the first striatum invocation in cmd, or (None, None)."""
    if "striatum" not in cmd:
        return None, None
    toks = shlex_ish(cmd)
    for i, t in enumerate(toks):
        base = t.strip("'\"")
        if base == "striatum" or base.endswith("/striatum"):
            j = i + 1
            verb = None
            disposition = None
            while j < len(toks):
                tj = toks[j].strip("'\"")
                if tj.startswith("-"):
                    # flag; may consume a value (space-separated form)
                    if "=" not in tj and j + 1 < len(toks) and not toks[j + 1].startswith("-"):
                        nxt = toks[j + 1].strip("'\"")
                        if verb is None and nxt in STRIATUM_VERBS:
                            # ambiguous: treat verb-looking token as flag value
                            pass
                        j += 2
                        continue
                    j += 1
                    continue
                if verb is None and tj in STRIATUM_VERBS:
                    verb = tj
                    j += 1
                    continue
                if verb == "resolve" and tj in RESOLVE_DISPOSITIONS:
                    disposition = tj
                    break
                if verb == "ledger" and tj in ("cat", "seal"):
                    disposition = tj
                    break
                if verb is not None:
                    break
                # positional that is not a known verb (e.g. numeric seq) — keep looking
                j += 1
            if verb:
                if verb == "resolve" and disposition is None:
                    m = re.search(r"--?disposition[= ]+['\"]?(\w+)", cmd)
                    if m:
                        disposition = m.group(1)
                return verb, disposition
    return None, None


NOTE_RE = re.compile(r"--?note[= ]+(?:\"((?:[^\"\\]|\\.)*)\"|'([^']*)'|(\S+))")


def extract_note(cmd):
    if not cmd or "note" not in cmd:
        return None
    m = NOTE_RE.search(cmd)
    if not m:
        return None
    return next((g for g in m.groups() if g is not None), None)


def has_striatum_invocation(cmd):
    return striatum_verb(cmd)[0] is not None


def classify_cwd(cwd):
    if not cwd:
        return None, "unknown"
    if "/striatum/exchange/" in cwd and "/workspaces/" in cwd:
        return cwd, "lane"
    m = re.search(r"/git/([\w.-]+)", cwd)
    repo = m.group(1) if m else cwd
    return repo, "workstation"


# ---------------------------------------------------------------- discovery

def discover(roots):
    """rg for striatum verb usage across *.jsonl under each root."""
    pat = r"striatum(\.|\s|\\n)|/striatum\s"
    files = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            out = subprocess.run(
                ["rg", "-l", "--no-messages", "-e", pat, "--glob", "*.jsonl", root],
                capture_output=True, text=True, timeout=1800,
            ).stdout
            files.extend([l for l in out.splitlines() if l])
        except FileNotFoundError:
            for dirpath, _dirnames, filenames in os.walk(root):
                for fn in filenames:
                    if fn.endswith(".jsonl"):
                        p = os.path.join(dirpath, fn)
                        try:
                            with open(p, "rb") as fh:
                                if b"striatum" in fh.read():
                                    files.append(p)
                        except OSError:
                            pass
    return sorted(set(files))


# ---------------------------------------------------------------- claude

def claude_blocks(content):
    """Yield (kind, payload) from a claude message content field."""
    if isinstance(content, str):
        if content.strip():
            yield ("text", content)
        return
    if not isinstance(content, list):
        return
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text" and b.get("text", "").strip():
            yield ("text", b["text"])
        elif t == "thinking" and b.get("thinking", "").strip():
            yield ("thinking", b["thinking"])
        elif t == "tool_use":
            yield ("tool_use", b)
        elif t == "tool_result":
            yield ("tool_result", b)


def tool_result_text(b):
    c = b.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts = []
        for x in c:
            if isinstance(x, dict) and x.get("type") == "text":
                parts.append(x.get("text", ""))
        return "\n".join(parts)
    return json.dumps(c, ensure_ascii=False, default=str) if c is not None else ""


def parse_claude_file(path, account):
    """Parse one Claude Code transcript. Returns (session, events)."""
    session = {
        "corpus_version": CORPUS_VERSION,
        "source": account,
        "interface": "claude-code",
        "file": path,
        "session_id": None,
        "cwd": None,
        "git_branch": None,
        "models": Counter(),
        "harness_versions": set(),
        "started_at": None,
        "ended_at": None,
        "first_user_text": None,
        "agent_kind": "session",
        "n_lines": 0,
    }
    rel = path
    if "/subagents/" in path:
        session["agent_kind"] = "workflow-agent" if "/workflows/" in path else "subagent"

    events = []
    seq = 0
    pending_tool = {}  # tool_use_id -> index in events

    with open(path, "r", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            session["n_lines"] = line_no
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            rtype = rec.get("type")
            ts = rec.get("timestamp")
            if ts:
                session["started_at"] = session["started_at"] or ts
                session["ended_at"] = ts
            if rec.get("sessionId") and not session["session_id"]:
                session["session_id"] = rec["sessionId"]
            if rec.get("cwd") and not session["cwd"]:
                session["cwd"] = rec["cwd"]
            if rec.get("gitBranch") and not session["git_branch"]:
                session["git_branch"] = rec["gitBranch"]
            if rec.get("version"):
                session["harness_versions"].add(rec["version"])

            if rtype not in ("user", "assistant"):
                continue
            msg = rec.get("message") or {}
            if not isinstance(msg, dict):
                continue
            if rtype == "assistant" and msg.get("model"):
                session["models"][msg["model"]] += 1
            sidechain = bool(rec.get("isSidechain"))

            for kind, payload in claude_blocks(msg.get("content")):
                seq += 1
                ev = {
                    "session_id": session["session_id"],
                    "file": rel,
                    "line_no": line_no,
                    "seq": seq,
                    "ts": ts,
                    "sidechain": sidechain,
                }
                if kind == "text":
                    ev["kind"] = "user" if rtype == "user" else "assistant"
                    ev["text"], ev["text_len"] = cap(payload, TEXT_CAP)
                    if rtype == "user" and session["first_user_text"] is None \
                            and not rec.get("isMeta") and not sidechain \
                            and not payload.startswith(("<local-command", "<command-name", "Caveat:")):
                        session["first_user_text"] = cap(payload, FIRST_USER_CAP)[0]
                elif kind == "thinking":
                    ev["kind"] = "thinking"
                    ev["text"], ev["text_len"] = cap(payload, TEXT_CAP)
                elif kind == "tool_use":
                    ev["kind"] = "tool_call"
                    ev["tool"] = payload.get("name")
                    ev["tool_use_id"] = payload.get("id")
                    inp = payload.get("input") or {}
                    if ev["tool"] == "Bash" and isinstance(inp, dict) and "command" in inp:
                        ev["command"], ev["command_len"] = cap(inp.get("command", ""), COMMAND_CAP)
                        v, d = striatum_verb(inp.get("command", ""))
                        if v:
                            ev["is_striatum"] = True
                            ev["striatum_verb"] = v
                            if d:
                                ev["striatum_disposition"] = d
                    else:
                        ev["input"], ev["input_len"] = cap(inp, COMMAND_CAP)
                        raw = json.dumps(inp, ensure_ascii=False, default=str)
                        v, d = striatum_verb(raw)
                        if v:
                            ev["is_striatum"] = True
                            ev["striatum_verb"] = v
                            if d:
                                ev["striatum_disposition"] = d
                    if payload.get("id"):
                        pending_tool[payload["id"]] = len(events)
                elif kind == "tool_result":
                    ev["kind"] = "tool_result"
                    ev["tool_use_id"] = payload.get("tool_use_id")
                    ev["is_error"] = bool(payload.get("is_error"))
                    ev["text"], ev["text_len"] = cap(tool_result_text(payload), OUTPUT_CAP)
                    idx = pending_tool.get(payload.get("tool_use_id"))
                    if idx is not None:
                        ev["for_call_seq"] = events[idx]["seq"]
                events.append(ev)

    session["models"] = dict(session["models"])
    session["harness_versions"] = sorted(session["harness_versions"])
    return session, events


# ---------------------------------------------------------------- codex

CODEX_CMD_RE = re.compile(r"exec_command\(\{", re.S)


def codex_extract_cmd(js_src):
    """Pull the cmd string out of a cells-runtime exec source, best-effort."""
    m = re.search(r'cmd\s*:\s*"((?:[^"\\]|\\.)*)"', js_src, re.S)
    if m:
        try:
            return json.loads('"' + m.group(1) + '"')
        except json.JSONDecodeError:
            return m.group(1)
    m = re.search(r"cmd\s*:\s*`([^`]*)`", js_src, re.S)
    if m:
        return m.group(1)
    return None


def parse_codex_file(path):
    session = {
        "corpus_version": CORPUS_VERSION,
        "source": "codex",
        "interface": "codex",
        "file": path,
        "session_id": None,
        "cwd": None,
        "git_branch": None,
        "models": Counter(),
        "harness_versions": set(),
        "started_at": None,
        "ended_at": None,
        "first_user_text": None,
        "agent_kind": "session",
        "n_lines": 0,
    }
    events = []
    seq = 0
    call_by_id = {}
    cur_model = None

    with open(path, "r", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            session["n_lines"] = line_no
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            rtype = rec.get("type")
            ts = rec.get("timestamp")
            if ts:
                session["started_at"] = session["started_at"] or ts
                session["ended_at"] = ts
            p = rec.get("payload") or {}

            if rtype == "session_meta":
                session["session_id"] = p.get("id") or p.get("session_id")
                session["cwd"] = p.get("cwd")
                if p.get("cli_version"):
                    session["harness_versions"].add(p["cli_version"])
                if p.get("thread_source") == "subagent" or p.get("agent_nickname"):
                    session["agent_kind"] = "subagent"
                    session["agent_nickname"] = p.get("agent_nickname")
                continue
            if rtype == "turn_context":
                if p.get("model"):
                    cur_model = p["model"]
                    session["models"][cur_model] += 1
                if p.get("cwd") and not session["cwd"]:
                    session["cwd"] = p["cwd"]
                continue
            if rtype != "response_item":
                continue

            ptype = p.get("type")
            seq += 1
            ev = {
                "session_id": session["session_id"],
                "file": path,
                "line_no": line_no,
                "seq": seq,
                "ts": ts,
                "sidechain": False,
            }
            if ptype == "message":
                role = p.get("role")
                parts = []
                for c in p.get("content") or []:
                    if isinstance(c, dict) and c.get("type") in ("input_text", "output_text", "text"):
                        parts.append(c.get("text", ""))
                text = "\n".join(x for x in parts if x)
                if not text.strip():
                    seq -= 1
                    continue
                ev["kind"] = "user" if role == "user" else "assistant"
                ev["text"], ev["text_len"] = cap(text, TEXT_CAP)
                if role == "user" and session["first_user_text"] is None \
                        and not text.startswith(("<", "#", "[")):
                    session["first_user_text"] = cap(text, FIRST_USER_CAP)[0]
            elif ptype == "reasoning":
                parts = []
                for s in p.get("summary") or []:
                    if isinstance(s, dict):
                        parts.append(s.get("text", ""))
                for c in p.get("content") or []:
                    if isinstance(c, dict):
                        parts.append(c.get("text", ""))
                text = "\n".join(x for x in parts if x)
                if not text.strip():
                    seq -= 1
                    continue
                ev["kind"] = "thinking"
                ev["text"], ev["text_len"] = cap(text, TEXT_CAP)
            elif ptype in ("function_call", "custom_tool_call"):
                ev["kind"] = "tool_call"
                ev["tool"] = p.get("name")
                ev["tool_use_id"] = p.get("call_id") or p.get("id")
                raw = p.get("arguments") if ptype == "function_call" else p.get("input")
                raw = raw if isinstance(raw, str) else json.dumps(raw or {}, ensure_ascii=False)
                cmd = None
                if ptype == "function_call":
                    try:
                        a = json.loads(raw)
                        if isinstance(a, dict):
                            c = a.get("command") or a.get("cmd")
                            if isinstance(c, list):
                                cmd = " ".join(str(x) for x in c)
                            elif isinstance(c, str):
                                cmd = c
                    except json.JSONDecodeError:
                        pass
                else:
                    cmd = codex_extract_cmd(raw)
                if cmd is not None:
                    ev["command"], ev["command_len"] = cap(cmd, COMMAND_CAP)
                else:
                    ev["input"], ev["input_len"] = cap(raw, COMMAND_CAP)
                probe = cmd if cmd is not None else raw
                v, d = striatum_verb(probe)
                if v:
                    ev["is_striatum"] = True
                    ev["striatum_verb"] = v
                    if d:
                        ev["striatum_disposition"] = d
                if ev.get("tool_use_id"):
                    call_by_id[ev["tool_use_id"]] = len(events)
            elif ptype in ("function_call_output", "custom_tool_call_output"):
                ev["kind"] = "tool_result"
                ev["tool_use_id"] = p.get("call_id")
                out = p.get("output")
                if isinstance(out, dict):
                    out = out.get("content") or out.get("output") or json.dumps(out, ensure_ascii=False)
                ev["text"], ev["text_len"] = cap(out or "", OUTPUT_CAP)
                idx = call_by_id.get(p.get("call_id"))
                if idx is not None:
                    ev["for_call_seq"] = events[idx]["seq"]
            else:
                seq -= 1
                continue
            events.append(ev)

    session["models"] = dict(session["models"])
    session["harness_versions"] = sorted(session["harness_versions"])
    return session, events


# ---------------------------------------------------------------- assembly

def finalize(session, events):
    repo, locus = classify_cwd(session.get("cwd"))
    session["repo"] = repo
    calls = [e for e in events if e.get("is_striatum")]
    session["n_events"] = len(events)
    session["n_tool_calls"] = sum(1 for e in events if e["kind"] == "tool_call")
    session["n_striatum_calls"] = len(calls)
    session["striatum_verbs"] = dict(Counter(e["striatum_verb"] for e in calls))
    if locus == "lane":
        session["role"] = "lane"
    elif calls:
        session["role"] = "driver"
    else:
        session["role"] = "mention"
    return session


def striatum_call_records(session, events):
    """The SFT-shaped grain: command + output + preceding decision context."""
    out = []
    result_for = {}
    for e in events:
        if e["kind"] == "tool_result" and e.get("for_call_seq"):
            result_for[e["for_call_seq"]] = e
    last_context = None
    for e in events:
        if e["kind"] in ("assistant", "thinking") and not e.get("sidechain"):
            last_context = e
        if e.get("is_striatum"):
            res = result_for.get(e["seq"])
            rec = {
                "source": session["source"],
                "interface": session["interface"],
                "session_id": session["session_id"],
                "agent_kind": session["agent_kind"],
                "repo": session["repo"],
                "file": e["file"],
                "line_no": e["line_no"],
                "seq": e["seq"],
                "ts": e["ts"],
                "verb": e["striatum_verb"],
                "disposition": e.get("striatum_disposition"),
                "command": e.get("command") or e.get("input"),
                "note": extract_note(e.get("command") or e.get("input")),
                "models": session["models"],
            }
            if last_context is not None:
                rec["pre_text"], rec["pre_text_len"] = cap(
                    last_context.get("text", ""), PRE_TEXT_CAP)
                rec["pre_kind"] = last_context["kind"]
            if res is not None:
                rec["output"] = res.get("text")
                rec["output_len"] = res.get("text_len")
                rec["is_error"] = res.get("is_error", False)
            out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--claude-root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--claude-harm-root", default=os.path.expanduser("~/.claude-harm/projects"))
    ap.add_argument("--codex-root", default=os.path.expanduser("~/.codex/sessions"))
    ap.add_argument("--out", default="corpus-driver")
    ap.add_argument("--limit", type=int, default=0, help="debug: cap files per source")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    sources = [
        ("claude", args.claude_root, "claude"),
        ("claude-harm", args.claude_harm_root, "claude"),
        ("codex", args.codex_root, "codex"),
    ]

    sess_f = open(os.path.join(args.out, "sessions.jsonl"), "w")
    ev_f = open(os.path.join(args.out, "events.jsonl"), "w")
    call_f = open(os.path.join(args.out, "striatum_calls.jsonl"), "w")

    stats = defaultdict(Counter)
    verb_stats = defaultdict(Counter)
    n_files = 0

    for account, root, fmt in sources:
        files = discover([root])
        if args.limit:
            files = files[: args.limit]
        print(f"[{account}] {len(files)} candidate files under {root}", file=sys.stderr)
        for i, path in enumerate(files):
            try:
                if fmt == "claude":
                    session, events = parse_claude_file(path, account)
                else:
                    session, events = parse_codex_file(path)
            except Exception as exc:  # noqa: BLE001 — log and continue the sweep
                print(f"  ! {path}: {exc}", file=sys.stderr)
                stats[account]["parse_errors"] += 1
                continue
            session = finalize(session, events)
            stats[account][f"role_{session['role']}"] += 1
            stats[account]["files"] += 1
            n_files += 1
            sess_f.write(json.dumps(session, ensure_ascii=False, default=str) + "\n")
            if session["role"] == "driver":
                stats[account]["driver_events"] += len(events)
                stats[account]["striatum_calls"] += session["n_striatum_calls"]
                for v, c in session["striatum_verbs"].items():
                    verb_stats[account][v] += c
                base = {"source": account, "interface": session["interface"]}
                for e in events:
                    ev_f.write(json.dumps({**base, **e}, ensure_ascii=False, default=str) + "\n")
                for rec in striatum_call_records(session, events):
                    call_f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            if (i + 1) % 200 == 0:
                print(f"  … {i + 1}/{len(files)}", file=sys.stderr)

    sess_f.close(); ev_f.close(); call_f.close()

    summary = {
        "corpus_version": CORPUS_VERSION,
        "files": n_files,
        "per_source": {k: dict(v) for k, v in stats.items()},
        "striatum_verbs": {k: dict(v) for k, v in verb_stats.items()},
    }
    with open(os.path.join(args.out, "stats.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
