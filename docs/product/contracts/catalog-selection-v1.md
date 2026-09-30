# Shared-catalog selection v1

CAPLAB can discover the routes the shared Quartermaster catalog offers it, and can check
one catalog entry against a complete prospective Revbench spec. The catalog supplies
**configured intent** only. It does not build a Binding, admit a native tuple, authorize an
effect, register evidence by itself or qualify anything.

Read [the ubiquitous language](../../domain/ubiquitous-language.md) first. In its terms:
discovery is a **proposal**; the preparation check is a **verification** that two
descriptions of one prospective subject agree; nothing here is an **authorization**,
**decision** or **acceptance**.

## The seam

One explicit argv, run without a shell and without stdin:

```text
<quartermaster-argv...> catalog project RELEASE OVERLAY
```

`--quartermaster-argv` is a JSON list naming the installed command, for example
`["/home/me/.local/bin/quartermaster"]`. It has no default, so a `PATH` lookup never chooses
the inventory. CAPLAB reads the release and overlay bytes once and gives Quartermaster
private copies, so the bytes it retains are the bytes Quartermaster consumed. Only `PATH`,
`PYTHONPATH`, `LANG`, `LC_ALL` and `SYSTEMROOT` are passed on; the working directory is a
private temporary directory; the call times out after 60 seconds and output is capped at
16 MiB.

Quartermaster stays the only catalog validator and model inventory. CAPLAB keeps no route
list and re-validates nothing in the release. It checks the projection's shape only as far
as it relies on it (`document`, `consumer: caplab`, identifiers, `entries`, the three named
parts and their forms) and refuses a native part that does not claim to be a `proposal`.

## `caplab catalog discover`

```sh
caplab catalog discover --release RELEASE --overlay OVERLAY --quartermaster-argv '["..."]' \
  [--native-policy docs/product/contracts/native-agent-systems.json] \
  [--sweep-config advisory/sweep-config.json] [--output FILE]
```

It prints a `caplab-catalog-discovery/1` document and writes nothing else (no ledger, no
custody, no advisory file). `--output` is an exclusive write.

- `status` is `proposal`; every `authority` flag (`preparation`, `adoption`, `qualification`,
  `execution`) is `false`.
- `catalog` names the release, projection and overlay digest Quartermaster reported, plus the
  SHA-256 of the exact release, overlay and projection bytes.
- Each entry carries `declaration_id`: the Striatum declaration ID the advisory lane uses.
  It is **not** a `bnd-` Binding identity and is never turned into one.
- `native.status` per entry:

  | Status | Meaning |
  | --- | --- |
  | `admitted` | the digest-pinned policy already lists this exact tuple (needs `--native-policy`, which must match `CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256`) |
  | `not_admitted` | the closed policy lists no such tuple; a new model reaches this state by appearing in the catalog alone. Listing it needs a new repository-owner contract |
  | `not_native_eligible` | Quartermaster left it out of the native proposal (`reason`: no native contract, home not canonical, home missing) |
  | `policy_not_supplied` | no policy was given to compare against |

- `population` restates the overlay's runtime classification with `applied: false`. With
  `--sweep-config`, a runtime that is supervised-only there but absent from the projected
  population produces `population_would_drop_supervised_runtime`. Caplab's sweep plans every
  runtime missing from that list for unattended execution, so the advisory configuration is
  only ever changed by its owner.

## `caplab revbench prepare` with a catalog entry

Optional arguments, all required together: `--catalog-release`, `--catalog-overlay`,
`--catalog-entry` (a `declaration_id`), `--quartermaster-argv`; plus the optional
`--catalog-reference-output`. The spec is still the complete `caplab-revbench-spec/1`; nothing
is derived from the catalog.

Order of work:

1. Refuse if the ledger directory does not exist (none is created), then project and select
   the entry. The entry must have a native tuple in the projection.
2. `prepare(spec, registrar)` runs unchanged. It alone validates the spec, the Binding, the
   native contract and its digest pin. A tuple the closed policy does not list is refused
   here with its own message, exactly as without catalog options.
3. `validate_against_spec` reads the registered artifacts and requires, in this order:
   the Binding's model, harness and effort to equal the entry's native tuple
   (`catalog_model_mismatch`, `catalog_harness_mismatch`, `catalog_effort_mismatch`); the
   spec's registered policy to list that exact tuple (`catalog_native_tuple_not_admitted`);
   the native command to start with the tuple's executable and required tokens
   (`catalog_command_mismatch`); the version probe command to equal the tuple's
   (`catalog_version_command_mismatch`); and the command's home assignment (`CODEX_HOME`,
   `CLAUDE_CONFIG_DIR` or `HOME`) to equal the catalog profile's `config_home`, or both to be
   absent (`catalog_profile_home_mismatch`).
4. Only then does anything register: the exact release, overlay and projection bytes, then
   a `caplab-catalog-selection/1` receipt, then the manifest. A registered manifest therefore
   always has its catalog provenance; a refusal in steps 1 to 3 leaves the ledger untouched.

Other stable refusals: `catalog_arguments_incomplete`, `catalog_ledger_missing`,
`catalog_entry_unknown`, `catalog_entry_not_native_eligible`, the seam codes
(`catalog_quartermaster_unavailable`, `catalog_quartermaster_argv_invalid`,
`catalog_projection_failed`, `catalog_projection_invalid`,
`catalog_projection_consumer_mismatch`, `catalog_release_mismatch`,
`catalog_input_unreadable`, `catalog_input_too_large`, `catalog_release_invalid`,
`catalog_overlay_invalid`), and `catalog_selection_unavailable_in_live_source_invocation`:
the pinned live-source invocation spawns nothing but its declared native processes, so it
does not accept catalog options.

### What is retained and what is not changed

The manifest, `experiment_id`, Binding and every historical identity are byte-for-byte what
`prepare` returns without catalog options. The receipt records:

- the projection (`projection_id`, `release_id`, `overlay_sha256`, host), the Quartermaster
  argv, and registered references to the exact release, overlay and projection bytes
  (registered as opaque bytes, so no re-encoding);
- the entry (declaration ID, route, account, effort, profile, catalog model spelling) and the
  native tuple;
- `configured_route: {resolution: "configured-route", observed_at: null}`: the catalog route
  is configured intent and is never relabeled as an observed route;
- what was validated (Binding ID, model, harness, effort, profile home, policy digest) and the
  manifest's `experiment_id`;
- `disclosures`, all `false`: no Binding was constructed from the catalog, account identity is
  not part of a Binding (only the profile home is compared), execution is not authorized, and
  nothing is qualified or adopted.

Custody, execution authorization, credential profiles and the live Codex boundary
(ADR 0063) are unchanged. The advisory lane keeps reading its own Striatum declarations;
`advisory/sweep-config.json` and its supervised population are never written.

## Dependencies and known limits

- The installed `quartermaster` command must accept the overlay. Codex's live Revbench subject
  runs an env-less command, so its native contract has **no canonical home** and its catalog
  profile configures none. Quartermaster must therefore accept `native.config_home: null`
  (Quartermaster branch `consolidation/caplab-native-home`, commit `66d2444`); before that
  is installed, such an entry is reported `not_native_eligible` (`config_home_missing`) and
  cannot be selected. The end-to-end test for it runs when
  `CAPLAB_TEST_QUARTERMASTER_SRC` names that source.
- Account identity is not in a Binding. The check compares the profile home only; credential
  profiles for a live run stay a separate authority.
- Discovery judges a tuple against the closed policy; it never judges quality, availability
  or capacity.
