# Ubiquitous language entrypoint

The canonical repository vocabulary is
[`../../ubiquitous_language.md`](../../ubiquitous_language.md).

This uppercase file is the requested DDD discovery entrypoint. It contains no
definitions, so case-sensitive and case-insensitive tools cannot observe two
competing root glossaries. The lowercase root path is also consumed by doctrine
tooling and pinned evaluation surfaces.

Update the canonical file when a term's repository-wide meaning changes. Use
the [context map](context-map.md) when the same term intentionally has different
meanings in separate contexts, and record a selected boundary or translation
rule in an [ADR](../decisions/README.md).
