# Independently investigate the three natural newsroom findings

Under ADR 0026 and the active goal, authorize a model-free witness in private
`reviewer-ranking-001/development/newsroom-findings-witness-1` custody.
The investigator has seen the completed natural review. That exposure is
recorded; it does not establish truth or independence. Expected behavior must
come from the original repository's requirements and actual observations.

Reuse the hash-checked full original base and change trees from
`newsroom-natural-output-2`. Mount them read-only in separate user/network
namespaces with disposable homes and databases. Preserve their original
commit/tree/blob identities. Do not mutate the target checkout or prior
custody. Use Python 3.12 and its existing pinned runtime. No model, real
Reddit, Slack, publication, timer or provider account is contacted.

Serve valid original-format HTML listings over local HTTPS for
`old.reddit.com`, using the established isolated low-port capability and a
test certificate. Keep ordinary urllib, parsing, filtering, executor and
state code unchanged. Capture actual request timestamps and response bodies;
do not replace `_fetch_subreddit`, `_reserve`, `harvest`, configuration loaders
or CLI functions with stubs. Preserve real source clocks and timeouts.

Two executions of each condition are authorized, at most 60 seconds each:

- Original base listing fetch: three configured AI subreddits, valid fresh
  posts and real HTTPS. Establish the pre-change request behavior.
- Original change harvest and pool: same healthy listings, then a fresh
  adapter reading the durable pool. Disable only the optional `rss_fallback`
  setting and observe both harvest and pool fetch using the same valid state.
- Original change CLI under a separately held `run.lock`: run harvest, run
  and fetch as distinct processes with a disposable data directory. Supply
  frozen test configuration through a read-only mount over the config input,
  leaving the original Python source untouched. Record exit codes, request
  receipts and durable candidates. The run control must stop at the lock
  before any model or delivery effect.

Freeze fixture, configuration, source/runtime identities and observation
criteria before executing. Separate the questions: does RSS disabling prevent
an otherwise working pool; does the CLI obey the run lock by command; do
actual listing requests share a 65-second interval, and did that behavior
change from the base? The latter two behavior observations alone cannot prove
that the reviewer interpreted the lock or pacing requirement correctly.

Preserve all outputs and failures. Do not award defect credit from a source
anchor or successful reproduction alone. Keep a disputed requirement scope
or change attribution unresolved. No corpus admission, general scorer
acceptance, comparative ranking or original-code repair is authorized.
Expiry: these six consumed executions or 2026-09-11T00:00:00Z. Stop on identity
drift, invalid response/configuration, unexpected endpoint or an expired
budget. No automatic replay; preserve failed preparation separately.
