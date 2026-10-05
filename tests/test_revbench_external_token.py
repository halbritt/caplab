"""The additive external-token Revbench administration, with fabricated credentials only.

Covers the selected construction decisions: a separately pinned external-token bundle policy
and closed public profile, private anchors supplied apart from the credential source, a
required access lifetime derived from the retained deadline, a directly executed host
Bubblewrap whose pinned loader closure is rechecked before every launch, and a retained
record of that check.  Original v1 bytes, defaults and behavior are asserted unchanged.

No real credential, native Codex, Bubblewrap, provider or AppArmor object is used; the
host-closure tests build their own fabricated trees.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

from caplab.revbench import codex, host_closure
from caplab.revbench.codex import (
    CODEX_EXTERNAL_CREDENTIAL_PROFILE_SCHEMA,
    CODEX_NATIVE_BUNDLE_POLICY_SHA256,
    CODEX_NATIVE_EXTERNAL_BUNDLE_POLICY_SHA256,
    CodexAdapterError,
    codex_native_bundle_policy,
    codex_native_bundle_policy_bytes,
    codex_native_external_bundle_policy,
    codex_native_external_bundle_policy_bytes,
    normalized_codex_containment_argv,
    pinned_bundle_policy_matching,
    validate_credential_profile,
)
from caplab.revbench.custody import (
    FilesystemLiveExecutionRuntime,
    LiveExecutionCustodyError,
    RecoveredProcessCapture,
)
from caplab.revbench.external_credential import (
    open_external_revbench_credential,
    required_access_lifetime_seconds,
)
from caplab.runtime.canonical import canonical_json, sha256_hex
from tests.support_host_closure import SyntheticHost, synthetic_elf
from tests.test_codex_external_credential import digest, fixture as credential_fixture

_SIGNAL_PATCHERS: list = []


def setUpModule():
    """No test in this module may signal a real process; every primitive fails fast."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unintercepted signal primitive called: {args!r}")

    for target in ("os.killpg", "os.kill", "signal.pthread_kill", "signal.raise_signal"):
        patcher = mock.patch(target, side_effect=refuse)
        patcher.start()
        _SIGNAL_PATCHERS.append(patcher)


def tearDownModule():
    while _SIGNAL_PATCHERS:
        _SIGNAL_PATCHERS.pop().stop()


PROFILE_ID = "caplab-openai-external"
ANCHORS_SCHEMA = "caplab-revbench-external-credential-anchors/1"


def external_profile(**changes):
    profile = {
        "schema_version": CODEX_EXTERNAL_CREDENTIAL_PROFILE_SCHEMA,
        "profile_id": PROFILE_ID,
        "provider": "openai",
        "auth_method": "chatgpt-external-tokens",
        "delivery_method": "codex-external-token-file/1",
        "quarantine_profile": "credential-private-text/v2",
        "initial_credentials_store": "file",
        "lifetime_rule": "access-token-covers-effective-execution-deadline/1",
        "private_anchor_schema": ANCHORS_SCHEMA,
    }
    profile.update(changes)
    return profile


