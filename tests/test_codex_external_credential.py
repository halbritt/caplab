"""A separate native credential projection preserves identity and descriptor custody."""

import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from copy import deepcopy


def digest(value):
    return hashlib.sha256(value).hexdigest()


def fixture():
    now = int(time.time())
    account, subject = "fabricated-account-00000001", "fabricated-subject-00000001"

    def token(expiry):
        def encode(value):
            return (
                base64.urlsafe_b64encode(json.dumps(value).encode())
                .rstrip(b"=")
                .decode()
            )

        return ".".join(
            (
                encode({"alg": "RS256", "kid": "fabricated-key-000001"}),
                encode(
                    {
                        "iss": "https://auth.openai.com",
                        "sub": subject,
                        "aud": ["https://api.openai.com/v1"],
                        "iat": now - 3600,
                        "exp": expiry,
                        "email": "fabricated-person@example.invalid",
                        "https://api.openai.com/auth": {
                            "chatgpt_account_id": account,
                            "organizations": [
                                {
                                    "id": "fabricated-org-00001",
                                    "is_default": True,
                                    "counter": 1,
                                }
                            ],
                        },
                    }
                ),
                encode("fabricated-signature-only"),
            )
        )

    document = {
        "auth_mode": "chatgpt",
        "OPENAI_API_KEY": None,
        "tokens": {
            "id_token": token(now - 60),
            "access_token": token(now + 3600),
            "refresh_token": "fabricated-refresh-token-000001",
            "account_id": account,
        },
        "last_refresh": "2026-09-09T00:00:00.123456789Z",
    }
    return document, account, subject


def with_claims(document, update):
    result = deepcopy(document)
    for key in ("id_token", "access_token"):
        parts = result["tokens"][key].split(".")
        claims = json.loads(
            base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
        )
        update(claims)
        parts[1] = (
            base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
        )
        result["tokens"][key] = ".".join(parts)
    return result


