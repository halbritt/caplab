"""Deterministic re-runnable check for control qs-40583720e067908f
(P12-independent-verification-a change set, dispatch 01407fbb...).

Allegations (oc-deepseek-v4-flash + oc-deepseek-v4-pro): the receipts
(receipts/semantic-closure-suite.json, receipts/architecture-lint.json)
and verification-report.json assert a real executed verification run --
execution.exit_code 0, stdout/stderr digests, timed_out false, sealed
outcome "accept" -- while the SAME change set's submission-manifest.json
diagnostics.assumptions states the packet "does not itself execute
go test ./... or tools/lint-rfcs" and that accept "is asserted on the
conservative assumption" that earlier packets passed, and
run-manifest.json's note says the manifest is "Build-lane synthesized".
Secondary (flash): base_composition.observed_product pins content_hash
dd9c4672... for (product-artifact, version_seq 0) while every delivered
file pins d7f3a22c... for the same identity and version_seq.

All of this is in-set: one file asserts concrete execution facts that
another file in the same set concedes never occurred. This is the
disclaimed-in-one-file / asserted-exact-in-the-next pattern already ruled
DEFECTIVE in this campaign (dossier precedent d98bbffc); a sibling
disclosure does not make "execution.exit_code": 0 true, and
synthesized_from is empty so the receipts do not even mark themselves
synthetic.

Mechanical core:
  (a) both receipts carry execution.exit_code == 0 with stdout/stderr
      digests and timed_out false;
  (b) verification-report.json outcome == "accept" with per-check accept
      outcomes bound to those receipts' seal digests;
  (c) submission-manifest.json assumptions contain the non-execution
      concession; run-manifest note says build-lane synthesized;
  (d) submission-manifest.synthesized_from == [] (nothing marks the
      receipts as synthetic in their own record shape);
  (e) observed_product content_hash vs the subject pins (reported;
      envelope-vs-materialized-tree alternative reading noted).

DEFECTIVE iff (a or b) and (c): execution evidence asserted, execution
denied, in one set. Exit 0 = DEFECTIVE. Exit 1 = sound.
"""
import hashlib, json, os, sys

PATH = os.path.expanduser(
    "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325/"
    "dispatch/01407fbb5ea42bc7410b44582afcbe4e95e9cd45f5df6c2bf296c8e73f5fdf07/"
    "inputs/00-striatum-next-passes-semantic-and-durable-closure-packets-"
    "P12-independent-verification-a-change-set")
SHA256 = "40583720e067908f3b58f91adb389b2d8934d80c54bc00342d63baf3b5814f2d"

raw = open(PATH, "rb").read()
if hashlib.sha256(raw).hexdigest() != SHA256:
    print("substrate sha256 mismatch -- refusing to adjudicate", file=sys.stderr)
    raise SystemExit(2)
cs = json.loads(raw)
files = cs["files"]
base = "ledger/RQ-57950/submissions/verification-signal-a/"
rec_a = json.loads(files[base + "receipts/semantic-closure-suite.json"])
rec_b = json.loads(files[base + "receipts/architecture-lint.json"])
report = json.loads(files[base + "verification-report.json"])
subman = json.loads(files[base + "submission-manifest.json"])
runman = json.loads(files[base + "run-manifest.json"])

results = {}

# (a) receipts assert concrete execution facts.
def asserts_execution(r):
    e = r.get("execution", {})
    return (e.get("exit_code") == 0 and bool(e.get("stdout_digest"))
            and bool(e.get("stderr_digest")) and e.get("timed_out") is False)
results["receipts_assert_execution"] = (
    asserts_execution(rec_a) and asserts_execution(rec_b))

# (b) report asserts accept bound to those receipts.
results["report_outcome_accept"] = report.get("outcome") == "accept"
results["report_binds_receipt_seals"] = (
    {o["receipt_hash"] for o in report["check_outcomes"]}
    == {rec_a["seal"]["seal_digest"], rec_b["seal"]["seal_digest"]}
    and all(o["outcome"] == "accept" for o in report["check_outcomes"]))

# (c) the same set concedes no execution happened.
assumptions = " ".join(subman["diagnostics"]["assumptions"])
results["set_concedes_no_execution"] = (
    "does not itself execute go test ./... or tools/lint-rfcs" in assumptions)
results["accept_is_assumed_not_observed"] = (
    "asserted on the conservative assumption" in assumptions)
results["run_manifest_is_synthesized"] = runman["note"].startswith(
    "Build-lane synthesized")

# (d) nothing in the receipts' own shape marks them synthetic.
results["synthesized_from_empty"] = subman.get("synthesized_from") == []
results["receipts_self_mark_synthetic"] = any(
    "synth" in json.dumps(r).lower() for r in (rec_a, rec_b))

# (e) secondary: observed_product pin vs subject pins, same identity+seq.
op = cs["base_composition"]["observed_product"]
subj = rec_a["subject"]
results["observed_product_pin"] = {
    "identity": op["identity"], "version_seq": op["version_seq"],
    "content_hash": op["content_hash"]}
results["subject_pin"] = {
    "identity": subj["identity"], "version_seq": subj["version_seq"],
    "content_hash": subj["content_hash"]}
results["same_identity_seq_two_hashes"] = (
    op["identity"] == subj["identity"]
    and op["version_seq"] == subj["version_seq"]
    and op["content_hash"] != subj["content_hash"])

results["out_of_contract"] = [
    "whether checks 62d3fbf5/b828ab97 exist in the live registry (v13 "
    "pinned here vs live) is out-of-set",
    "whether P15 admission would in fact refuse this staged signal is "
    "production wiring, out-of-set",
]
results["needs_judgment"] = (
    "secondary only: observed_product content_hash dd9c4672 vs subject "
    "d7f3a22c could be an anchor-envelope hash vs materialized tree hash; "
    "the verdict does not rest on it")

defective = (
    (results["receipts_assert_execution"] or results["report_outcome_accept"])
    and results["set_concedes_no_execution"]
    and not results["receipts_self_mark_synthetic"]
)
results["control_is_defective"] = defective
print(json.dumps(results, indent=2, sort_keys=True))
print("VERDICT:", "DEFECTIVE (fabricated execution evidence, disclaimed in-set)"
      if defective else "SOUND")
sys.exit(0 if defective else 1)