def deadline_in(seconds: float) -> str:
    return (datetime.now(UTC) + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def diff_paths(left, right, prefix=""):
    """Dotted paths at which two JSON values differ (dict keys and list lengths/items)."""

    if isinstance(left, dict) and isinstance(right, dict):
        found = []
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                found.append(f"{prefix}{key}")
            else:
                found += diff_paths(left[key], right[key], f"{prefix}{key}.")
        return found
    return [] if left == right else [prefix.rstrip(".")]


class ExternalPolicyTests(unittest.TestCase):
    def test_original_policy_bytes_pin_and_default_selection_are_unchanged(self):
        self.assertEqual(
            CODEX_NATIVE_BUNDLE_POLICY_SHA256,
            "211354874f4e3443a6e11fbe8b09cf54205c9cfc767f1a9a7ca2d7a9b210a68e",
        )
        self.assertEqual(
            hashlib.sha256(codex_native_bundle_policy_bytes()).hexdigest(),
            CODEX_NATIVE_BUNDLE_POLICY_SHA256,
        )
        v1 = codex_native_bundle_policy()
        self.assertEqual(v1["policy_id"], "codex-terra-max-revbench-live-v1")
        self.assertEqual(v1["credential_profile_schema"], "caplab-revbench-codex-credential-profile/1")
        self.assertNotIn("host_closure", v1)
        self.assertEqual(v1["version_containment_argv_template"][0], "{adapter_loader}")
        self.assertEqual(
            normalized_codex_containment_argv(["codex", "--version"]),
            v1["version_containment_argv_template"],
        )
        # The apparatus receipt still pins the original document and, additively, names the new one.
        protocol = codex.execution_apparatus_receipt(require_clean=False)["protocol"]
        self.assertEqual(protocol["bundle_policy_source_sha256"], CODEX_NATIVE_BUNDLE_POLICY_SHA256)
        self.assertEqual(
            protocol["external_token_bundle_policy_source_sha256"],
            CODEX_NATIVE_EXTERNAL_BUNDLE_POLICY_SHA256,
        )
        self.assertEqual(protocol["host_closure_trust"], host_closure.TRUST_ASSUMPTION)

    def test_external_policy_is_its_own_pinned_document_and_differs_only_as_selected(self):
        self.assertEqual(
            hashlib.sha256(codex_native_external_bundle_policy_bytes()).hexdigest(),
            CODEX_NATIVE_EXTERNAL_BUNDLE_POLICY_SHA256,
        )
        v1, external = codex_native_bundle_policy(), codex_native_external_bundle_policy()
        self.assertEqual(external["schema_version"], v1["schema_version"])
        differing = diff_paths(v1, external)
        unselected = [
            path
            for path in differing
            if not path.startswith(
                (
                    "policy_id",
                    "launcher.review_argv",
                    "containment.adapter_sha256",
                    "containment.adapter_launch",
                    "version_containment_argv_template",
                    "review_containment_argv_template",
                    "adapter_runtime",
                    "host_closure",
                    "credential_profile_schema",
                    "credential_delivery",
                    "evidence_limits",
                )
            )
        ]
        self.assertEqual(unselected, [])
        # Everything about the native subject, tools, network and containment shape is the same.
        for section in ("native_agent_system", "environment", "response_schema", "pinned_host_resources"):
            self.assertEqual(external[section], v1[section], section)
        for field in ("executable_sha256", "executable_byte_count", "harness_version", "version_argv", "target"):
            self.assertEqual(external["launcher"][field], v1["launcher"][field], field)
        self.assertEqual(
            {key: value for key, value in external["containment"].items()
             if key not in ("adapter_sha256", "adapter_launch")},
            {key: value for key, value in v1["containment"].items() if key != "adapter_sha256"},
        )

    def test_review_command_adds_only_the_file_credential_store_setting(self):
        v1 = codex_native_bundle_policy()["launcher"]["review_argv"]
        external = codex_native_external_bundle_policy()["launcher"]["review_argv"]
        extra = ["-c", "cli_auth_credentials_store=file"]
        index = external.index("cli_auth_credentials_store=file") - 1
        self.assertEqual(external[index : index + 2], extra)
        self.assertEqual(external[:index] + external[index + 2 :], v1)
        self.assertEqual(
            [t for t in external if t.startswith("cli_auth_credentials_store=")],
            ["cli_auth_credentials_store=file"],
        )  # the store is pinned once, to file; `--ephemeral` is Codex's separate session flag
        # The frozen native-system contract constrains these leading tokens; they are unchanged.
        self.assertEqual(external[1:6], v1[1:6])

    def test_external_templates_run_the_pinned_host_path_directly_with_the_same_flags(self):
        v1, external = codex_native_bundle_policy(), codex_native_external_bundle_policy()
        for name in ("version_containment_argv_template", "review_containment_argv_template"):
            self.assertEqual(v1[name][:4], ["{adapter_loader}", "--library-path", "{adapter_library_directory}", "{adapter_executable}"])
            self.assertEqual(external[name][0], "/usr/bin/bwrap")
            # The one selected template difference besides the host path: the review layout creates /tmp
            # (see test_every_mountpoint_...); everything else is the original template.
            remainder = list(external[name][1:])
            if name == "review_containment_argv_template":
                created = [i for i in range(len(remainder) - 1) if remainder[i : i + 2] == ["--dir", "/tmp"]]
                self.assertEqual(len(created), 1)
                del remainder[created[0] : created[0] + 2]
            self.assertEqual(remainder, v1[name][4:])
            self.assertFalse([t for t in external[name] if t in ("{adapter_loader}", "{adapter_library_directory}", "{adapter_executable}")])
        self.assertEqual(external["containment"]["adapter_path"], "/usr/bin/bwrap")

    @staticmethod
    def mountpoint_violations(template):
        """Replay a containment template's filesystem operations in order; list what cannot succeed.

        Bubblewrap performs its operations in argument order. After ``--remount-ro /`` the root is
        read-only, so a later ``--tmpfs``/``--dir``/``--file`` can only land on a directory that
        already exists or inside a tmpfs mounted since. The model knows only the options this
        template uses; an unknown option fails the replay so the model must be extended with it.
        """

        arity = {"--unshare-all": 0, "--share-net": 0, "--die-with-parent": 0, "--new-session": 0,
                 "--clearenv": 0, "--hostname": 1, "--proc": 1, "--dev": 1, "--perms": 1, "--file": 2,
                 "--ro-bind-data": 2, "--setenv": 2, "--chdir": 1, "--dir": 1, "--tmpfs": 1, "--remount-ro": 1}
        def parents(path):
            return [str(p) for p in Path(path).parents if str(p) != "/"]

        exists, writable_mounts, read_only, violations = {"/"}, set(), False, []

        def writable(path):
            return not read_only or any(path == m or path.startswith(m + "/") for m in writable_mounts)

        index = 1  # token 0 is the adapter path
        while index < len(template) and template[index] != "--":
            option = template[index]
            if option not in arity:
                return [(option, "option unknown to the replay model")]
            operands = template[index + 1 : index + 1 + arity[option]]
            index += 1 + arity[option]
            if option in ("--dir", "--tmpfs"):
                path = operands[0]
                if option == "--tmpfs" and read_only:
                    if path not in exists and not writable(path):
                        violations.append((option, path))
                    writable_mounts.add(path)
                elif not writable(path) and path not in exists:
                    violations.append((option, path))
                exists.update([path, *parents(path)])
            elif option in ("--file", "--ro-bind-data"):
                path = operands[1]
                if not writable(str(Path(path).parent)) and str(Path(path).parent) not in exists:
                    violations.append((option, path))
                exists.update([path, *parents(path)])
            elif option == "--remount-ro" and operands == ["/"]:
                read_only = True
        return violations

    def test_every_mountpoint_requested_after_the_root_goes_read_only_already_exists(self):
        external = codex_native_external_bundle_policy()
        for name in ("version_containment_argv_template", "review_containment_argv_template"):
            with self.subTest(name):
                self.assertEqual(self.mountpoint_violations(external[name]), [])
        review = external["review_containment_argv_template"]
        # The later tmpfs is kept; /tmp is created exactly once, with the other directories, before the remount.
        self.assertEqual(review.count("/tmp"), 2)  # the new --dir and the kept --tmpfs
        directory_at = next(i for i in range(len(review) - 1) if review[i : i + 2] == ["--dir", "/tmp"])
        tmpfs_at = next(i for i in range(len(review) - 1) if review[i : i + 2] == ["--tmpfs", "/tmp"])
        self.assertLess(directory_at, review.index("--remount-ro"))
        self.assertLess(review.index("--remount-ro"), tmpfs_at)
        self.assertLess(review.index("/work"), directory_at)  # beside the other directory creations
        # The replay is a real check: the template as selected before this repair fails it exactly as the
        # offline diagnostic observed (mkdir /tmp on a read-only root), and so does any other missing mountpoint.
        before = copy.deepcopy(review)
        del before[directory_at : directory_at + 2]
        self.assertEqual(self.mountpoint_violations(before), [("--tmpfs", "/tmp")])
        no_work = copy.deepcopy(review)
        no_work_at = next(i for i in range(len(no_work) - 1) if no_work[i : i + 2] == ["--dir", "/work"])
        del no_work[no_work_at : no_work_at + 2]
        self.assertEqual(self.mountpoint_violations(no_work), [("--tmpfs", "/work")])
        self.assertEqual(self.mountpoint_violations(["/usr/bin/bwrap", "--bind", "/", "/"]),
                         [("--bind", "option unknown to the replay model")])

    def test_pinned_members_and_closure_description_agree(self):
        policy = codex_native_external_bundle_policy()
        closure = policy["host_closure"]
        runtime = policy["adapter_runtime"]
        self.assertEqual(closure["schema_version"], host_closure.CLOSURE_SCHEMA)
        self.assertEqual(closure["trust_assumption"], host_closure.TRUST_ASSUMPTION)
        self.assertEqual(closure["launch_environment"], "empty")
        self.assertEqual(closure["executable"]["path"], policy["containment"]["adapter_path"])
        self.assertEqual(closure["executable"]["sha256"], policy["containment"]["adapter_sha256"])
        self.assertEqual(closure["executable"]["byte_count"], policy["containment"]["adapter_byte_count"])
        interpreter = closure["interpreter"]
        self.assertEqual(interpreter["path"], runtime["loader"]["path"])
        self.assertEqual(interpreter["path"], interpreter["pt_interp"])
        self.assertEqual(
            (interpreter["sha256"], interpreter["byte_count"], interpreter["resolution"][-1]["mode"]),
            (runtime["loader"]["sha256"], runtime["loader"]["byte_count"], runtime["loader"]["mode"]),
        )
        self.assertEqual(
            [(lib["soname"], lib["path"], lib["sha256"], lib["byte_count"], lib["resolution"][-1]["mode"])
             for lib in closure["libraries"]],
            [(lib["name"], lib["path"], lib["sha256"], lib["byte_count"], lib["mode"]) for lib in runtime["libraries"]],
        )
        # Every needed name is pinned, and the loader inputs cover exactly the pinned libraries.
        pinned = {lib["soname"] for lib in closure["libraries"]} | {interpreter["soname"]}
        needed = set(closure["executable"]["needed"]).union(*(lib["needed"] for lib in closure["libraries"]))
        self.assertLessEqual(needed, pinned)
        self.assertEqual(
            set(closure["loader_inputs"]["cache"]["entries"]), {lib["soname"] for lib in closure["libraries"]}
        )
        self.assertEqual(closure["loader_inputs"]["preload"], {"path": "/etc/ld.so.preload", "state": "absent"})
        self.assertFalse(
            [step for step in self._steps(closure) if step["kind"] != "symlink" and int(step["mode"], 8) & 0o022]
        )
        self.assertEqual({step["uid"] for step in self._steps(closure)}, {0})

    @staticmethod
    def _steps(closure):
        yield from closure["executable"]["resolution"]
        yield from closure["interpreter"]["resolution"]
        yield from closure["loader_inputs"]["cache"]["resolution"]
        for library in closure["libraries"]:
            yield from library["resolution"]

    def test_a_changed_installed_external_policy_file_is_refused_by_its_digest_pin(self):
        original = codex_native_external_bundle_policy_bytes()
        changed = original.replace(b'"cli_auth_credentials_store=file"', b'"cli_auth_credentials_store=keyring"')
        self.assertNotEqual(changed, original)

        class Resource:
            def read_bytes(self):
                return changed

        class Package:
            def joinpath(self, _name):
                return Resource()

        with mock.patch("caplab.revbench.codex.importlib.resources.files", return_value=Package()):
            with self.assertRaisesRegex(CodexAdapterError, "^codex_bundle_policy_digest_mismatch$"):
                codex_native_external_bundle_policy_bytes()

    def test_selection_is_by_exact_equality_with_an_installed_policy_never_by_name(self):
        v1, external = codex_native_bundle_policy(), codex_native_external_bundle_policy()
        installed = (v1, external)
        self.assertIs(pinned_bundle_policy_matching(copy.deepcopy(external), installed), external)
        self.assertIs(pinned_bundle_policy_matching(copy.deepcopy(v1), installed), v1)
        lookalikes = []
        renamed = copy.deepcopy(external)
        renamed["policy_id"] = v1["policy_id"]
        lookalikes.append(renamed)
        for edit in (
            lambda p: p["launcher"]["review_argv"].remove("cli_auth_credentials_store=file"),
            lambda p: p["credential_delivery"].update(initial_credentials_store="ephemeral"),
            lambda p: p["host_closure"]["libraries"][0].update(sha256="0" * 64),
            lambda p: p["containment"].update(adapter_path="/tmp/bwrap"),
            lambda p: p.update(extra="field"),
        ):
            changed = copy.deepcopy(external)
            edit(changed)
            lookalikes.append(changed)
        for index, candidate in enumerate(lookalikes):
            with self.subTest(index=index):
                self.assertIsNone(pinned_bundle_policy_matching(candidate, installed))
        self.assertIsNone(pinned_bundle_policy_matching({"not": float("nan")}, installed))


class ExternalProfileTests(unittest.TestCase):
    def test_closed_public_profile_validates_against_the_pinned_external_policy(self):
        profile = external_profile()
        self.assertEqual(validate_credential_profile(profile), profile)
        policy = codex_native_external_bundle_policy()
        self.assertEqual(validate_credential_profile(profile, policy=policy), profile)

    def test_profile_refuses_every_departure_from_the_selected_method(self):
        base = external_profile()
        refusals = {
            "extra private field": {**base, "provider_account_id_sha256": "a" * 64},
            "extra source path": {**base, "source_path": "/x"},
            "missing field": {k: v for k, v in base.items() if k != "lifetime_rule"},
            "other schema": {**base, "schema_version": "caplab-revbench-codex-credential-profile/1"},
            "other auth method": external_profile(auth_method="chatgpt"),
            "other provider": external_profile(provider="other"),
            "bad id": external_profile(profile_id="Not A Valid Id"),
            "ephemeral store": external_profile(initial_credentials_store="ephemeral"),
            "keyring store": external_profile(initial_credentials_store="keyring"),
            "v1 marker policy": external_profile(quarantine_profile="credential-private-text/v1"),
            "v3 marker policy": external_profile(quarantine_profile="credential-private-text/v3"),
            "other delivery": external_profile(delivery_method="codex-external-token-file/2"),
            "other lifetime rule": external_profile(lifetime_rule="fixed-300-seconds"),
            "other anchor schema": external_profile(private_anchor_schema="caplab-revbench-external-credential-anchors/2"),
        }
        for name, profile in refusals.items():
            with self.subTest(name), self.assertRaises(CodexAdapterError):
                validate_credential_profile(profile)

    def test_original_profile_validation_is_unchanged_and_cannot_pose_as_external(self):
        v1_profile = {
            "schema_version": "caplab-revbench-codex-credential-profile/1",
            "profile_id": "caplab-openai-revbench",
            "provider": "openai",
            "auth_method": "chatgpt",
            "identity_basis": "operator-declared-unverified-token-claims",
            "provider_account_id_sha256": "a" * 64,
            "provider_subject_sha256": "b" * 64,
            "identity_token_issuer": "https://auth.openai.com",
            "identity_token_audience": ["https://api.openai.com/v1"],
        }
        self.assertEqual(validate_credential_profile(v1_profile), v1_profile)
        # External fields under the original schema name, and the reverse, are both refused.
        with self.assertRaises(CodexAdapterError):
            validate_credential_profile({**external_profile(), "schema_version": v1_profile["schema_version"]})
        with self.assertRaises(CodexAdapterError):
            validate_credential_profile({**v1_profile, "schema_version": CODEX_EXTERNAL_CREDENTIAL_PROFILE_SCHEMA})
        # An external profile does not validate against the original policy's (absent) delivery description.
        with self.assertRaises(CodexAdapterError):
            validate_credential_profile(external_profile(), policy=codex_native_bundle_policy())


class RequiredLifetimeTests(unittest.TestCase):
    NOW = datetime(2026, 10, 3, 12, 0, 0, 400_000, tzinfo=UTC)

    def required(self, seconds_after_now: float) -> int:
        deadline = (self.NOW + timedelta(seconds=seconds_after_now)).replace(microsecond=0)
        return required_access_lifetime_seconds(deadline.strftime("%Y-%m-%dT%H:%M:%SZ"), self.NOW)

    def test_requirement_rounds_up_and_only_the_positive_minimum_is_raised_to_one(self):
        # NOW carries 0.4 s; a whole-second deadline k seconds later is k - 0.4 s away.
        self.assertEqual(self.required(1), 1)       # 0.6 s -> the one-second minimum
        self.assertEqual(self.required(2), 2)       # 1.6 s -> rounded up
        self.assertEqual(self.required(10), 10)     # 9.6 s -> 10
        self.assertEqual(self.required(86400), 86400)  # 86399.6 s -> 86400, the maximum
        deadline = (self.NOW.replace(microsecond=0) + timedelta(seconds=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertEqual(
            required_access_lifetime_seconds(deadline, self.NOW.replace(microsecond=0)), 7
        )  # an exact whole-second remainder is not inflated

    def test_elapsed_deadlines_and_deadlines_beyond_the_maximum_are_refused_not_truncated(self):
        for seconds, code in (
            (0, "external_credential_deadline_elapsed"),
            (-30, "external_credential_deadline_elapsed"),
            (86401, "external_credential_lifetime_exceeds_maximum"),
            (200000, "external_credential_lifetime_exceeds_maximum"),
        ):
            with self.subTest(seconds), self.assertRaisesRegex(CodexAdapterError, f"^{code}$"):
                self.required(seconds)

    def test_malformed_deadline_or_naive_clock_is_a_fixed_code(self):
        for value in ("2026-10-03T12:00:00", "2026-10-03 12:00:00Z", "tomorrow", None, 5):
            with self.subTest(value), self.assertRaisesRegex(CodexAdapterError, "^external_credential_deadline_invalid$"):
                required_access_lifetime_seconds(value, self.NOW)
        with self.assertRaisesRegex(CodexAdapterError, "^external_credential_clock_invalid$"):
            required_access_lifetime_seconds("2026-10-03T12:00:30Z", datetime(2026, 10, 3, 12, 0, 0))


class HostClosureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.uid = os.getuid()
        self.host = SyntheticHost(Path(self.temporary.name))

    def capture(self):
        return host_closure.capture_host_closure(SyntheticHost.EXECUTABLE, root=self.host.root)

    def verify(self, closure):
        return host_closure.verify_host_closure(closure, root=self.host.root, trusted_uid=self.uid)

    def refusal(self, closure) -> str:
        with self.assertRaises(host_closure.HostClosureError) as caught:
            self.verify(closure)
        return str(caught.exception)

    def test_capture_describes_the_whole_closure_and_verification_is_deterministic(self):
        closure = self.capture()
        self.assertEqual([lib["soname"] for lib in closure["libraries"]], ["libalpha.so.1", "libc.so.6"])
        self.assertEqual(closure["interpreter"]["pt_interp"], SyntheticHost.INTERPRETER)
        self.assertEqual(closure["interpreter"]["soname"], "ld-test.so.2")
        alpha = closure["libraries"][0]
        self.assertTrue(alpha["real_path"].endswith("libalpha.so.1.0"))
        self.assertIn("symlink", [step["kind"] for step in alpha["resolution"]])
        facts = self.verify(closure)
        self.assertEqual(facts, {"closure_sha256": host_closure.closure_sha256(closure), "member_count": 4})
        self.assertEqual(self.verify(copy.deepcopy(closure)), facts)

    def test_every_change_to_a_pinned_member_or_its_resolution_is_refused_by_category(self):
        def append_library(host):
            path = host.path(f"{host.LIBDIR}/libalpha.so.1.0")
            path.write_bytes(path.read_bytes() + b"x")

        def replace_executable(host):
            original = host.path(host.EXECUTABLE).read_bytes()
            host.write(host.EXECUTABLE, synthetic_elf(
                interpreter=host.INTERPRETER, needed=("libalpha.so.1", "libc.so.6"), padding=b"\0" * 4), 0o755)
            self.assertNotEqual(host.path(host.EXECUTABLE).read_bytes(), original)

        def retarget_library_link(host):
            link = host.path(f"{host.LIBDIR}/libalpha.so.1")
            link.unlink()
            host.write(f"{host.LIBDIR}/libalpha.so.2.0", host.path(f"{host.LIBDIR}/libalpha.so.1.0").read_bytes(), 0o644)
            os.symlink("libalpha.so.2.0", link)

        def retarget_interpreter_link(host):
            link = host.path("/usr/lib64/ld-test.so.2")
            link.unlink()
            os.symlink("../lib/x86_64-linux-gnu/libc.so.6", link)

        def delete_library(host):
            host.path(f"{host.LIBDIR}/libc.so.6").unlink()

        def loosen_directory(host):
            os.chmod(host.path(host.LIBDIR), 0o775)

        def set_setuid(host):
            os.chmod(host.path(host.EXECUTABLE), 0o4755)

        def add_preload(host):
            host.write("/etc/ld.so.preload", b"/lib/x86_64-linux-gnu/libevil.so\n", 0o644)

        def repoint_cache_entry(host):
            host.write_cache(replace={"libalpha.so.1": "/lib/x86_64-linux-gnu/libc.so.6"})

        def add_hwcap_variant(host):
            host.write_cache(extra=[("libalpha.so.1", "/lib/x86_64-linux-gnu/glibc-hwcaps/x86-64-v3/libalpha.so.1", 0x0303, 1)])

        def add_second_plain_entry(host):
            host.write_cache(extra=[("libc.so.6", "/lib/x86_64-linux-gnu/libalpha.so.1.0", 0x0303, 0)])

        cases = {
            "library bytes": (append_library, "host_closure_member_changed:libalpha.so.1"),
            "executable bytes": (replace_executable, "host_closure_member_changed:executable"),
            "library symlink retargeted": (retarget_library_link, "host_closure_member_changed:libalpha.so.1"),
            "interpreter symlink retargeted": (retarget_interpreter_link, "host_closure_member_changed:interpreter"),
            "library deleted": (delete_library, "host_closure_member_missing:libc.so.6"),
            "ancestor became group-writable": (loosen_directory, "host_closure_member_changed:"),
            "executable gained setuid": (set_setuid, "host_closure_member_changed:executable"),
            "global preload appeared": (add_preload, "host_closure_resolution_ambiguous:preload"),
            "cache entry repointed": (repoint_cache_entry, "host_closure_resolution_ambiguous:libalpha.so.1"),
            "hardware-capability variant appeared": (add_hwcap_variant, "host_closure_resolution_ambiguous:libalpha.so.1"),
            "second cache entry appeared": (add_second_plain_entry, "host_closure_resolution_ambiguous:libc.so.6"),
        }
        for name, (mutate, expected) in cases.items():
            with self.subTest(name):
                self.fresh_host()
                closure = self.capture()
                mutate(self.host)
                self.assertTrue(self.refusal(closure).startswith(expected), (name, self.refusal(closure)))

    def fresh_host(self):
        self.temporary.cleanup()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.host = SyntheticHost(Path(self.temporary.name))

    def test_a_closure_pinned_while_writable_or_foreign_owned_is_refused_at_launch(self):
        os.chmod(self.host.path(SyntheticHost.LIBDIR), 0o775)
        writable = self.capture()  # capture records facts; protection is enforced at verification
        self.assertEqual(self.refusal(writable), "host_closure_member_writable:interpreter")
        self.fresh_host()
        os.chmod(self.host.path(SyntheticHost.EXECUTABLE), 0o4755)
        privileged = self.capture()
        self.assertEqual(self.refusal(privileged), "host_closure_member_privileged:executable")
        self.fresh_host()
        closure = self.capture()
        with self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_member_writable:executable$"):
            host_closure.verify_host_closure(closure, root=self.host.root, trusted_uid=self.uid + 1)

    def test_unrelated_loader_cache_changes_do_not_refuse_the_pinned_closure(self):
        closure = self.capture()
        self.host.write_cache(
            replace={"libunrelated.so.3": "/lib/x86_64-linux-gnu/libother.so.9"},
            extra=[("libnew.so.1", "/lib/x86_64-linux-gnu/libnew.so.1", 0x0303, 0)],
        )
        self.assertEqual(self.verify(closure)["member_count"], 4)

    def test_capture_refuses_a_closure_it_cannot_close(self):
        self.host.write(f"{SyntheticHost.LIBDIR}/libalpha.so.1.0", synthetic_elf(
            needed=("libc.so.6",), soname="libalpha.so.1", runpath="/opt/elsewhere"), 0o644)
        with self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_resolution_ambiguous:libalpha.so.1$"):
            self.capture()
        self.fresh_host()
        self.host.write(f"{SyntheticHost.LIBDIR}/libc.so.6", synthetic_elf(
            needed=("libghost.so.9", "ld-test.so.2"), soname="libc.so.6"), 0o755)
        with self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_resolution_ambiguous:libghost.so.9$"):
            self.capture()
        self.fresh_host()
        self.host.write(SyntheticHost.EXECUTABLE, synthetic_elf(needed=("libc.so.6",)), 0o755)  # no PT_INTERP
        with self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_resolution_ambiguous:executable$"):
            self.capture()

    def test_refusal_codes_carry_a_category_and_a_public_member_id_but_no_path_or_content(self):
        closure = self.capture()
        host = self.host
        host.path(f"{SyntheticHost.LIBDIR}/libc.so.6").write_bytes(b"secret-looking-bytes")
        message = self.refusal(closure)
        self.assertRegex(message, r"^host_closure_[a-z_]+:[a-z0-9._-]+$")
        self.assertNotIn(self.temporary.name, message)
        self.assertNotIn("secret", message)

    def test_readers_agree_with_real_world_elf_and_cache_files(self):
        # The fabricated images are not the only evidence the readers understand real files.
        executable = Path("/usr/bin/true")
        cache = Path("/etc/ld.so.cache")
        if not executable.is_file() or not cache.is_file():
            self.skipTest("no standard dynamic executable or loader cache on this host")
        dynamic = host_closure.elf_dynamic(executable.read_bytes())
        self.assertIn("libc.so.6", dynamic["needed"])
        self.assertTrue(dynamic["interpreter"].startswith("/"))
        self.assertEqual((dynamic["rpath"], dynamic["runpath"]), ([], []))
        names = {entry["soname"] for entry in host_closure.parse_ld_so_cache(cache.read_bytes())}
        self.assertIn("libc.so.6", names)

    def test_readers_refuse_unsupported_or_truncated_images(self):
        for name, payload in {
            "not elf": b"MZ" + b"\0" * 100,
            "32-bit class": b"\x7fELF\x01\x01\x01" + b"\0" * 100,
            "big-endian": b"\x7fELF\x02\x02\x01" + b"\0" * 100,
            "truncated headers": synthetic_elf(needed=("libc.so.6",))[:100],
        }.items():
            with self.subTest(name), self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_elf_unsupported$"):
                host_closure.elf_dynamic(payload)
        with self.assertRaisesRegex(host_closure.HostClosureError, "^host_closure_cache_unsupported$"):
            host_closure.parse_ld_so_cache(b"ld.so-1.7.0" + b"\0" * 64)



class PrivateRuntimeCase(unittest.TestCase):
    """A fabricated external credential, its private anchors and a live runtime over them."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.ledger = self.parent / "ledger"
        self.ledger.mkdir(mode=0o700)
        self.credential_root = self.parent / "credentials-private"
        self.credential_root.mkdir(mode=0o700)
        self.document, self.account, self.subject = credential_fixture()
        self.write_source(self.document)
        self.write_anchors()

    def write_source(self, document, *, mode=0o600, name="source.json"):
        self.raw = json.dumps(document).encode()
        path = self.credential_root / name
        path.write_bytes(self.raw)
        path.chmod(mode)
        return path

    def write_anchors(self, *, name="anchors.json", mode=0o600, **overrides):
        anchors = {
            "schema_version": ANCHORS_SCHEMA,
            "profile_id": PROFILE_ID,
            "source_sha256": digest(self.raw),
            "provider_account_id_sha256": digest(self.account.encode()),
            "provider_subject_sha256": digest(self.subject.encode()),
            **overrides,
        }
        path = self.credential_root / name
        path.write_text(json.dumps(anchors))
        path.chmod(mode)
        return path

    def runtime(self, *, sources=None, anchors=None):
        return FilesystemLiveExecutionRuntime(
            self.ledger,
            credential_root=self.credential_root,
            credential_sources={PROFILE_ID: "source.json"} if sources is None else sources,
            credential_anchor_sources={PROFILE_ID: "anchors.json"} if anchors is None else anchors,
        )

    def assertFixedCode(self, error, *forbidden):
        """A refusal is a short stable code: no path, digest, claim or file text."""

        text = str(error)
        self.assertRegex(text, r"^[a-z][a-z0-9_]*(:[a-z0-9._-]+)?$")
        for value in (self.temporary.name, "source.json", "anchors.json", digest(self.raw), self.account, self.subject, *forbidden):
            self.assertNotIn(value, text)


class PrivateAnchorTests(PrivateRuntimeCase):
    def test_anchors_are_read_from_a_second_direct_child_bound_to_the_public_profile(self):
        anchors = self.runtime().credential_anchors(PROFILE_ID)
        self.assertEqual(
            anchors,
            {
                "source_sha256": digest(self.raw),
                "account_sha256": digest(self.account.encode()),
                "subject_sha256": digest(self.subject.encode()),
            },
        )

    def test_anchor_refusals_are_fixed_codes_that_leak_nothing(self):
        def rewrite(**overrides):
            self.write_anchors(**overrides)

        def drop(key):
            document = json.loads((self.credential_root / "anchors.json").read_text())
            del document[key]
            (self.credential_root / "anchors.json").write_text(json.dumps(document))

        def text(payload):
            (self.credential_root / "anchors.json").write_bytes(payload)
            (self.credential_root / "anchors.json").chmod(0o600)

        def link():
            os.link(self.credential_root / "anchors.json", self.credential_root / "alias.json")

        def symlink():
            (self.credential_root / "anchors.json").unlink()
            os.symlink(self.credential_root / "source.json", self.credential_root / "anchors.json")

        def loosen():
            (self.credential_root / "anchors.json").chmod(0o644)

        def remove():
            (self.credential_root / "anchors.json").unlink()

        def open_root():
            self.credential_root.chmod(0o755)

        good = (self.credential_root / "anchors.json").read_text()
        cases = {
            "mode 0644": (loosen, "credential_anchors_metadata_invalid"),
            "second hard link": (link, "credential_anchors_metadata_invalid"),
            "symlink to the source": (symlink, "credential_anchors_open_failed"),
            "missing file": (remove, "credential_anchors_open_failed"),
            "empty": (lambda: text(b""), "credential_anchors_metadata_invalid"),
            "oversized": (lambda: text(b" " * 5000), "credential_anchors_metadata_invalid"),
            "other profile": (lambda: rewrite(profile_id="caplab-another-profile"), "credential_anchors_profile_mismatch"),
            "other schema": (lambda: rewrite(schema_version="caplab-revbench-external-credential-anchors/2"), "credential_anchors_invalid"),
            "extra key": (lambda: rewrite(note="x"), "credential_anchors_invalid"),
            "missing key": (lambda: drop("source_sha256"), "credential_anchors_invalid"),
            "uppercase digest": (lambda: rewrite(source_sha256=digest(self.raw).upper()), "credential_anchors_invalid"),
            "short digest": (lambda: rewrite(provider_subject_sha256="abc"), "credential_anchors_invalid"),
            "duplicate key": (lambda: text(good.replace('"profile_id"', '"profile_id": "x", "profile_id"').encode()), "credential_anchors_invalid"),
            "not json": (lambda: text(b"not json"), "credential_anchors_invalid"),
            "not utf-8": (lambda: text(b"\xff\xfe{}"), "credential_anchors_invalid"),
            "root opened to group": (open_root, "credential_root_owner_or_mode_invalid"),
        }
        for name, (mutate, code) in cases.items():
            with self.subTest(name):
                self.setUp()
                runtime = self.runtime()
                mutate()
                with self.assertRaisesRegex(LiveExecutionCustodyError, f"^{code}$") as caught:
                    runtime.credential_anchors(PROFILE_ID)
                self.assertFixedCode(caught.exception)

    def test_anchors_must_be_provisioned_and_cannot_be_the_credential_source(self):
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_anchors_not_provisioned$"):
            self.runtime(anchors={}).credential_anchors(PROFILE_ID)
        # Same filename for both: the expected hashes would be read from the file they check.
        same = self.runtime(sources={PROFILE_ID: "source.json"}, anchors={PROFILE_ID: "source.json"})
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_anchors_not_independent$"):
            same.credential_anchors(PROFILE_ID)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_anchors_name_invalid$"):
            self.runtime(anchors={PROFILE_ID: "nested/anchors.json"})
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_root_required$"):
            FilesystemLiveExecutionRuntime(self.ledger, credential_anchor_sources={PROFILE_ID: "anchors.json"})
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_profile_id_invalid$"):
            self.runtime(anchors={"Not Valid": "anchors.json"})
        with self.assertRaisesRegex(LiveExecutionCustodyError, "^credential_profile_id_invalid$"):
            self.runtime().credential_anchors("Not Valid")



def open_descriptors() -> int:
    return len(os.listdir("/proc/self/fd"))


def jwt_claims(token: str) -> dict:
    import base64

    part = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))


class ExternalLeaseTests(PrivateRuntimeCase):
    def lease(self, deadline=None, profile=None, runtime=None):
        return open_external_revbench_credential(
            runtime=runtime or self.runtime(),
            profile=external_profile() if profile is None else profile,
            execution_deadline_at=deadline or deadline_in(600),
        )

    def refusal(self, **kwargs) -> str:
        before = open_descriptors()
        with self.assertRaises(CodexAdapterError) as caught:
            with self.lease(**kwargs):
                self.fail("the lease must be refused")
        self.assertEqual(open_descriptors(), before, "a refused lease leaks no descriptor")
        self.assertFixedCode(caught.exception)
        return str(caught.exception)

    def test_lease_exposes_the_sealed_external_projection_and_leaves_the_source_alone(self):
        import fcntl

        source = self.credential_root / "source.json"
        before = (source.read_bytes(), source.stat().st_mtime_ns, source.stat().st_ino)
        claims = jwt_claims(self.document["tokens"]["id_token"])
        self.assertLess(claims["exp"], datetime.now(UTC).timestamp())  # the ID token is already expired
        descriptors = open_descriptors()
        with self.lease() as lease:
            descriptor = lease.descriptor
            delivered = json.loads(os.pread(descriptor, 1 << 16, 0))
            seals = fcntl.fcntl(descriptor, fcntl.F_GET_SEALS)
            with self.assertRaises(OSError):
                os.pwrite(descriptor, b"x", 0)
        self.assertEqual(delivered["auth_mode"], "chatgptAuthTokens")
        self.assertEqual(delivered["tokens"]["refresh_token"], "")
        self.assertEqual(
            {k: v for k, v in delivered["tokens"].items() if k != "refresh_token"},
            {k: v for k, v in self.document["tokens"].items() if k != "refresh_token"},
        )
        self.assertEqual(delivered["last_refresh"], self.document["last_refresh"])
        self.assertTrue(seals & fcntl.F_SEAL_WRITE and seals & fcntl.F_SEAL_GROW and seals & fcntl.F_SEAL_SHRINK)
        self.assertEqual((source.read_bytes(), source.stat().st_mtime_ns, source.stat().st_ino), before)
        self.assertEqual(open_descriptors(), descriptors)
        with self.assertRaises(OSError):
            os.fstat(descriptor)  # closed with its owning context
        with self.assertRaisesRegex(CodexAdapterError, "^external_credential_lease_closed$"):
            lease.descriptor
        with self.assertRaisesRegex(CodexAdapterError, "^external_credential_lease_closed$"):
            lease.stream_quarantine()

    def test_the_original_profile_still_refuses_an_expired_identity_token(self):
        # The expired-ID allowance belongs to the external profile only.
        from tests.test_revbench_codex import (
            LIVE_ACCOUNT, LIVE_SUBJECT, credential_memfd, synthetic_live_credential)
        import base64

        document = json.loads(synthetic_live_credential())
        header, payload, signature = document["tokens"]["id_token"].split(".")
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        claims.update(iat=1_700_000_000, exp=1_700_000_100)
        document["tokens"]["id_token"] = ".".join(
            (header, base64.urlsafe_b64encode(canonical_json(claims)).rstrip(b"=").decode(), signature)
        )
        source = self.credential_root / "v1-source.json"
        source.write_bytes(canonical_json(document))
        source.chmod(0o600)
        profile = {
            "schema_version": "caplab-revbench-codex-credential-profile/1",
            "profile_id": "caplab-openai-revbench",
            "provider": "openai",
            "auth_method": "chatgpt",
            "identity_basis": "operator-declared-unverified-token-claims",
            "provider_account_id_sha256": sha256_hex(LIVE_ACCOUNT.encode()),
            "provider_subject_sha256": sha256_hex(LIVE_SUBJECT.encode()),
            "identity_token_issuer": "https://auth.openai.com",
            "identity_token_audience": ["https://api.openai.com/v1"],
        }
        with self.assertRaisesRegex(CodexAdapterError, "credential_identity_token_expiry_invalid"):
            with credential_memfd(source, profile, credential_root=self.credential_root):
                self.fail("v1 must keep refusing an expired identity token")

    def test_access_token_must_cover_the_retained_deadline(self):
        with self.lease(deadline_in(1800)):
            pass  # the fixture's access token lives about an hour
        self.assertEqual(self.refusal(deadline=deadline_in(7200)), "external_credential_access_lifetime_insufficient")
        self.assertEqual(self.refusal(deadline=deadline_in(-5)), "external_credential_deadline_elapsed")
        self.assertEqual(self.refusal(deadline=deadline_in(90000)), "external_credential_lifetime_exceeds_maximum")
        self.assertEqual(self.refusal(deadline="soon"), "external_credential_deadline_invalid")

    def test_private_anchors_not_the_credential_file_decide_what_is_accepted(self):
        for name, overrides, code in (
            ("source hash", {"source_sha256": digest(b"another file")}, "external_credential_source_hash_mismatch"),
            ("account", {"provider_account_id_sha256": digest(b"another account")}, "external_credential_account_mismatch"),
            ("subject", {"provider_subject_sha256": digest(b"another subject")}, "external_credential_subject_mismatch"),
        ):
            with self.subTest(name):
                self.write_anchors(**overrides)
                self.assertEqual(self.refusal(), code)
        self.write_anchors()
        with self.lease():
            pass
        # A source edited after anchoring is a different file, whatever it still parses as.
        edited = json.loads(self.raw)
        edited["last_refresh"] = "2026-09-10T00:00:00Z"
        self.write_source(edited)
        self.assertEqual(self.refusal(), "external_credential_source_hash_mismatch")

    def test_missing_unprovisioned_or_misplaced_inputs_are_refused_before_any_read(self):
        (self.credential_root / "anchors.json").unlink()
        self.assertEqual(self.refusal(), "credential_anchors_open_failed")
        self.write_anchors()
        self.assertEqual(self.refusal(runtime=self.runtime(anchors={})), "credential_anchors_not_provisioned")
        self.assertEqual(self.refusal(runtime=self.runtime(sources={})), "credential_profile_not_provisioned")
        self.assertEqual(self.refusal(profile={}), "credential_profile_shape_invalid")
        self.assertEqual(
            self.refusal(profile=external_profile(schema_version="caplab-revbench-codex-credential-profile/1")),
            "credential_profile_shape_invalid",
        )

    def test_source_and_root_checks_of_the_original_seam_are_kept(self):
        source = self.credential_root / "source.json"
        source.chmod(0o640)
        self.assertEqual(self.refusal(), "external_credential_source_metadata_invalid")
        source.chmod(0o600)
        os.link(source, self.credential_root / "second-name.json")
        self.assertEqual(self.refusal(), "external_credential_source_metadata_invalid")
        (self.credential_root / "second-name.json").unlink()
        source.write_bytes(b" " * 70000)
        source.chmod(0o600)
        self.write_anchors(source_sha256=digest(source.read_bytes()))
        self.assertEqual(self.refusal(), "external_credential_source_metadata_invalid")
        self.write_source(self.document)
        self.write_anchors()
        source.unlink()
        os.symlink(self.credential_root / "second.json", source)
        self.assertRegex(self.refusal(), r"^external_credential_(source_path|input)_invalid$")
        source.unlink()
        self.write_source(self.document)
        runtime = self.runtime()  # constructed while the root is private, as in a real run
        self.credential_root.chmod(0o755)
        self.assertEqual(self.refusal(runtime=runtime), "credential_root_owner_or_mode_invalid")

    def test_each_stream_gets_its_own_guard_and_the_source_refresh_token_stays_guarded(self):
        tokens = self.document["tokens"]
        with self.lease() as lease:
            first, second = lease.stream_quarantine(), lease.stream_quarantine()
            self.assertIsNot(first, second)
            token = tokens["access_token"].encode()
            leaked = first.feed(b"prefix " + token[:20]) + first.feed(token[20:] + b" tail") + first.finish()
            self.assertTrue(first.quarantined)
            self.assertNotIn(token, leaked)
            # A tripped guard cannot taint another stream's guard.
            self.assertEqual(second.feed(b"ordinary output") + second.finish(), b"ordinary output")
            self.assertFalse(second.quarantined)
            # The empty refresh token is what the native process sees; the real one stays a marker.
            refresh = tokens["refresh_token"].encode()
            guard = lease.stream_quarantine()
            guard.feed(refresh)
            guard.finish()
            self.assertTrue(guard.quarantined)
            for text in (b"stdout is clean", b"stderr is clean"):
                lease.assert_streams_safe(text, text)
            for stdout, stderr in ((token, b""), (b"", refresh), (b"", self.account.encode())):
                with self.subTest(stdout=stdout[:8], stderr=stderr[:8]), self.assertRaisesRegex(
                    CodexAdapterError, "^credential_secret_quarantine$"
                ):
                    lease.assert_streams_safe(stdout, stderr)
            with self.assertRaisesRegex(CodexAdapterError, "^credential_quarantine_stream_not_bytes$"):
                lease.assert_streams_safe("text", b"")

    def test_marker_policy_v2_exempts_declared_categories_but_never_a_private_equal_occurrence(self):
        from tests.test_codex_external_credential import with_claims

        auth = "https://api.openai.com/auth"
        categorized = with_claims(
            self.document,
            lambda claims: (claims.update(scope="openid profile"), claims[auth].update(chatgpt_plan_type="plus")),
        )
        private_equal = with_claims(
            categorized, lambda claims: claims.update(name="plus")
        )  # a private name equal to the plan category
        probe = b"scope openid, plan plus"
        for document, plus_blocked in ((categorized, False), (private_equal, True)):
            with self.subTest(plus_blocked=plus_blocked):
                self.write_source(document)
                self.write_anchors()
                with self.lease() as lease:
                    gate = lease.stream_quarantine()
                    gate.feed(probe)
                    gate.finish()
                    self.assertIs(gate.quarantined, plus_blocked)
                    other = lease.stream_quarantine()
                    other.feed(b"scope openid")
                    other.finish()
                    self.assertFalse(other.quarantined)  # the scope category is exempt in both



def process_claim(runtime, logical_argv, *, kind="version-probe"):
    """A claimed process slot for ``logical_argv``; returns (plan, intent)."""

    from tests.test_revbench_live_custody import LiveExecutionCustodyTests

    helper = LiveExecutionCustodyTests("test_credential_mapping_requires_one_configured_private_root")
    scope = helper._launch_plan(process_kind=kind)["effect_scope"]
    plan = codex.build_live_launch_plan(
        scope,
        logical_argv=logical_argv,
        normalized_containment_argv=logical_argv,
        stdin=b"",
        contained_environment={},
        runtime_ref_sha256="d" * 64,
        apparatus_sha256="4" * 64,
        command_ref_sha256="e" * 64,
        credential_profile_id=PROFILE_ID,
        credential_profile_sha256="f" * 64,
        timeout_seconds=5,
        execution_deadline_at="2099-01-01T00:00:00Z",
        stdout_limit=1024,
        stderr_limit=1024,
    )
    intent = helper._execution_intent("7", plan, custody_domain_id=runtime.custody_domain_id)
    intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"
    return plan, intent


def run_claimed(capture, logical_argv, **kwargs):
    options = {"credential": None, "monotonic_deadline": float("inf"), **kwargs}
    return codex._run_owned_process(
        logical_argv,
        logical_argv,
        logical_argv,
        b"",
        contained_environment={},
        runtime_ref_sha256="d" * 64,
        apparatus_sha256="4" * 64,
        command_ref_sha256="e" * 64,
        credential_profile_id=PROFILE_ID,
        credential_profile_sha256="f" * 64,
        pass_fds=(),
        capture=capture,
        **options,
    )


class HostClosureLaunchBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        ledger = Path(self.temporary.name) / "ledger"
        ledger.mkdir(mode=0o700)
        self.runtime = FilesystemLiveExecutionRuntime(ledger)

    def host_closure_of_true(self):
        try:
            return host_closure.capture_host_closure("/usr/bin/true")
        except host_closure.HostClosureError:
            self.skipTest("this host has no capturable standard dynamic executable")

    def synthetic_closure(self):
        host_root = Path(self.temporary.name) / "synthetic-host"
        host_root.mkdir()
        host = SyntheticHost(host_root)
        return host_closure.capture_host_closure(SyntheticHost.EXECUTABLE, root=host.root)

    def test_a_missing_member_refuses_before_any_process_exists_and_the_refusal_is_retained(self):
        closure = self.synthetic_closure()  # its executable path does not exist on this host
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            with (
                capture,
                mock.patch(
                    "caplab.revbench.codex.subprocess.Popen",
                    side_effect=AssertionError("unexpected process launch"),
                ) as popen,
                mock.patch(
                    "caplab.revbench.codex.os.killpg",
                    side_effect=AssertionError("unexpected process signal"),
                ) as killpg,
            ):
                observation = run_claimed(capture, ["/usr/bin/true"], host_closure=closure)
            popen.assert_not_called()
            killpg.assert_not_called()
        self.assertEqual((observation.termination, observation.invocation_state), ("preflight-refused", "not-invoked"))
        with self.runtime.claim_execution(intent) as execution:
            recovered = execution.claim_process(plan)
        self.assertIsInstance(recovered, RecoveredProcessCapture)
        check = recovered.host_closure_check
        self.assertEqual(check["result"], "refused")
        self.assertEqual(check["refusal_code"], "host_closure_member_missing:executable")
        self.assertEqual(check["closure_sha256"], host_closure.closure_sha256(closure))
        self.assertEqual(recovered.completion["invocation_state"], "not-invoked")

    def test_a_drifted_member_is_detected_at_the_launch_boundary_not_at_capture_time(self):
        closure = self.host_closure_of_true()
        drifted = copy.deepcopy(closure)
        drifted["libraries"][0]["sha256"] = "0" * 64  # the host file no longer matches the pin
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            with (
                capture,
                mock.patch(
                    "caplab.revbench.codex.subprocess.Popen",
                    side_effect=AssertionError("unexpected process launch"),
                ) as popen,
                mock.patch(
                    "caplab.revbench.codex.os.killpg",
                    side_effect=AssertionError("unexpected process signal"),
                ) as killpg,
            ):
                observation = run_claimed(capture, ["/usr/bin/true"], host_closure=drifted)
            popen.assert_not_called()
            killpg.assert_not_called()
            recovered = execution.claim_process(plan)
        self.assertEqual(observation.termination, "preflight-refused")
        self.assertRegex(recovered.host_closure_check["refusal_code"], r"^host_closure_member_changed:[a-z0-9._-]+$")

    def test_a_passed_check_is_retained_before_the_launch_and_read_back_on_recovery(self):
        closure = self.host_closure_of_true()
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            observation = run_claimed(capture, ["/usr/bin/true"], host_closure=closure)
        self.assertEqual((observation.termination, observation.exit_code), ("exited", 0))
        with self.runtime.claim_execution(intent) as execution:
            recovered = execution.claim_process(plan)
        check = recovered.host_closure_check
        self.assertEqual((check["result"], check["refusal_code"]), ("verified", None))
        self.assertEqual(check["member_count"], 2 + len(closure["libraries"]))
        self.assertEqual(check["closure_sha256"], host_closure.closure_sha256(closure))
        self.assertLessEqual(check["checked_at"], recovered.completion["launch_attempted_at"])
        self.assertEqual(recovered.invocation_state, "invoked")

    def test_a_policy_without_a_closure_records_no_check(self):
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        with self.runtime.claim_execution(intent) as execution:
            run_claimed(execution.claim_process(plan), ["/usr/bin/true"])
            recovered = execution.claim_process(plan)
        self.assertIsNone(recovered.host_closure_check)

    def test_a_crash_after_the_check_leaves_an_uncertain_capture_that_still_carries_it(self):
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        document = {
            "schema_version": "caplab-revbench-host-closure-check/1",
            "process_id": live_process(plan),
            "closure_sha256": "a" * 64,
            "member_count": 6,
            "checked_at": "2026-10-03T00:00:00Z",
            "result": "verified",
            "refusal_code": None,
        }
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            capture.record_host_closure_check(document)
            capture.close()  # the executor dies before a completion is written
        with self.runtime.claim_execution(intent) as execution:
            recovered = execution.claim_process(plan)
        self.assertEqual((recovered.invocation_state, recovered.termination), ("uncertain", "executor-interrupted"))
        self.assertEqual(recovered.host_closure_check, document)

    def test_the_retained_record_is_closed_and_written_once(self):
        plan, intent = process_claim(self.runtime, ["/usr/bin/true"])
        good = {
            "schema_version": "caplab-revbench-host-closure-check/1",
            "process_id": live_process(plan),
            "closure_sha256": "a" * 64,
            "member_count": 6,
            "checked_at": "2026-10-03T00:00:00Z",
            "result": "refused",
            "refusal_code": "host_closure_member_changed:libc.so.6",
        }
        bad = {
            "other process": {**good, "process_id": "process-" + "9" * 64},
            "extra field": {**good, "path": "/etc/passwd"},
            "missing field": {k: v for k, v in good.items() if k != "member_count"},
            "other schema": {**good, "schema_version": "caplab-revbench-host-closure-check/2"},
            "short digest": {**good, "closure_sha256": "abc"},
            "negative count": {**good, "member_count": -1},
            "huge count": {**good, "member_count": 65},
            "boolean count": {**good, "member_count": True},
            "bad time": {**good, "checked_at": "now"},
            "path in refusal": {**good, "refusal_code": "host_closure_member_changed:/etc/passwd"},
            "free text refusal": {**good, "refusal_code": "the libc changed"},
            "refused without code": {**good, "refusal_code": None},
            "verified with code": {**good, "result": "verified"},
            "unknown result": {**good, "result": "maybe"},
        }
        with self.runtime.claim_execution(intent) as execution:
            capture = execution.claim_process(plan)
            for name, document in bad.items():
                with self.subTest(name), self.assertRaises(LiveExecutionCustodyError):
                    capture.record_host_closure_check(document)
            capture.record_host_closure_check(good)
            with self.assertRaisesRegex(LiveExecutionCustodyError, "^process_capture_closed$"):
                capture.record_host_closure_check(good)
            capture.close()


def live_process(plan):
    from caplab.revbench.custody import live_process_id

    return live_process_id(plan)


class DirectLaunchWiringTests(unittest.TestCase):
    """``run_codex_process`` with synthetic members: staged for v1, in place for the external bundle."""

    def setUp(self):
        from tests.test_revbench_codex import make_synthetic_bundle_fixture, synthetic_clean_apparatus

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        ledger = self.root / "ledger"
        ledger.mkdir(mode=0o700)
        self.runtime = FilesystemLiveExecutionRuntime(ledger)
        self.apparatus = synthetic_clean_apparatus()
        self.make_fixture = make_synthetic_bundle_fixture

    def bundle_for(self, base_policy):
        policy, members = self.make_fixture(self.root, base_policy=base_policy)
        bundle = codex.CodexExecutionBundle(
            runtime_ref_sha256="d" * 64,
            apparatus_sha256=sha256_hex(canonical_json(self.apparatus)),
            review_command_ref_sha256="e" * 64,
            version_command_ref_sha256="c" * 64,
            credential_profile_id=PROFILE_ID,
            credential_profile_sha256="f" * 64,
            executable=members["executable"],
            adapter=members["adapter"],
            adapter_loader=members["adapter-loader"],
            adapter_libraries=tuple(
                (lib["name"], members[f"adapter-library:{lib['name']}"]) for lib in policy["adapter_runtime"]["libraries"]
            ),
            ca_certificates=members["resource:ca_certificates"],
            resolver=members["resource:resolver"],
            nsswitch=members["resource:nsswitch"],
            response_schema=canonical_json(policy["response_schema"]),
            environment=dict(policy["environment"]),
            bundle_policy_id=policy["policy_id"],
        )
        return policy, bundle

    def launched_argv(self, base_policy, patched_name):
        policy, bundle = self.bundle_for(base_policy)
        logical = ["codex", "--version"]
        plan = codex.build_live_launch_plan(
            {
                "schema_version": "caplab-revbench-live-effect-scope/1",
                "manifest_sha256": "6" * 64,
                "experiment_id": "revbench-example",
                "binding_id": "bnd-" + "8" * 64,
                "case_id": "case-a",
                "arm": "control",
                "assignment_index": 0,
                "process_kind": "version-probe",
            },
            logical_argv=logical,
            normalized_containment_argv=normalized_codex_containment_argv(logical, policy=policy),
            stdin=b"",
            contained_environment={},
            runtime_ref_sha256=bundle.runtime_ref_sha256,
            apparatus_sha256=bundle.apparatus_sha256,
            command_ref_sha256=bundle.version_command_ref_sha256,
            credential_profile_id=bundle.credential_profile_id,
            credential_profile_sha256=bundle.credential_profile_sha256,
            timeout_seconds=5,
            execution_deadline_at="2099-01-01T00:00:00Z",
            stdout_limit=1024,
            stderr_limit=1024,
        )
        from tests.test_revbench_live_custody import LiveExecutionCustodyTests

        helper = LiveExecutionCustodyTests("test_credential_mapping_requires_one_configured_private_root")
        intent = helper._execution_intent("7", plan, custody_domain_id=self.runtime.custody_domain_id)
        intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"
        launched, events = [], []
        facts = {"closure_sha256": "a" * 64, "member_count": 6}

        def popen(argv, **kwargs):
            events.append("popen")
            launched.append((list(argv), kwargs))
            raise OSError("synthetic: no process is started")

        def verify(pinned):
            events.append("verify")
            return facts

        with (
            mock.patch(f"caplab.revbench.codex.{patched_name}", return_value=copy.deepcopy(policy)),
            mock.patch("caplab.revbench.codex.execution_apparatus_receipt", return_value=self.apparatus),
            mock.patch("caplab.revbench.codex.verify_host_closure", side_effect=verify),
            mock.patch("caplab.revbench.codex.subprocess.Popen", side_effect=popen),
            self.runtime.claim_execution(intent) as execution,
        ):
            capture = execution.claim_process(plan)
            observation = codex.run_codex_process(
                logical, b"", bundle=bundle, capture=capture, credential=None, monotonic_deadline=float("inf"))
        return policy, launched, events, observation

    def test_original_bundle_launches_through_its_staged_loader_and_checks_no_host_closure(self):
        policy, launched, events, observation = self.launched_argv(codex_native_bundle_policy(), "codex_native_bundle_policy")
        argv = launched[0][0]
        self.assertIn("caplab-revbench-codex-adapter-", argv[0])
        self.assertEqual(argv[1], "--library-path")
        self.assertEqual(events, ["popen"])
        self.assertEqual(observation.termination, "spawn-failure")

    def test_external_bundle_launches_the_pinned_host_path_directly_after_the_closure_check(self):
        policy, launched, events, observation = self.launched_argv(
            codex_native_external_bundle_policy(), "codex_native_external_bundle_policy")
        (argv, kwargs), = launched
        self.assertEqual(events, ["verify", "popen"])  # the check immediately precedes the launch
        self.assertEqual(argv[0], "/usr/bin/bwrap")
        self.assertNotIn("--library-path", argv)
        self.assertFalse([token for token in argv if "caplab-revbench-codex-adapter-" in token])
        self.assertEqual(kwargs["env"], {})  # an empty environment closes the loader's variables
        self.assertEqual(argv[1:3], ["--unshare-all", "--hostname"])
        self.assertEqual(observation.termination, "spawn-failure")

    def test_external_launch_stages_nothing(self):
        with mock.patch("caplab.revbench.codex.tempfile.TemporaryDirectory", side_effect=AssertionError("staged")):
            self.launched_argv(codex_native_external_bundle_policy(), "codex_native_external_bundle_policy")



class ExternalLiveFlowTests(PrivateRuntimeCase):
    """prepare -> execute -> score for the external-token bundle, with a fake process runner.

    The runner stands in for ``run_codex_process`` at the process boundary; everything else
    - policy selection, profile agreement, the post-intent credential lease, launch plans,
    the retained host-closure check, custody and evidence validation - is the real code.
    """

    def setUp(self):
        super().setUp()
        self.build()

    def build(self, *, policy_edit=None, profile=None, base_policy=None, registered_policy_edit=None):
        from tests.test_revbench import MemoryRegistrar, make_spec, registered
        from tests.test_revbench_codex import (
            make_live_codex_binding, make_synthetic_bundle_fixture, synthetic_clean_apparatus)
        from caplab.revbench import prepare

        bundle_root = self.parent / f"bundle-{len(os.listdir(self.parent))}"
        bundle_root.mkdir()
        policy, members = make_synthetic_bundle_fixture(
            bundle_root, base_policy=base_policy or codex_native_external_bundle_policy())
        if policy_edit is not None:
            policy_edit(policy)
        self.policy = policy
        self.registrar = MemoryRegistrar()
        registered_policy = copy.deepcopy(policy)
        if registered_policy_edit is not None:
            registered_policy_edit(registered_policy)
        binding, native_ref = make_live_codex_binding(
            self.registrar, policy=registered_policy, member_bytes=members,
            credential_profile=external_profile() if profile is None else profile)
        with self.installed(policy):
            self.manifest = prepare(
                make_spec(self.registrar, binding=binding, native_system_contract_ref=native_ref),
                self.registrar)
        self.apparatus = synthetic_clean_apparatus()
        self.apparatus_ref = registered(
            self.registrar, self.apparatus["apparatus_id"], self.apparatus,
            kind="execution-apparatus-receipt", schema="caplab-revbench-execution-apparatus/1")

    def installed(self, policy, *, v1=None):
        """Make ``policy`` the installed external policy (and optionally a v1 stand-in)."""

        stack = mock.patch.multiple(
            "caplab.revbench._core",
            codex_native_external_bundle_policy=mock.Mock(return_value=copy.deepcopy(policy)),
        )
        return stack

    def authorization(self, runtime, **limits):
        from tests.test_revbench import make_execution_authorization

        return make_execution_authorization(
            self.registrar, self.manifest, apparatus_ref=self.apparatus_ref,
            custody_domain_id=runtime.custody_domain_id, limits_override=limits or None)

    def execute(self, runner, *, runtime=None, authorization=None, **limits):
        from caplab.revbench import execute

        runtime = runtime or self.runtime()
        authorization = authorization or self.authorization(runtime, **limits)
        with (
            self.installed(self.policy),
            mock.patch("caplab.revbench.execution.run_codex_process", side_effect=runner),
            mock.patch("caplab.revbench.execution.execution_apparatus_receipt", return_value=self.apparatus),
        ):
            return execute(self.manifest, authorization, self.registrar, live_runtime=runtime)

    def score(self, reviews, policy=None):
        from caplab.revbench import score

        with self.installed(self.policy if policy is None else policy):
            return score(self.manifest, reviews, self.registrar)

    def runner(self, mode="valid", calls=None):
        """A process runner that behaves like the real one at the custody and lease seams."""

        from caplab.revbench.codex import CodexProcessObservation

        policy = self.policy
        calls = [] if calls is None else calls
        self.delivered = []

        def fake(logical_argv, stdin, *, bundle, capture, credential, monotonic_deadline):
            stamp = capture.intent["intent_recorded_at"]
            kind = capture.intent["launch_plan"]["effect_scope"]["process_kind"]
            self.assertGreater(monotonic_deadline, 0)
            self.assertEqual(bundle.bundle_policy_id, policy["policy_id"])
            check = {
                "schema_version": "caplab-revbench-host-closure-check/1",
                "process_id": capture.intent["process_id"],
                "closure_sha256": host_closure.closure_sha256(policy.get("host_closure", {"pins": "none"})),
                "member_count": 6,
                "checked_at": stamp,
                "result": "verified",
                "refusal_code": None,
            }
            if mode == "wrong-closure":
                check["closure_sha256"] = "9" * 64
            if mode == "late-check":
                check["checked_at"] = "2099-01-01T00:00:00Z"
            if mode == "drift":
                check.update(result="refused", member_count=0, refusal_code="host_closure_member_changed:libc.so.6")
            if mode == "refused-but-invoked":
                check.update(result="refused", member_count=0, refusal_code="host_closure_member_changed:libc.so.6")
            if mode != "omit-check":
                capture.record_host_closure_check(check)

            def complete(stdout, stderr, *, invoked, termination="exited", complete_streams=True, exit_code=0):
                capture.write_stdout(stdout)
                capture.write_stderr(stderr)
                state = "invoked" if invoked else "not-invoked"
                capture.complete({
                    "schema_version": "caplab-revbench-live-process-completion/1",
                    "process_id": capture.intent["process_id"],
                    "launch_attempted_at": stamp,
                    "process_started_at": stamp if invoked else None,
                    "process_completed_at": stamp if invoked else None,
                    "completion_recorded_at": stamp,
                    "stdout_complete": complete_streams,
                    "stderr_complete": complete_streams,
                    "exit_code": exit_code if invoked else None,
                    "termination": termination,
                    "invocation_state": state,
                })
                calls.append((kind, logical_argv[0], invoked))
                return CodexProcessObservation(
                    stamp if invoked else None, stamp if invoked else None, stamp if invoked else None,
                    stamp, stdout, complete_streams, stderr, complete_streams,
                    exit_code if invoked else None, termination, state)

            if mode == "drift":
                capture.write_stdout(b"")
                capture.write_stderr(b"")
                capture.complete({
                    "schema_version": "caplab-revbench-live-process-completion/1",
                    "process_id": capture.intent["process_id"],
                    "launch_attempted_at": None, "process_started_at": None, "process_completed_at": None,
                    "completion_recorded_at": stamp, "stdout_complete": True, "stderr_complete": True,
                    "exit_code": None, "termination": "preflight-refused", "invocation_state": "not-invoked",
                })
                calls.append((kind, logical_argv[0], False))
                return CodexProcessObservation(None, None, None, stamp, b"", True, b"", True, None,
                                               "preflight-refused", "not-invoked")
            if kind == "version-probe":
                self.assertIsNone(credential)
                return complete(b"codex-cli 0.147.0\n", b"", invoked=True)
            self.assertIsNotNone(credential)
            delivered = json.loads(os.pread(credential.descriptor, 1 << 16, 0))
            self.delivered.append(delivered)
            native_input = json.loads(stdin)
            oracle, value = native_input["requirement"], native_input["artifact"]
            for token in oracle["pointer"].strip("/").split("/"):
                value = value[token]
            clean = value >= oracle["minimum"]
            response = {"schema_version": "caplab-revbench-native-response/1",
                        "verdict": "clean" if clean else "defect",
                        "anchors": [] if clean else [oracle["pointer"]]}
            events = [
                {"type": "thread.started", "thread_id": "thread-1"}, {"type": "turn.started"},
                {"type": "item.completed", "item": {"id": "item-1", "type": "agent_message",
                                                    "text": canonical_json(response).decode()}},
                {"type": "turn.completed", "usage": {"input_tokens": 1}},
            ]
            stdout = b"".join(canonical_json(event) + b"\n" for event in events)
            if mode == "quarantine" and not any(c[0] == "native-review" for c in calls):
                token = self.document["tokens"]["access_token"].encode()
                gate = credential.stream_quarantine()
                stdout = gate.feed(b"safe prefix:" + token[:30]) + gate.feed(token[30:] + b":unsafe tail") + gate.finish()
                self.assertTrue(gate.quarantined)
                return complete(stdout, b"", invoked=True, termination="privacy-quarantine",
                                complete_streams=False, exit_code=-15)
            return complete(stdout, b"", invoked=True)

        return fake

    def surfaces(self, runtime, reviews):
        custody = b"\n".join(p.read_bytes() for p in sorted(runtime.root.rglob("*")) if p.is_file() and not p.is_symlink())
        return custody + b"\n".join(self.registrar.documents.values()) + canonical_json(reviews)

    def private_values(self):
        tokens = self.document["tokens"]
        return [
            tokens["id_token"], tokens["access_token"], tokens["refresh_token"], self.account,
            self.subject, digest(self.raw), str(self.credential_root), "source.json", "anchors.json",
            digest(self.account.encode()), digest(self.subject.encode()),
        ]

    def test_the_external_profile_runs_end_to_end_with_a_leased_sealed_projection(self):
        runtime = self.runtime()
        calls = []
        reviews = self.execute(self.runner(calls=calls), runtime=runtime)
        measurement = self.score(reviews)
        self.assertEqual(reviews["status"], "complete")
        self.assertEqual(len(reviews["attempts"]), 4)
        self.assertEqual(len(calls), 8)
        self.assertEqual(measurement["disposition"], "complete")
        self.assertEqual(len(self.delivered), 4)
        for delivered in self.delivered:  # the native process was handed the external projection, every time
            self.assertEqual(delivered["auth_mode"], "chatgptAuthTokens")
            self.assertEqual(delivered["tokens"]["refresh_token"], "")
            self.assertEqual(delivered["tokens"]["access_token"], self.document["tokens"]["access_token"])
        surfaces = self.surfaces(runtime, reviews)
        for value in self.private_values():
            self.assertNotIn(value.encode(), surfaces)

    def test_every_process_receipt_retains_the_check_of_the_pinned_closure(self):
        reviews = self.execute(self.runner())
        pinned = host_closure.closure_sha256(self.policy["host_closure"])
        self.assertEqual(len(reviews["process_receipt_refs"]), 8)
        for ref in reviews["process_receipt_refs"]:
            receipt = json.loads(self.registrar.resolve(ref))
            check = json.loads(self.registrar.resolve(receipt["host_closure_check_ref"]))
            self.assertEqual((check["result"], check["closure_sha256"]), ("verified", pinned))
            self.assertEqual(check["process_id"], receipt["process_id"])
            normalized = normalized_codex_containment_argv(
                ["codex", "--version"] if receipt["launch_plan"]["effect_scope"]["process_kind"] == "version-probe"
                else self.policy["launcher"]["review_argv"], policy=self.policy)
            self.assertEqual(receipt["launch_plan"]["containment_argv_sha256"], sha256_hex(canonical_json(normalized)))
            self.assertEqual(normalized[0], "/usr/bin/bwrap")
        # The same logical command planned under the original policy would name a staged loader instead.
        original = normalized_codex_containment_argv(["codex", "--version"])
        self.assertNotEqual(original[0], "/usr/bin/bwrap")

    def test_a_drifted_closure_is_a_retained_refusal_that_is_never_retried(self):
        runtime = self.runtime()
        calls = []
        authorization = self.authorization(runtime)
        reviews = self.execute(self.runner("drift", calls), runtime=runtime, authorization=authorization)
        self.assertEqual(reviews["status"], "stopped")
        self.assertTrue(all(not invoked for _kind, _argv, invoked in calls))
        self.assertFalse([c for c in calls if c[0] == "native-review" and c[2]])
        receipt = json.loads(self.registrar.resolve(reviews["process_receipt_refs"][0]))
        self.assertEqual((receipt["outer_launch_state"], receipt["termination"]), ("not-invoked", "preflight-refused"))
        check = json.loads(self.registrar.resolve(receipt["host_closure_check_ref"]))
        self.assertEqual(check["refusal_code"], "host_closure_member_changed:libc.so.6")
        self.score(reviews)  # a refused check is valid evidence of an infrastructure stop
        self.setUp_credentials_rotated()
        replay = self.execute(self.exploding_runner(), runtime=runtime, authorization=authorization)
        self.assertEqual(replay, reviews)

    def exploding_runner(self):
        def explode(*_args, **_kwargs):
            raise AssertionError("a sealed slot must not launch again")

        return explode

    def setUp_credentials_rotated(self):
        rotated, _account, _subject = credential_fixture()
        self.write_source(rotated)
        self.write_anchors()

    def test_evidence_without_the_pre_launch_check_is_refused_when_scored(self):
        from caplab.revbench import RevbenchContractError

        reviews = self.execute(self.runner("omit-check"))
        with self.assertRaisesRegex(RevbenchContractError, "host_closure_check_ref.*required before an invoked process"):
            self.score(reviews)

    def test_a_check_of_another_closure_a_late_check_or_a_refusal_before_a_run_is_refused(self):
        from caplab.revbench import RevbenchContractError

        for mode, message in (
            ("wrong-closure", "does not check the pinned closure"),
            ("late-check", "was not made before launch"),
            ("refused-but-invoked", "contradicts its refusal"),
        ):
            with self.subTest(mode):
                self.setUp()
                reviews = self.execute(self.runner(mode))
                with self.assertRaisesRegex(RevbenchContractError, message):
                    self.score(reviews)

    def test_a_bundle_that_pins_no_closure_refuses_a_retained_check(self):
        from caplab.revbench import RevbenchContractError

        def drop_closure(policy):
            del policy["host_closure"]

        self.build(policy_edit=drop_closure)
        reviews = self.execute(self.runner())  # this runner records a check, as the direct launcher does
        with self.assertRaisesRegex(RevbenchContractError, "host_closure_check_ref.*is not valid for this bundle"):
            self.score(reviews)

    def test_the_credential_lease_is_taken_after_the_durable_intent_and_a_refusal_seals_the_slot(self):
        runtime = self.runtime()
        authorization = self.authorization(runtime, total_wall_seconds=7200)  # longer than the 3600 s token
        calls = []
        reviews = self.execute(self.runner(calls=calls), runtime=runtime, authorization=authorization)
        self.assertEqual((reviews["status"], reviews["stop_reason"]), ("stopped", "preflight-refused"))
        self.assertEqual((reviews["attempts"], reviews["process_receipt_refs"], calls), ([], [], []))
        self.assertEqual(self.score(reviews)["disposition"], "infrastructure-failure")
        authorization_document = json.loads(self.registrar.resolve(authorization))
        identity = {
            "schema_version": "caplab-revbench-live-execution-identity/1",
            "authorization_id": authorization_document["authorization_id"],
            "manifest_sha256": authorization_document["manifest_ref"]["sha256"],
            "experiment_id": self.manifest["experiment_id"],
            "binding_id": self.manifest["binding"]["binding_id"],
            "custody_domain_id": runtime.custody_domain_id,
        }
        self.assertIsNotNone(runtime.retained_execution_intent(identity))  # the intent was durable before the refusal
        # The same credential suffices for a 120 s deadline (the end-to-end test), so the refusal
        # above is the deadline-derived lifetime requirement, not the credential.  Rotating to a
        # long-lived credential afterwards cannot reopen the sealed slot.
        self.setUp_credentials_rotated()
        replay = self.execute(self.exploding_runner(), runtime=runtime, authorization=authorization)
        self.assertEqual(replay, reviews)
        for value in self.private_values():
            self.assertNotIn(value.encode(), self.surfaces(runtime, reviews))

    def test_missing_or_mismatched_private_inputs_refuse_after_the_intent_without_any_launch(self):
        cases = {
            "anchors unprovisioned": lambda: self.runtime(anchors={}),
            "anchors file missing": lambda: (self.credential_root / "anchors.json").unlink() or self.runtime(),
            "source changed after anchoring": lambda: (self.write_source({**self.document, "last_refresh": "2026-09-10T00:00:00Z"}), self.runtime())[1],
            "wrong subject anchor": lambda: (self.write_anchors(provider_subject_sha256=digest(b"x")), self.runtime())[1],
        }
        for name, make in cases.items():
            with self.subTest(name):
                self.setUp()
                runtime = make()
                calls = []
                reviews = self.execute(self.runner(calls=calls), runtime=runtime)
                self.assertEqual((reviews["status"], reviews["stop_reason"]), ("stopped", "preflight-refused"))
                self.assertEqual(calls, [])
                for value in self.private_values():
                    self.assertNotIn(value.encode(), self.surfaces(runtime, reviews))

    def test_privacy_quarantine_withholds_the_stream_through_the_adapters_fresh_guard(self):
        runtime = self.runtime()
        calls = []
        reviews = self.execute(self.runner("quarantine", calls), runtime=runtime)
        self.assertEqual((reviews["status"], reviews["stop_reason"]), ("stopped", "privacy-quarantine"))
        receipt = json.loads(self.registrar.resolve(reviews["process_receipt_refs"][1]))
        self.assertEqual(receipt["stream_disposition"], "privacy-quarantined")
        self.assertIsNone(receipt["stdout_ref"])
        self.assertEqual(self.score(reviews)["disposition"], "infrastructure-failure")
        for value in self.private_values():
            self.assertNotIn(value.encode(), self.surfaces(runtime, reviews))

    def test_prepare_refuses_every_mismatch_between_method_profile_policy_and_command(self):
        from caplab.revbench import RevbenchContractError

        v1_profile = {
            "schema_version": "caplab-revbench-codex-credential-profile/1",
            "profile_id": "caplab-openai-revbench", "provider": "openai", "auth_method": "chatgpt",
            "identity_basis": "operator-declared-unverified-token-claims",
            "provider_account_id_sha256": "a" * 64, "provider_subject_sha256": "b" * 64,
            "identity_token_issuer": "https://auth.openai.com",
            "identity_token_audience": ["https://api.openai.com/v1"],
        }

        def without_store_flag(policy):
            argv = policy["launcher"]["review_argv"]
            index = argv.index("cli_auth_credentials_store=file")
            del argv[index - 1 : index + 1]

        cases = {
            "original profile under the external policy": dict(profile=v1_profile),
            "external profile with a private anchor field": dict(profile={**external_profile(), "provider_account_id_sha256": "a" * 64}),
            "external profile with another store": dict(profile=external_profile(initial_credentials_store="ephemeral")),
            "external profile with another marker policy": dict(profile=external_profile(quarantine_profile="credential-private-text/v1")),
            "command without the file-store setting": dict(registered_policy_edit=without_store_flag),
            "registered policy with another delivery store": dict(registered_policy_edit=lambda p: p["credential_delivery"].update(initial_credentials_store="keyring")),
            "registered policy with another closure member": dict(registered_policy_edit=lambda p: p["host_closure"]["libraries"][0].update(sha256="0" * 64)),
            "registered policy under the original name": dict(registered_policy_edit=lambda p: p.update(policy_id="codex-terra-max-revbench-live-v1")),
        }
        for name, arguments in cases.items():
            with self.subTest(name), self.assertRaises(RevbenchContractError):
                self.build(**arguments)
        # And the reverse: the original policy cannot take the external profile.
        with self.subTest("external profile under the original policy"), self.assertRaises(RevbenchContractError):
            self.build(base_policy=codex_native_bundle_policy(), profile=external_profile())

    def test_scoring_under_another_policy_does_not_recompute_the_launch_plans(self):
        from caplab.revbench import RevbenchContractError

        reviews = self.execute(self.runner())
        other = copy.deepcopy(self.policy)
        other["containment"]["hostname"] = "caplab-other"
        other["version_containment_argv_template"][3] = "caplab-other"
        for name, policy in (("changed template", other), ("original policy", codex_native_bundle_policy())):
            with self.subTest(name), self.assertRaises(RevbenchContractError):
                self.score(reviews, policy=policy)


    def test_external_evidence_validates_against_the_published_schemas_and_hostile_edits_do_not(self):
        from jsonschema import Draft202012Validator, ValidationError
        from referencing import Registry, Resource

        contracts = Path(__file__).resolve().parents[1] / "docs" / "product" / "contracts"
        root_schema = json.loads((contracts / "revbench-v1.schema.json").read_bytes())
        live_schema = json.loads((contracts / "revbench-live-native-v1.schema.json").read_bytes())
        claim_schema = json.loads((contracts / "qualification-claim-v1.schema.json").read_bytes())
        registry = Registry().with_resources(
            ((claim_schema["$id"], Resource.from_contents(claim_schema)),
             (live_schema["$id"], Resource.from_contents(live_schema)))
        )
        live = Draft202012Validator(live_schema, registry=registry)
        reviews = self.execute(self.runner())
        seen = set()
        for raw in self.registrar.documents.values():
            try:
                document = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            version = document.get("schema_version") if isinstance(document, dict) else None
            if version == "caplab-revbench-codex-native-bundle-policy/1":
                continue  # synthetic member bytes; the shipped constants are validated below
            if version in (
                "caplab-revbench-codex-external-credential-profile/1",
                "caplab-revbench-execution-apparatus/1",
                "caplab-revbench-live-process-receipt/1",
                "caplab-revbench-live-execution-intent/1",
                "caplab-revbench-codex-runtime/1",
                "caplab-revbench-host-closure-check/1",
            ):
                with self.subTest(version=version):
                    live.validate(document)
                seen.add(version)
        self.assertEqual(
            seen,
            {
                "caplab-revbench-codex-external-credential-profile/1",
                "caplab-revbench-execution-apparatus/1",
                "caplab-revbench-live-process-receipt/1",
                "caplab-revbench-live-execution-intent/1",
                "caplab-revbench-codex-runtime/1",
                "caplab-revbench-host-closure-check/1",
            },
        )
        Draft202012Validator(root_schema, registry=registry).validate(reviews)
        live.validate(codex_native_external_bundle_policy())
        live.validate(codex_native_bundle_policy())  # the original policy still validates

        def mutated(edit):
            policy = codex_native_external_bundle_policy()
            edit(policy)
            return policy

        hostile = {
            "host mount added": lambda p: p["containment"].update(host_mount="/"),
            "adapter elsewhere": lambda p: p["containment"].update(adapter_path="/tmp/bwrap"),
            "store ephemeral": lambda p: p["credential_delivery"].update(initial_credentials_store="ephemeral"),
            "store flag removed": lambda p: p["launcher"]["review_argv"].remove("cli_auth_credentials_store=file"),
            "closure member changed": lambda p: p["host_closure"]["libraries"][0].update(sha256="0" * 64),
            "preload allowed": lambda p: p["host_closure"]["loader_inputs"]["preload"].update(state="present"),
        }
        for name, edit in hostile.items():
            with self.subTest(name), self.assertRaises(ValidationError):
                live.validate(mutated(edit))
        receipt = next(
            json.loads(raw) for raw in self.registrar.documents.values()
            if raw.startswith(b'{"authorization_id"') and b"host_closure_check_ref" in raw
        )
        for name, edit in {
            "check ref of another kind": lambda d: d["host_closure_check_ref"].update(kind="prompt"),
            "unknown receipt field": lambda d: d.update(note="x"),
        }.items():
            document = copy.deepcopy(receipt)
            edit(document)
            with self.subTest(name), self.assertRaises(ValidationError):
                live.validate(document)
        profile = external_profile(provider_account_id_sha256="a" * 64)
        with self.subTest("private anchor in public profile"), self.assertRaises(ValidationError):
            live.validate(profile)



    def score_with_check_edit(self, edit, *, mode="valid"):
        """Run a flow whose retained check records are freshly registered with ``edit`` applied.

        The edit happens before the registrar hashes the document, so every returned reference and
        derived receipt identity is valid for the malformed content: the scorer has to look at the
        values themselves, not just at integrity.
        """

        from caplab.revbench import RevbenchContractError

        original = self.registrar.register_document

        def register(document, **kwargs):
            if edit is not None and kwargs.get("kind") == "native-host-closure-check":
                edit(document)
            return original(document, **kwargs)

        self.registrar.register_document = register
        try:
            reviews = self.execute(self.runner(mode))
        finally:
            self.registrar.register_document = original
        try:
            return self.score(reviews), None
        except RevbenchContractError as error:
            return None, str(error)

    def test_public_scoring_refuses_a_freshly_registered_check_whose_values_break_the_closed_contract(self):
        malformed = {
            "boolean member count": lambda d: d.update(member_count=True),
            "negative member count": lambda d: d.update(member_count=-1),
            "member count above 64": lambda d: d.update(member_count=65),
            "string member count": lambda d: d.update(member_count="6"),
            "object member count": lambda d: d.update(member_count={"fabricated": "count"}),
        }
        measurement, error = self.score_with_check_edit(None)
        self.assertEqual((error, measurement["disposition"]), (None, "complete"))  # the valid positive control
        for name, edit in malformed.items():
            with self.subTest(name):
                self.setUp()
                measurement, error = self.score_with_check_edit(edit)
                self.assertIsNone(measurement)
                self.assertRegex(error, r"host_closure_check_ref.*violates its closed contract")
        for name, edit in {
            "free-text refusal": lambda d: d.update(refusal_code="private-looking/path or arbitrary text"),
            "refusal naming a path": lambda d: d.update(refusal_code="host_closure_member_changed:/etc/passwd"),
        }.items():
            with self.subTest(name):
                self.setUp()
                measurement, error = self.score_with_check_edit(edit, mode="drift")
                self.assertIsNone(measurement)
                self.assertRegex(error, r"host_closure_check_ref.*violates its closed contract")
        self.setUp()
        measurement, error = self.score_with_check_edit(None, mode="drift")  # a valid refusal still scores
        self.assertEqual((error, measurement["disposition"]), (None, "infrastructure-failure"))


class OfflineHostClosureEvidenceTests(unittest.TestCase):
    """One value contract for the retained check: custody writes it, the schema states it, the scorer reads it."""

    PROCESS = "process-" + "a" * 64

    def document(self, *, refused=True, **changes):
        document = {
            "schema_version": "caplab-revbench-host-closure-check/1",
            "process_id": self.PROCESS,
            "closure_sha256": host_closure.closure_sha256(codex_native_external_bundle_policy()["host_closure"]),
            "member_count": 0 if refused else 6,
            "checked_at": "2026-10-05T00:00:00Z",
            "result": "refused" if refused else "verified",
            "refusal_code": "host_closure_member_missing:executable" if refused else None,
        }
        document.update(changes)
        return document

    def receipt(self, *, refused=True):
        return {
            "outer_launch_state": "not-invoked" if refused else "invoked",
            "termination": "preflight-refused" if refused else "exited",
            "process_id": self.PROCESS,
            "intent_recorded_at": "2026-10-05T00:00:00Z",
            "launch_attempted_at": None if refused else "2026-10-05T00:00:02Z",
            "completion_recorded_at": "2026-10-05T00:00:03Z",
        }

    def verdicts(self, document, *, refused=True):
        """(schema rejects, custody rejects, scorer rejects) for one registered record."""

        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
        from caplab.revbench import RevbenchContractError, _core
        from caplab.revbench.custody import validate_host_closure_check
        from tests.test_revbench import MemoryRegistrar, registered

        contracts = Path(__file__).resolve().parents[1] / "docs" / "product" / "contracts"
        live = json.loads((contracts / "revbench-live-native-v1.schema.json").read_bytes())
        claim = json.loads((contracts / "qualification-claim-v1.schema.json").read_bytes())
        registry = Registry().with_resources(
            [(live["$id"], Resource.from_contents(live)), (claim["$id"], Resource.from_contents(claim))])
        schema_rejects = not Draft202012Validator(live, registry=registry).is_valid(document)
        try:
            validate_host_closure_check(document, self.PROCESS)
            custody_rejects = False
        except LiveExecutionCustodyError:
            custody_rejects = True
        registrar = MemoryRegistrar()
        ref = registered(registrar, "check", document, kind="native-host-closure-check", schema=document["schema_version"])
        try:
            _core._validate_host_closure_check_evidence(
                ref, self.receipt(refused=refused), host_closure=codex_native_external_bundle_policy()["host_closure"],
                registrar=registrar, path="probe")
            scorer_rejects = False
        except RevbenchContractError:
            scorer_rejects = True
        return schema_rejects, custody_rejects, scorer_rejects

    def test_valid_records_are_accepted_by_all_three_including_the_count_boundaries(self):
        for name, document, refused in (
            ("refusal", self.document(), True),
            ("verified", self.document(refused=False), False),
            ("count zero", self.document(refused=False, member_count=0), False),
            ("count 64", self.document(refused=False, member_count=64), False),
            ("category and member at their limits", self.document(
                refusal_code="host_closure_" + "a" * 36 + ":" + "b" * 64), True),
        ):
            with self.subTest(name):
                self.assertEqual(self.verdicts(document, refused=refused), (False, False, False))

    def test_values_outside_the_contract_are_refused_by_the_schema_custody_and_the_scorer_alike(self):
        cases = {
            "boolean count": dict(member_count=True),
            "false count": dict(member_count=False),
            "negative count": dict(member_count=-1),
            "count above 64": dict(member_count=65),
            "string count": dict(member_count="6"),
            "null count": dict(member_count=None),
            "object count": dict(member_count={"fabricated": "count"}),
            "list count": dict(member_count=[6]),
            "free text refusal": dict(refusal_code="private-looking/path or arbitrary text"),
            "path in refusal": dict(refusal_code="host_closure_member_changed:/etc/passwd"),
            "uppercase refusal": dict(refusal_code="HOST_CLOSURE_MEMBER_CHANGED:libc"),
            "empty member id": dict(refusal_code="host_closure_member_changed:"),
            "member id too long": dict(refusal_code="host_closure_member_changed:" + "a" * 65),
            "category too long": dict(refusal_code="host_closure_" + "a" * 49),
            "other prefix": dict(refusal_code="drift:libc"),
            "short digest": dict(closure_sha256="abc"),
            "uppercase digest": dict(closure_sha256="A" * 64),
            "malformed time": dict(checked_at="now"),
            "other schema": dict(schema_version="caplab-revbench-host-closure-check/2"),
        }
        for name, changes in cases.items():
            with self.subTest(name):
                self.assertEqual(self.verdicts(self.document(**changes)), (True, True, True))

    def test_custody_and_the_scorer_also_refuse_what_json_schema_semantics_would_let_through(self):
        # Python's JSON Schema `$` and `integer` are looser than the closed contract; the code must not be.
        cases = {
            "newline after the refusal code": (dict(refusal_code="host_closure_member_changed:libc\n"), True),
            "verified with a refusal code": (dict(result="verified", member_count=6, refusal_code="host_closure_x"), True),
            "refused without a code": (dict(refusal_code=None), True),
        }
        for name, (changes, refused) in cases.items():
            with self.subTest(name):
                _schema, custody, scorer = self.verdicts(self.document(**changes), refused=refused)
                self.assertEqual((custody, scorer), (True, True))


class ExternalAdapterApparatusTests(unittest.TestCase):
    def test_importing_the_external_adapter_cannot_change_the_apparatus_identity(self):
        """The adapter is imported lazily, after the apparatus is identified; it must add nothing to it."""

        import subprocess
        import sys

        root = Path(__file__).resolve().parents[1]
        scripts = (
            "from caplab.revbench.codex import execution_apparatus_receipt as r;"
            "print(r(require_clean=False)['apparatus_id'])",
            "from caplab.revbench.codex import execution_apparatus_receipt as r;"
            "before = r(require_clean=False)['apparatus_id'];"
            "import caplab.revbench.external_credential, caplab.revbench.host_closure, caplab.codex_external_credential;"
            "print(before);"
            "print(r(require_clean=False)['apparatus_id'])",
            "import caplab.revbench.external_credential, caplab.codex_external_credential;"
            "from caplab.revbench.codex import execution_apparatus_receipt as r;"
            "print(r(require_clean=False)['apparatus_id'])",
        )
        observed = []
        for script in scripts:
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=root,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(root / "src"), "PYTHONDONTWRITEBYTECODE": "1"},
                check=True,
                capture_output=True,
                text=True,
            )
            observed.append(result.stdout.split())
        identity = observed[0][0]
        self.assertEqual(observed[1], [identity, identity])
        self.assertEqual(observed[2], [identity])

    def test_the_receipt_validator_accepts_the_original_and_the_extended_protocol_only(self):
        receipt = codex.execution_apparatus_receipt(require_clean=False)

        def resealed(edit):
            document = copy.deepcopy(receipt)
            edit(document["protocol"])
            identity = copy.deepcopy(document)
            identity.pop("apparatus_id")
            document["apparatus_id"] = "apparatus-" + sha256_hex(canonical_json(identity))
            return document

        original = resealed(
            lambda protocol: [protocol.pop(key) for key in ("external_token_bundle_policy_source_sha256", "host_closure_trust")]
        )
        for document in (receipt, original):
            self.assertEqual(codex.validate_execution_apparatus_receipt(document, allow_dirty=True), document)
        for name, edit in {
            "only one extra field": lambda protocol: protocol.pop("host_closure_trust"),
            "another trust statement": lambda protocol: protocol.update(host_closure_trust="root-never-updates-anything"),
            "another external policy pin": lambda protocol: protocol.update(external_token_bundle_policy_source_sha256="0" * 64),
            "another original pin": lambda protocol: protocol.update(bundle_policy_source_sha256="0" * 64),
            "unknown field": lambda protocol: protocol.update(extra="x"),
        }.items():
            with self.subTest(name), self.assertRaisesRegex(CodexAdapterError, "execution_apparatus_protocol_invalid"):
                codex.validate_execution_apparatus_receipt(resealed(edit), allow_dirty=True)



class ExternalCliTests(unittest.TestCase):
    def setUp(self):
        from caplab.revbench import __main__ as cli

        self.cli = cli
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.custody = self.root / "custody"
        self.custody.mkdir(mode=0o700)
        self.credentials = self.root / "credentials-private-root-7f31"
        self.credentials.mkdir(mode=0o700)
        self.live_manifest = self.root / "live-manifest.json"
        self.live_manifest.write_bytes(canonical_json({"binding": {"provider_or_path": {"kind": "direct-provider"}}}))
        self.local_manifest = self.root / "local-manifest.json"
        self.local_manifest.write_bytes(canonical_json({"binding": {"provider_or_path": {"kind": "local-serving"}}}))

    def arguments(self, manifest, *extra, live=True):
        base = [
            "execute", "--manifest", str(manifest),
            "--execution-authorization-ref", str(self.root / "authorization.json"),
            "--ledger", str(self.root / "ledger"), "--output", str(self.root / "output.json"),
        ]
        if live:
            base += ["--live-custody-root", str(self.custody), "--credential-root", str(self.credentials)]
        return base + list(extra)

    def run_error(self, argv, *, live_source=True):
        emitted = []
        with (
            mock.patch("caplab.revbench.__main__._emit", side_effect=lambda document, **_: emitted.append(document)),
            mock.patch("caplab.revbench.__main__.require_live_source_invocation"),
        ):
            result = self.cli.main(argv, live_source=live_source)
        self.assertEqual(result, 2)
        self.assertEqual(len(emitted), 1)
        return emitted[0]

    def test_the_anchor_option_exists_only_in_the_live_source_parser_and_repeats(self):
        live = self.cli.build_parser(live_source=True)
        parsed = live.parse_args(self.arguments(
            self.live_manifest, "--credential-profile-source", "a=a.json", "--credential-anchor", "a=anchors.json"))
        self.assertEqual(parsed.credential_anchor, ["a=anchors.json"])
        self.assertIsNone(live.parse_args(self.arguments(self.live_manifest)).credential_anchor)
        error = self.run_error(
            ["execute", "--credential-anchor", "caplab-private-profile-7f31=private-anchors-7f31.json"],
            live_source=False,
        )
        self.assertEqual(error["code"], "argument_error")
        self.assertNotIn("7f31", json.dumps(error))

    def test_anchor_arguments_are_closed_and_their_errors_are_path_free(self):
        source = "--credential-profile-source"
        cases = {
            "no separator": ([source, "p=s.json", "--credential-anchor", "p-anchors.json"], "credential_anchor_invalid"),
            "empty filename": ([source, "p=s.json", "--credential-anchor", "p="], "credential_anchor_invalid"),
            "duplicate profile": ([source, "p=s.json", "--credential-anchor", "p=a.json", "--credential-anchor", "p=b.json"], "credential_anchor_invalid"),
            "profile without a source mapping": ([source, "p=s.json", "--credential-anchor", "q=private-anchors-7f31.json"], "credential_anchor_profile_unmapped"),
        }
        for name, (extra, code) in cases.items():
            with self.subTest(name):
                error = self.run_error(self.arguments(self.live_manifest, *extra))
                self.assertEqual(error["code"], code)
                self.assertNotIn("7f31", json.dumps(error))
                self.assertNotIn(str(self.root), json.dumps(error))

    def test_the_anchor_option_is_refused_for_a_local_fixture_run(self):
        error = self.run_error(self.arguments(self.local_manifest, "--credential-anchor", "p=a.json", live=False))
        self.assertEqual(error["code"], "local_fixture_rejects_live_runtime_options")

    def test_anchor_mappings_reach_the_private_runtime_without_values_on_the_command_line(self):
        captured = {}

        def runtime(*args, **kwargs):
            captured.update(kwargs)
            raise self.cli.RevbenchContractError("stop_after_runtime")

        argv = self.arguments(
            self.live_manifest, "--credential-profile-source", "p=source.json", "--credential-anchor", "p=anchors.json")
        with mock.patch("caplab.revbench.__main__.FilesystemLiveExecutionRuntime", side_effect=runtime):
            error = self.run_error(argv)
        self.assertEqual(error["code"], "stop_after_runtime")
        self.assertEqual(captured["credential_sources"], {"p": "source.json"})
        self.assertEqual(captured["credential_anchor_sources"], {"p": "anchors.json"})
        # Only file names travel through the command line: the hashes live in the private file.
        self.assertFalse([token for token in argv if len(token) >= 64 and set(token) <= set("0123456789abcdef")])

    def test_runs_without_anchors_pass_none_so_the_original_profile_is_unchanged(self):
        captured = {}

        def runtime(*args, **kwargs):
            captured.update(kwargs)
            raise self.cli.RevbenchContractError("stop_after_runtime")

        argv = self.arguments(self.live_manifest, "--credential-profile-source", "p=source.json")
        with mock.patch("caplab.revbench.__main__.FilesystemLiveExecutionRuntime", side_effect=runtime):
            self.run_error(argv)
        self.assertIsNone(captured["credential_anchor_sources"])
        self.assertEqual(captured["credential_sources"], {"p": "source.json"})

    def test_the_isolated_source_command_shape_and_prepare_arguments_are_unchanged(self):
        program = self.cli._live_program()
        self.assertTrue(program.startswith("/usr/bin/python3 -I -S -B -X pycache_prefix="))
        self.assertTrue(program.endswith("live_entrypoint.py"))
        parser = self.cli.build_parser(live_source=True)
        prepare_live = parser.parse_args(
            ["prepare-live-runtime", "--ledger", "l", "--live-custody-root", "c", "--output", "o"])
        self.assertEqual(vars(prepare_live).keys() - {"command"}, {"ledger", "live_custody_root", "output", "reference_output"})


if __name__ == "__main__":
    unittest.main()