class CodexExternalCredentialTests(unittest.TestCase):
    def test_protocol_categories_do_not_exempt_custom_identity_or_malformed_locations(
        self,
    ):
        from caplab.codex_external_credential import open_codex_external_credential

        original, account, subject = fixture()
        auth = "https://api.openai.com/auth"

        def organization(claims, **fields):
            claims[auth]["organizations"][0].update(fields)

        cases = [
            (
                "nondefault-title",
                lambda c: organization(c, title="Personal", is_default=False),
                "Personal",
            ),
            (
                "numeric-default",
                lambda c: organization(c, title="Personal", is_default=1),
                "Personal",
            ),
            (
                "custom-title",
                lambda c: organization(
                    c, title="Private organization 001", is_default=True
                ),
                "Private organization 001",
            ),
            (
                "private-name-overlap",
                lambda c: (
                    organization(c, title="Personal", is_default=True),
                    c.update(name="Personal"),
                ),
                "Personal",
            ),
            (
                "private-role-overlap",
                lambda c: (organization(c, role="owner"), c.update(name="owner")),
                "owner",
            ),
            (
                "unknown-role",
                lambda c: organization(c, role="private-role-001"),
                "private-role-001",
            ),
            (
                "unknown-scope",
                lambda c: c.update(scp=["profile", "private-scope-001"]),
                "private-scope-001",
            ),
            (
                "unknown-scope-string",
                lambda c: c.update(scope="openid private-scope-001"),
                "openid private-scope-001",
            ),
            (
                "scope-wrong-type",
                lambda c: c.update(scp=["profile", {"name": "private"}]),
                "profile",
            ),
            (
                "scope-wrong-location",
                lambda c: c.update(private={"scp": ["profile"]}),
                "profile",
            ),
            (
                "private-scope-overlap",
                lambda c: c.update(scope="openid profile", name="profile"),
                "profile",
            ),
            ("field-wrong-type", lambda c: c.update(rat="rat"), "rat"),
            ("field-wrong-location", lambda c: c.update(private={"rat": True}), "rat"),
            (
                "organization-wrong-container",
                lambda c: c[auth].update(
                    organizations={"*": {"title": "Personal", "is_default": True}}
                ),
                "Personal",
            ),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            for name, change, text in cases:
                document = with_claims(original, change)
                raw = json.dumps(document).encode()
                source.write_bytes(raw)
                source.chmod(0o600)
                with (
                    self.subTest(name=name),
                    open_codex_external_credential(
                        source,
                        expected_source_sha256=digest(raw),
                        expected_account_sha256=digest(account.encode()),
                        expected_subject_sha256=digest(subject.encode()),
                        minimum_access_lifetime_seconds=300,
                        quarantine_profile="credential-private-text/v2",
                    ) as lease,
                ):
                    guard = lease.quarantine_factory()
                    value = text.encode()
                    retained = (
                        guard.feed(value[:2]) + guard.feed(value[2:]) + guard.finish()
                    )
                    self.assertTrue(guard.quarantined)
                    self.assertNotIn(value, retained)
                self.assertEqual(source.read_bytes(), raw)

    def test_protocol_field_names_and_categories_do_not_quarantine_normal_native_metadata(
        self,
    ):
        from caplab.codex_external_credential import open_codex_external_credential

        original, account, subject = fixture()

        def update(claims):
            claims.update(
                rat=1,
                sl=True,
                sid="fabricated-session-000001",
                session_id="fabricated-session-000002",
                scp=["openid", "profile", "email", "offline_access"],
            )
            claims["https://api.openai.com/auth"]["organizations"][0].update(
                title="Personal", role="owner", is_default=True
            )

        document = with_claims(original, update)
        raw = json.dumps(document).encode()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            source.write_bytes(raw)
            source.chmod(0o600)
            with open_codex_external_credential(
                source,
                expected_source_sha256=digest(raw),
                expected_account_sha256=digest(account.encode()),
                expected_subject_sha256=digest(subject.encode()),
                minimum_access_lifetime_seconds=300,
                quarantine_profile="credential-private-text/v2",
            ) as lease:
                message = b'{"profile":"exact-ipv4-tcp/v1","operation":"inspect","role":"user","title":"Personal notes","session_id":"fabricated-display-reference"}\n'
                guard = lease.quarantine_factory()
                retained = guard.feed(message) + guard.finish()
                self.assertFalse(guard.quarantined)
                self.assertEqual(retained, message)
                for value in (
                    b"fabricated-session-000001",
                    b"fabricated-session-000002",
                ):
                    guard = lease.quarantine_factory()
                    retained = (
                        guard.feed(value[:5]) + guard.feed(value[5:]) + guard.finish()
                    )
                    self.assertTrue(guard.quarantined)
                    self.assertNotIn(value, retained)

    def test_selected_category_profile_allows_normal_output_and_preserves_projection(
        self,
    ):
        from caplab.codex_external_credential import open_codex_external_credential

        document, account, subject = fixture()
        for key in ("id_token", "access_token"):
            parts = document["tokens"][key].split(".")
            claims = json.loads(
                base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
            )
            claims["https://api.openai.com/auth"]["chatgpt_plan_type"] = "pro"
            parts[1] = (
                base64.urlsafe_b64encode(json.dumps(claims).encode())
                .rstrip(b"=")
                .decode()
            )
            document["tokens"][key] = ".".join(parts)
        raw = json.dumps(document).encode()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            source.write_bytes(raw)
            source.chmod(0o600)
            arguments = dict(
                expected_source_sha256=digest(raw),
                expected_account_sha256=digest(account.encode()),
                expected_subject_sha256=digest(subject.encode()),
                minimum_access_lifetime_seconds=300,
            )
            with open_codex_external_credential(source, **arguments) as old:
                before = os.pread(old.descriptor, 65536, 0)
                guard = old.quarantine_factory()
                guard.feed(b'{"schema":"caplab.process-capture/v1"}\n')
                guard.finish()
                self.assertTrue(guard.quarantined)
            with open_codex_external_credential(
                source, **arguments, quarantine_profile="credential-private-text/v2"
            ) as selected:
                self.assertEqual(
                    selected.quarantine_profile, "credential-private-text/v2"
                )
                self.assertEqual(os.pread(selected.descriptor, 65536, 0), before)
                guard = selected.quarantine_factory()
                message = b'{"schema":"caplab.process-capture/v1"}\n'
                retained = (
                    guard.feed(message[:20]) + guard.feed(message[20:]) + guard.finish()
                )
                self.assertFalse(guard.quarantined)
                self.assertEqual(retained, message)
            self.assertEqual(source.read_bytes(), raw)

    def test_category_exemption_preserves_private_occurrences_and_token_material(self):
        from caplab.codex_external_credential import (
            open_codex_external_credential,
            ExternalCredentialError,
        )

        original, account, subject = fixture()
        auth = "https://api.openai.com/auth"
        cases = []
        for category in (
            "free",
            "go",
            "plus",
            "pro",
            "team",
            "business",
            "enterprise",
            "edu",
            "unknown",
        ):
            document = with_claims(
                original, lambda c: c[auth].update(chatgpt_plan_type=category)
            )
            cases.append((category, document, category, False))
        base = with_claims(original, lambda c: c[auth].update(chatgpt_plan_type="pro"))
        for name, update, secret in (
            ("private-name", lambda c: c.update(name="pro"), "pro"),
            ("private-key", lambda c: c.update(pro=True), "pro"),
            ("wrong-location", lambda c: c.update(chatgpt_plan_type="pro"), "pro"),
            (
                "unknown-value",
                lambda c: c[auth].update(chatgpt_plan_type="private-category-00001"),
                "private-category-00001",
            ),
            (
                "nested-value",
                lambda c: c[auth].update(chatgpt_plan_type={"name": "pro"}),
                "pro",
            ),
            (
                "non-ascii",
                lambda c: c.update(name="Zoë Δ private-person"),
                "Zoë Δ private-person",
            ),
        ):
            cases.append((name, with_claims(base, update), secret, True))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            for name, document, text, expected in cases:
                raw = json.dumps(document).encode()
                source.write_bytes(raw)
                source.chmod(0o600)
                arguments = dict(
                    expected_source_sha256=digest(raw),
                    expected_account_sha256=digest(account.encode()),
                    expected_subject_sha256=digest(subject.encode()),
                    minimum_access_lifetime_seconds=300,
                    quarantine_profile="credential-private-text/v2",
                )
                with (
                    self.subTest(name=name),
                    open_codex_external_credential(source, **arguments) as lease,
                ):
                    guard = lease.quarantine_factory()
                    value = text.encode()
                    retained = (
                        b"".join(
                            guard.feed(value[n : n + 1]) for n in range(len(value))
                        )
                        + guard.finish()
                    )
                    self.assertEqual(guard.quarantined, expected)
                    if not expected:
                        self.assertEqual(retained, value)
                    for secret in (
                        raw,
                        *[v.encode() for v in document["tokens"].values()],
                        *[
                            p.encode()
                            for p in document["tokens"]["id_token"].split(".")
                        ],
                    ):
                        guard = lease.quarantine_factory()
                        cut = len(secret) // 2
                        retained = (
                            guard.feed(secret[:cut])
                            + guard.feed(secret[cut:])
                            + guard.finish()
                        )
                        self.assertTrue(guard.quarantined)
                        self.assertNotIn(secret, retained)
                self.assertEqual(source.read_bytes(), raw)
            with self.assertRaisesRegex(
                ExternalCredentialError, "credential_quarantine_profile_invalid"
            ):
                with open_codex_external_credential(
                    source / "absent",
                    **(arguments | {"quarantine_profile": "unselected"}),
                ):
                    self.fail("unsupported profile reached delivery")

    def test_expired_id_metadata_and_fractional_refresh_project_to_sealed_external_tokens(
        self,
    ):
        from caplab.codex_external_credential import open_codex_external_credential

        document, account, subject = fixture()
        raw = json.dumps(document).encode()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            source.write_bytes(raw)
            source.chmod(0o600)
            before = set(os.listdir("/proc/self/fd"))
            with open_codex_external_credential(
                source,
                expected_source_sha256=digest(raw),
                expected_account_sha256=digest(account.encode()),
                expected_subject_sha256=digest(subject.encode()),
                minimum_access_lifetime_seconds=300,
            ) as lease:
                projected = json.loads(os.pread(lease.descriptor, 65536, 0))
                self.assertEqual(
                    projected,
                    document
                    | {
                        "auth_mode": "chatgptAuthTokens",
                        "tokens": document["tokens"] | {"refresh_token": ""},
                    },
                )
                with self.assertRaises(PermissionError):
                    os.write(lease.descriptor, b"altered")
                seals = fcntl.fcntl(lease.descriptor, fcntl.F_GET_SEALS)
                self.assertEqual(
                    seals
                    & (
                        fcntl.F_SEAL_WRITE
                        | fcntl.F_SEAL_GROW
                        | fcntl.F_SEAL_SHRINK
                        | fcntl.F_SEAL_SEAL
                    ),
                    fcntl.F_SEAL_WRITE
                    | fcntl.F_SEAL_GROW
                    | fcntl.F_SEAL_SHRINK
                    | fcntl.F_SEAL_SEAL,
                )
                self.assertNotIn(account, repr(lease))
                for secret in (
                    account,
                    subject,
                    document["tokens"]["refresh_token"],
                    "fabricated-person@example.invalid",
                    "fabricated-org-00001",
                ):
                    guard = lease.quarantine_factory()
                    value = secret.encode()
                    middle = len(value) // 2
                    retained = (
                        guard.feed(value[:middle])
                        + guard.feed(value[middle:])
                        + guard.finish()
                    )
                    self.assertTrue(guard.quarantined)
                    self.assertNotIn(value, retained)
                descriptor = lease.descriptor
            with self.assertRaises(OSError):
                os.fstat(descriptor)
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(set(os.listdir("/proc/self/fd")), before)

    def test_rehashed_claims_cannot_bypass_identity_expiry_or_finite_json_checks(self):
        from caplab.codex_external_credential import (
            ExternalCredentialError,
            open_codex_external_credential,
        )

        document, account, subject = fixture()

        def changed_token(token, **changes):
            parts = token.split(".")
            claims = json.loads(
                base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
            )
            claims.update(changes)
            parts[1] = (
                base64.urlsafe_b64encode(json.dumps(claims).encode())
                .rstrip(b"=")
                .decode()
            )
            return ".".join(parts)

        candidates = []
        for changes in (
            {"sub": "fabricated-different-subject"},
            {"exp": int(time.time()) + 10},
            {
                "https://api.openai.com/auth": {
                    "chatgpt_account_id": "fabricated-other-account"
                }
            },
            {"private_measurement": float("inf")},
            {"exp": True},
        ):
            candidate = deepcopy(document)
            candidate["tokens"]["access_token"] = changed_token(
                candidate["tokens"]["access_token"], **changes
            )
            candidates.append(json.dumps(candidate).encode())
        # JSON's exponent notation can overflow a float without using Infinity.
        parts = document["tokens"]["access_token"].split(".")
        claims = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
        claims = claims[:-1] + b', "private_measurement": 1e999}'
        parts[1] = base64.urlsafe_b64encode(claims).rstrip(b"=").decode()
        candidates.append(
            json.dumps(
                document
                | {"tokens": document["tokens"] | {"access_token": ".".join(parts)}}
            ).encode()
        )
        raw = json.dumps(document).encode()
        candidates += [
            raw.replace(b'"auth_mode":', b'"auth_mode": "chatgpt", "auth_mode":'),
            json.dumps(document | {"last_refresh": "2026-02-30T00:00:00Z"}).encode(),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "auth.json"
            before = set(os.listdir("/proc/self/fd"))
            for index, raw in enumerate(candidates):
                source.write_bytes(raw)
                source.chmod(0o600)
                with self.subTest(index=index):
                    with self.assertRaises(ExternalCredentialError) as error:
                        with open_codex_external_credential(
                            source,
                            expected_source_sha256=digest(raw),
                            expected_account_sha256=digest(account.encode()),
                            expected_subject_sha256=digest(subject.encode()),
                            minimum_access_lifetime_seconds=300,
                        ):
                            self.fail("invalid credential reached delivery")
                    self.assertNotIn("fabricated", str(error.exception))
                self.assertEqual(set(os.listdir("/proc/self/fd")), before)

    def test_source_hash_owner_mode_links_and_descriptor_cleanup_guard_delivery(self):
        from caplab.codex_external_credential import (
            ExternalCredentialError,
            open_codex_external_credential,
        )

        document, account, subject = fixture()
        raw = json.dumps(document).encode()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "auth.json"
            source.write_bytes(raw)
            source.chmod(0o600)
            arguments = dict(
                expected_source_sha256=digest(raw),
                expected_account_sha256=digest(account.encode()),
                expected_subject_sha256=digest(subject.encode()),
                minimum_access_lifetime_seconds=300,
            )
            for field in (
                "expected_source_sha256",
                "expected_account_sha256",
                "expected_subject_sha256",
            ):
                with (
                    self.subTest(field=field),
                    self.assertRaises(ExternalCredentialError),
                ):
                    with open_codex_external_credential(
                        source, **(arguments | {field: "0" * 64})
                    ):
                        self.fail("mismatched source reached delivery")
            before = set(os.listdir("/proc/self/fd"))
            source.chmod(0o644)
            with self.assertRaises(ExternalCredentialError):
                with open_codex_external_credential(source, **arguments):
                    self.fail("public source reached delivery")
            source.chmod(0o600)
            link = root / "linked.json"
            os.link(source, link)
            with self.assertRaises(ExternalCredentialError):
                with open_codex_external_credential(source, **arguments):
                    self.fail("multiply linked source reached delivery")
            link.unlink()
            link.symlink_to(source)
            with self.assertRaises(ExternalCredentialError):
                with open_codex_external_credential(link, **arguments):
                    self.fail("symlink source reached delivery")
            self.assertEqual(set(os.listdir("/proc/self/fd")), before)
            with self.assertRaisesRegex(RuntimeError, "consumer failed"):
                with open_codex_external_credential(source, **arguments) as lease:
                    descriptor = lease.descriptor
                    raise RuntimeError("consumer failed")
            with self.assertRaises(OSError):
                os.fstat(descriptor)
            self.assertEqual(set(os.listdir("/proc/self/fd")), before)

    def test_explicit_child_handoff_reads_only_projection_and_quarantines_claim_echo(
        self,
    ):
        from caplab.codex_external_credential import open_codex_external_credential
        from caplab.process_capture import (
            capture_process,
            ProcessCaptureQuarantineError,
        )

        for profile in ("credential-private-text/v1", "credential-private-text/v2"):
            with self.subTest(profile=profile):
                document, account, subject = fixture()
                if profile == "credential-private-text/v2":
                    document = with_claims(
                        document,
                        lambda c: c["https://api.openai.com/auth"].update(
                            chatgpt_plan_type="pro"
                        ),
                    )
                raw = json.dumps(document).encode()
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    source = root / "auth.json"
                    source.write_bytes(raw)
                    source.chmod(0o600)
                    with open_codex_external_credential(
                        source,
                        expected_source_sha256=digest(raw),
                        expected_account_sha256=digest(account.encode()),
                        expected_subject_sha256=digest(subject.encode()),
                        minimum_access_lifetime_seconds=300,
                        quarantine_profile=profile,
                    ) as lease:
                        read = "import json,os,sys;d=json.loads(os.pread(int(sys.argv[1]),65536,0));assert d['auth_mode']=='chatgptAuthTokens' and d['tokens']['refresh_token']=='';"
                        process = capture_process(
                            [
                                "/usr/bin/python3",
                                "-I",
                                "-S",
                                "-c",
                                read + "print('external input read')",
                                str(lease.descriptor),
                            ],
                            cwd=root,
                            environment={},
                            output_dir=root / "safe",
                            max_stream_bytes=16384,
                            timeout_seconds=3,
                            pass_fds=(lease.descriptor,),
                            quarantine_factory=lease.quarantine_factory,
                        )
                        self.assertEqual(process["return_code"], 0)
                        self.assertEqual(
                            (root / "safe/native.stdout").read_bytes(),
                            b"external input read\n",
                        )
                        echo = "import base64,time;p=d['tokens']['id_token'].split('.')[1];v=json.loads(base64.urlsafe_b64decode(p+'='*(-len(p)%4)))['email'].encode();os.write(1,b'prefix '+v[:10]);time.sleep(.01);os.write(1,v[10:])"
                        with self.assertRaises(ProcessCaptureQuarantineError):
                            capture_process(
                                [
                                    "/usr/bin/python3",
                                    "-I",
                                    "-S",
                                    "-c",
                                    read + echo,
                                    str(lease.descriptor),
                                ],
                                cwd=root,
                                environment={},
                                output_dir=root / "quarantined",
                                max_stream_bytes=16384,
                                timeout_seconds=3,
                                pass_fds=(lease.descriptor,),
                                quarantine_factory=lease.quarantine_factory,
                            )
                        for output in ("safe", "quarantined"):
                            for path in (root / output).rglob("*"):
                                if path.is_file():
                                    payload = path.read_bytes()
                                    for value in (
                                        account,
                                        subject,
                                        document["tokens"]["id_token"],
                                        document["tokens"]["refresh_token"],
                                        "fabricated-person@example.invalid",
                                    ):
                                        self.assertNotIn(value.encode(), payload)
                    self.assertEqual(source.read_bytes(), raw)
