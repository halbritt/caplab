# Finding — reference resolution against the wrong repository

- Date: 2026-08-23. Reported by the Principal: on two controls,
  oc-deepseek-pro reviewers demonstrably resolved a change set's file
  references against the caplab tree the lane was mounted in, not the
  change set under review.
- Class: the third face of one defect — the artifact names repository
  paths, the harness supplies a filesystem, the subject conflates the two.
  Write was the replay escape; search was the OOM greps; this is read.
  The read-only sandbox of earlier today did not prevent it: read access
  was enough to compute reference verdicts against the wrong universe, in
  both directions (false dangling-reference refusals when the path lives
  in another repo; false clears when the mounted tree happens to match).

## Fix (landed, instrument-versioned)

1. **The checkouts no longer exist inside a lane.** `sandbox_argv` masks
   `~/git` with a tmpfs instead of ro-binding it; only the case workspace
   is visible. Files the *declaration* pins by absolute path (agy's
   `--json-schema` under striatum-next) are re-exposed read-only — files
   the declaration names, never directories, never anything the artifact
   names. Verified: agy, codex, claude-code, opencode all answer inside
   the masked sandbox.
2. **Neutral cwd.** Lanes now run in the case workspace, never a
   repository checkout — a subject that "looks around" finds only its own
   spill file.
3. **Preamble v2** adds: the filesystem is not the artifact; judge
   references only against the artifact's own content. Version recorded
   per row, with a new `workspace_isolation: 1` row field.

## Comparability caveat, honestly stated

Every agentic-harness row before this change had ambient read access to
both checkouts. For striatum-next artifacts, subjects could resolve
references against the *right* tree — an affordance lane subjects never
had — so part of the mounting gradient (gemini +28, GLM +14, deepseek +9)
may be ambient-repo access rather than tools per se, concentrated in the
reference-resolution defect classes (dangling_reference,
broken_internal_crossref, checks-real). The gradient's direction is safe
(three pairs, zero reversals); its decomposition into tool-use versus
ambient-tree access is not, and a post-isolation re-measurement of one
harness pair would separate them. Verdicts on the two named controls are
the reporting session's records; the class is what CAPLAB owns.
