"""Deterministic re-runnable check for dispatch b206738756470f74... (substrate
qs-93a90787f0d83382, fleet-overlay-autoresolve product artifact).

Three allegations from the codex-sol-high refusal, each settled against the
change set's own files only:

  A1  docs/reference/deferrals.md lists "go test ./... as a registered
      verification check" and "a lint-rfcs check identity in policy/checks/" as
      STANDING deferrals, while policy/checks/repository.json (same set) defines
      both checks and puts lint-rfcs in the active "code" set.
  A2  docs (fleet-catalog-resolution.md and root.go comments) say overlay
      resolution happens ONCE per invocation; runAcceptance calls
      openGraphAndCatalog (discarding the resolved Config) and then
      buildSession, which calls openGraphAndCatalog again.
  A3  wakeTimerUnits renders ExecStart by space-joining argv after stripping
      double quotes, with no systemd escaping; resolveEffectiveOverlays admits
      any clean absolute directory path, whitespace included; so the timer does
      not reliably carry the promised -catalog-overlay snapshot.

Exit 0 = control is DEFECTIVE.  Exit 1 = control is SOUND.
"""
import json, os, re, sys
exchange = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
DISPATCH = "b206738756470f74"
full = [x for x in os.listdir(os.path.join(exchange, "dispatch"))
        if x.startswith(DISPATCH)][0]
bundle = os.path.join(exchange, "dispatch", full)
man = json.load(open(os.path.join(bundle, "manifest.json")))
files = json.loads(open(os.path.join(bundle, man["inputs"][0]["path"]),
                        errors="replace").read())["files"]
results = {}


def func_body(src, name):
    m = re.search(r"(?s)\nfunc (?:\([^)]*\) )?" + re.escape(name) + r"\(.*?\n}\n", src)
    return m.group(0) if m else ""


# --- A1: deferrals page vs checks registry ---------------------------------
deferrals = files["docs/reference/deferrals.md"]
registry = json.loads(files["policy/checks/repository.json"])
build_flow = re.search(r"(?s)\{#el:build-flow\}.*?\n## ", deferrals).group(0)
results["a1_page_lists_lint_rfcs_as_standing_deferral"] = bool(
    re.search(r"^\| Self-law as a verification gate: a `lint-rfcs` check identity in `policy/checks/`",
              build_flow, re.M))
results["a1_page_lists_go_test_as_standing_deferral"] = bool(
    re.search(r"^\| `go test \./\.\.\.` as a registered verification check", build_flow, re.M))
by_argv = {tuple(c["argv"]): c["check_id"] for c in registry["checks"]}
lint_id = next((cid for argv, cid in by_argv.items() if argv[-1] == "./tools/lint-rfcs"), None)
gotest_id = next((cid for argv, cid in by_argv.items() if argv[1:] == ("test", "./...")), None)
results["a1_registry_defines_lint_rfcs_check"] = lint_id is not None
results["a1_lint_rfcs_in_active_code_set"] = lint_id in registry["sets"].get("code", [])
results["a1_registry_defines_go_test_check"] = gotest_id is not None
results["a1_go_test_in_any_set"] = any(gotest_id in s for s in registry["sets"].values())
results["a1_page_retired_section_mentions_lint_rfcs"] = "lint-rfcs" in deferrals.split("{#el:retired}")[-1]
a1 = (results["a1_page_lists_lint_rfcs_as_standing_deferral"]
      and results["a1_registry_defines_lint_rfcs_check"]
      and results["a1_lint_rfcs_in_active_code_set"]
      and not results["a1_page_retired_section_mentions_lint_rfcs"])
results["a1_substantiated"] = a1

# --- A2: once-per-invocation claim vs runAcceptance --------------------------
root = files["internal/cli/root.go"]
explanation = files["docs/explanation/fleet-catalog-resolution.md"]
results["a2_doc_claims_once_per_invocation"] = (
    "Resolution happens once per invocation" in explanation
    and "computed once per invocation" in root
    and "one resolution per invocation" in root)
acceptance = func_body(root, "runAcceptance")
session = func_body(root, "buildSession")
results["a2_runAcceptance_calls_openGraphAndCatalog"] = "openGraphAndCatalog(config)" in acceptance
results["a2_runAcceptance_discards_resolved_config"] = bool(
    re.search(r"graph, catalog, _, err := openGraphAndCatalog\(config\)", acceptance))
results["a2_runAcceptance_then_calls_buildSession_with_original_config"] = bool(
    re.search(r"session, _, err := buildSession\(config\)", acceptance))
results["a2_buildSession_calls_openGraphAndCatalog"] = "openGraphAndCatalog(config)" in session
results["a2_openGraphAndCatalog_resolves_each_call"] = (
    "resolveEffectiveOverlays(config, graph.RepoID)" in func_body(root, "openGraphAndCatalog"))
a2 = all(results[k] for k in (
    "a2_doc_claims_once_per_invocation",
    "a2_runAcceptance_calls_openGraphAndCatalog",
    "a2_runAcceptance_then_calls_buildSession_with_original_config",
    "a2_buildSession_calls_openGraphAndCatalog",
    "a2_openGraphAndCatalog_resolves_each_call"))
results["a2_substantiated"] = a2

# --- A3: unquoted ExecStart vs whitespace-bearing overlay path ---------------
wake = files["internal/cli/waketimer.go"]
units = func_body(wake, "wakeTimerUnits")
results["a3_doc_promises_timer_receives_overlay_snapshot"] = (
    "re-emitted to the post-commit wake and the standing liveness timer as explicit absolute `-catalog-overlay` argv"
    in explanation)
results["a3_execstart_is_space_joined"] = 'strings.Join(quoted, " ")' in units and "ExecStart=" in units
results["a3_only_transform_is_quote_stripping"] = 'strings.ReplaceAll(arg, `"`, ``)' in units
results["a3_no_escaping_helper_used"] = not re.search(
    r"strconv\.Quote|shellquote|systemd.*escape|QuoteArg|escapeArg", wake)
resolve = func_body(root, "resolveEffectiveOverlays")
results["a3_resolver_rejects_whitespace_paths"] = bool(
    re.search(r"IsSpace|ContainsAny\([^)]*\" |whitespace", resolve))
# Replicate the Go rendering in Python and show the split.
argv = ["/usr/local/bin/striatum", "-catalog-overlay", "/srv/fleet instance/catalog", "-trigger", "timer"]
rendered = " ".join(a.replace('"', "") for a in argv)
results["a3_rendered_execstart_sample"] = "ExecStart=" + rendered
results["a3_systemd_word_count_vs_argv_len"] = [len(rendered.split()), len(argv)]
a3 = (results["a3_doc_promises_timer_receives_overlay_snapshot"]
      and results["a3_execstart_is_space_joined"]
      and results["a3_no_escaping_helper_used"]
      and not results["a3_resolver_rejects_whitespace_paths"]
      and len(rendered.split()) != len(argv))
results["a3_substantiated"] = a3

defective = a1 or a2 or a3
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE" if defective else "SOUND")
sys.exit(0 if defective else 1)
