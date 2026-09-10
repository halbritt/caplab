# Corrected Unix test namespace

Under ADR 0026, the primary agent authorizes new readiness custody
`reviewer-ranking-001/development/dependency-readiness-2`. Preserve all first
batch results. Copy the same four exact source snapshots and only the installed
dependency files named by each first-batch inventory, verifying their hashes
and links. No dependency version changes or new downloads are authorized.

Provide `/bin` and `/sbin` aliases, private `/var/tmp`, a minimal local-hosts
and user/group configuration, and a read-only copy of `/etc/ld.so.cache` for
the public system libraries already mounted. These correct observed missing
`/var/tmp`, `/sbin/ldconfig.real` and localhost-resolution failures. Provide
separate copies of the prepared npm cache and force offline npm behavior so
release tests cannot wait on disabled networking. Keep those remaining cache
or historical-native-runtime prerequisites explicit.

Authorize up to four five-second namespace preflights and four original test
script invocations with `--maxWorkers=2`, 180 seconds each and 800 seconds
total. All run with disabled networking, empty owner credentials and separate
workspaces. Record source preservation, dependency identities, exact commands
and every failure. No consumed first-batch slot is replayed; these are new
environment observations. Do not repair historical source or relabel a missing
system fixture as a source defect. Expiry: consumption or 2026-09-11T00:00:00Z.
