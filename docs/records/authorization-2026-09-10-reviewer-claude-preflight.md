# Inspect the Claude native administration interface

Under ADR 0026 and the active reviewer-ranking goal, authorize a bounded
Claude Code preparation inspection in private custody
`reviewer-ranking-001/development/claude-preflight-1`. This closes an
administration gap; it supplies no reviewer performance evidence.

Permit exactly one `--version` and one `--help` execution of the installed
`/home/halbritt/.local/share/claude/versions/2.1.268` binary in a fresh
network-isolated Bubblewrap namespace with synthetic home, no user settings,
no credentials, no project or historical evidence and a ten-second limit
per command. Pin the binary bytes and preserve commands, stdout, stderr and
terminal status. Read public official documentation if needed to interpret
these interfaces. No provider or model request is authorized.

Permit one local metadata inspection of
`/home/halbritt/.claude/.credentials.json` through a non-following descriptor.
Require a regular, single-link, current-user-owned mode-0600 file of at most
64 KiB. Parse only in memory; report required Claude OAuth field presence,
value types, known scope names and numeric expiry relative to now. Do not
print or retain raw bytes, credentials, account identifiers, token hashes,
refresh timestamps or unrecognized string values. No credential may be
copied, delivered to a process, refreshed or written by this inspection.
Stop on an unsafe source type or unsupported schema; preserve source bytes.

Permit implementation and synthetic testing of a separate credential adapter
only after the observed interface establishes its requirements. Such tests
must use invented credentials and local fixtures. A later exact authorization
must name any delivery of the real credential and live native review. Do not
modify earlier frozen credential contracts or historical captures.

The two preflight commands and one metadata read expire on consumption or
2026-09-11T02:00:00Z. No case admission, ranking, qualification, original source
repair, model spend or operational placement is authorized by this record.
