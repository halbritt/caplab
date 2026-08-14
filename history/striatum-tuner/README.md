# `striatum-tuner` absorption record

`striatum-tuner` is historical custody and provenance for CAPLAB. It is no
longer an independent capability-measurement or qualification authority.
CAPLAB did not copy the tuner's generated corpora, model artifacts, raw run
directories, or historical result bodies into this public repository.

The absorption preserves a narrower, useful result: the matched-pair
known-defect method is now the `caplab.revbench` experiment family. Its active
implementation produces a CAPLAB Measurement against an exact Binding and
uses an independently registered mechanical oracle. The active implementation
does not inherit the tuner's downstream-fate control selection, ranking, DPO,
or backend-tier conclusions.

## Evidence classification

The repository-owner build task defines five classes:

- **A — valid capability measurement.** No historical tuner run was admitted
  wholesale in this class. An old result can be reconsidered only through a
  separately authorized import that proves its exact Binding, protocol,
  corpus, case selection, evidence registration, and independent truth basis.
- **B — useful observational or covariate data.** Historical run results and
  outcome summaries remain in their source custody. They are not CAPLAB
  Measurements. Downstream fate may later be registered as the
  `downstream_fate` covariate, never as qualification truth.
- **C — reusable infrastructure.** The defect-injection, paired-control, and
  deterministic scoring ideas were selectively reimplemented behind the
  pinned CAPLAB contracts. Source identity and hashes are in
  [`migration-manifest.json`](migration-manifest.json).
- **D — obsolete fate-derived qualification logic.** Fate agreement,
  fate-selected controls, rankings, DPO preferences derived from those labels,
  and backend-tier interpretations remain historical and non-authoritative.
- **E — unclear or unadmitted material.** Ignored and untracked generated data,
  private raw material, model outputs, and large workspaces remain untouched in
  the source checkout. They were not inventoried as evidence, copied,
  registered, rewritten, or deleted.

The classification was independently inspected from the CAPLAB boundary, the
tuner boundary, and the revbench failure path. Disagreements were resolved
conservatively: a mechanically checkable transformation is reusable
infrastructure, but a historical run does not become Class A merely because
part of its injector can be verified.

## Custody and compatibility

The source snapshot used for this decision is pinned by repository commit,
tree, path, and content or inventory hashes in the migration manifest. These
locators are historical provenance, not registered CAPLAB evidence references.
Registration is a separate, authorized effect.

Read-only inspection of the pinned `striatum-next` tree found documentation,
policy comments, and backend `benchmark_ref` strings, but no executable or
import dependency on `striatum-tuner`. No compatibility service or adapter was
created. Existing strings remain historical locators until their owning
repository replaces them through its own decision process.

No source data was deleted. The source repository receives a retirement notice
in its own local Git history; its raw custody stays in place.
