# Claude native interface and credential delivery preparation

The installed Claude Code binary identifies itself as `2.1.268 (Claude Code)`
and exposes structured output, max effort, stream capture and safe-mode
options. Both version and help completed with exit 0 in fresh network-isolated
namespaces without credentials or project files. This establishes the local
interface, not provider authentication or reviewer competence.

The one metadata-only credential inspection found the expected Claude OAuth
fields, a locally future millisecond expiry and inference scope. No token,
account identifier or raw credential bytes were retained by that inspection.
The [authorization](authorization-2026-09-10-reviewer-claude-preflight.md)
separates those reads from later credential delivery and model execution.
Private evidence is under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/claude-preflight-1`.
Commands, binary hash, stdout, stderr, terminal status and metadata projection
are retained. `inspection-method.py` is a post-execution copy of the method;
the contemporaneous launch records retain the actual command arrays. The
[preflight receipt](../product/studies/reviewer-ranking-001/claude-preflight-development-receipt.json)
pins all 12 retained files.

Official [environment documentation](https://code.claude.com/docs/en/env-vars)
describes `CLAUDE_CODE_OAUTH_TOKEN` as the access-token interface for automated
sessions. The [CLI reference](https://code.claude.com/docs/en/cli-reference)
describes `--json-schema` and safe mode. Local help confirms both options for
the installed binary. Safe mode preserves authentication and built-in tools
while suppressing customizations; its use remains part of the administered
configuration. The native system prompt is retained.

The new `claude_external_credential` adapter reuses the existing bounded,
non-following source reader and sealed-descriptor primitive. It checks source
identity, local expiry and inference scope, then delivers only the access
token. The refresh token is never delivered. Four synthetic tests exercise
sealed read-only delivery and descriptor closure, source preservation,
chunk-boundary token quarantine, expiry/scope/hash refusal, unsafe permissions,
symlink refusal and duplicate-key diagnostics. They pass. These are credential
handling tests, not authentication tests or review-quality measurements.

The adapter's exact-byte guard does not establish transformed-secret detection
or memory erasure. Local credential metadata does not prove account identity,
provider acceptance or available model capacity. The separate
[native review authorization](authorization-2026-09-10-reviewer-claude-output.md)
names the single real delivery and development attempt; it does not retroactively
turn this preparation into a reviewer result.

The full repository check passed after the adapter change: 1,564 tests in
204.677 seconds, seven skips. The retained check log SHA-256 is
`21a6b631039f75b3365b5b62de4cce8a0614841ef106a0ed1a83177e71767d08`
in the separate `claude-output-1` custody root.
