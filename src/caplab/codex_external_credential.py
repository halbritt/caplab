"""Private, explicitly pinned external-token projection; no authentication or refresh."""

import base64
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import time

from caplab.revbench.codex import ExactSecretStreamQuarantine, _sealed_data_memfd

_MAX_BYTES = 65536
_AUTH_CLAIM = "https://api.openai.com/auth"
_PUBLIC_KEYS = frozenset(
    {"id", "label", "email", "name", "organization", "delegations", _AUTH_CLAIM}
)
_QUARANTINE_PROFILES = (
    "credential-private-text/v1", "credential-private-text/v2", "credential-private-text/v3",
    "credential-private-text/v4",
)
_PLAN_CATEGORIES = frozenset(
    {"free", "go", "plus", "pro", "team", "business", "enterprise", "edu", "unknown"}
)
_SCOPES = frozenset({"openid", "profile", "email", "offline_access"})
_ROLES = frozenset({"owner", "admin", "member", "user", "reader"})
_DEFAULT_TITLES = frozenset({"Personal", "personal", "Default", "default"})
_ORG_PATH = (_AUTH_CLAIM, "organizations", None)


class ExternalCredentialError(ValueError):
    """A fixed diagnostic code, with no source path, token or claim in its text."""


@dataclass(frozen=True)
class ExternalCodexCredential:
    descriptor: int
    _secrets: tuple[bytes, ...] = field(repr=False)
    quarantine_profile: str = "credential-private-text/v1"

    def quarantine_factory(self):
        """Create independent stream state; the caller must guard every durable surface."""
        return ExactSecretStreamQuarantine(self._secrets)


def _require(condition, code):
    if not condition:
        raise ExternalCredentialError(code)


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _pairs(rows):
    result = {}
    for key, value in rows:
        _require(key not in result, "credential_json_invalid")
        result[key] = value
    return result


def _json(raw):
    def invalid_constant(_):
        raise ExternalCredentialError("credential_json_invalid")

    def finite_float(raw):
        value = float(raw)
        _require(math.isfinite(value), "credential_json_invalid")
        return value

    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=invalid_constant,
        parse_float=finite_float,
    )


def _identity(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_uid,
        info.st_nlink,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read_source(source, expected):
    path = Path(source)
    _require(
        path.is_absolute() and path.resolve() == path, "credential_source_path_invalid"
    )
    descriptor = os.open(
        path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK
    )
    try:
        before = os.fstat(descriptor)
        _require(
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.getuid()
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_nlink == 1
            and 0 < before.st_size <= _MAX_BYTES,
            "credential_source_metadata_invalid",
        )
        chunks, size = [], 0
        while size <= _MAX_BYTES:
            chunk = os.read(descriptor, _MAX_BYTES + 1 - size)
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        raw = b"".join(chunks)
        _require(
            size == before.st_size
            and _identity(before)
            == _identity(os.fstat(descriptor))
            == _identity(path.lstat()),
            "credential_source_changed",
        )
        _require(_sha(raw) == expected, "credential_source_hash_mismatch")
        return raw
    finally:
        os.close(descriptor)


def _jwt(value, now):
    pieces = value.split(".")
    _require(
        len(pieces) == 3
        and all(re.fullmatch(r"[A-Za-z0-9_-]+", part) for part in pieces),
        "credential_jwt_shape_invalid",
    )
    decoded = []
    for part in pieces[:2]:
        raw = base64.b64decode(
            part + "=" * (-len(part) % 4), altchars=b"-_", validate=True
        )
        _require(
            base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") == part,
            "credential_jwt_encoding_invalid",
        )
        decoded.append(_json(raw))
    header, claims = decoded
    _require(
        type(header) is dict
        and header.get("alg") in ("RS256", "ES256")
        and type(claims) is dict,
        "credential_jwt_shape_invalid",
    )
    _require(
        claims.get("iss") == "https://auth.openai.com"
        and type(claims.get("sub")) is str
        and len(claims["sub"]) >= 12,
        "credential_claim_identity_invalid",
    )
    audience = claims.get("aud")
    _require(
        (type(audience) is str and bool(audience))
        or (
            type(audience) is list
            and audience
            and all(type(v) is str and v for v in audience)
        ),
        "credential_audience_invalid",
    )
    issued, expiry = claims.get("iat"), claims.get("exp")
    _require(
        type(issued) is int
        and type(expiry) is int
        and 0 <= issued < expiry < 2**64
        and issued <= now,
        "credential_claim_time_invalid",
    )
    return header, claims, tuple(part.encode("ascii") for part in pieces)


def _protocol_claim_field(path, key, value, owner, *, authentication_categories=False, identity_alias=False):
    """Classify this occurrence, never remove equal private markers globally."""
    if path == ():
        if authentication_categories and key == "auth_provider":
            return type(value) is str, type(value) is str and value == "password"
        if key == "rat":
            return type(value) is int and value >= 0, False
        if key == "sl":
            return type(value) is bool, False
        if key in ("sid", "session_id"):
            return type(value) is str and bool(value), False
        if key in ("scope", "scp"):
            shape = type(value) is str or (
                type(value) is list and all(type(v) is str for v in value)
            )
            category = type(value) is str and all(
                v in _SCOPES for v in value.split(" ")
            )
            return shape, category
    if path == (_AUTH_CLAIM,):
        if identity_alias and key == "user_id":
            return type(value) is str and bool(value), False
        if authentication_categories and key == "groups":
            return type(value) is list, False
        if key in ("chatgpt_account_id", "chatgpt_user_id", "chatgpt_plan_type"):
            return type(value) is str, (
                key == "chatgpt_plan_type"
                and type(value) is str
                and value in _PLAN_CATEGORIES
            )
        if key == "organizations":
            return type(value) is list, False
    if path == _ORG_PATH:
        if key == "is_default":
            return type(value) is bool, False
        if key == "role":
            return type(value) is str, type(value) is str and value in _ROLES
        if key == "title":
            return type(value) is str, (
                type(value) is str
                and owner.get("is_default") is True
                and value in _DEFAULT_TITLES
            )
    return False, False


def _private_strings(value, *, claim_categories=False, authentication_categories=False, identity_alias=False):
    strings, pending, count = set(), [(value, 0, (), False)], 0
    while pending:
        value, depth, path, category = pending.pop()
        count += 1
        _require(count <= 4096 and depth <= 32, "credential_claim_complexity_exceeded")
        if type(value) is str:
            if value and not category:
                strings.add(value.encode("utf-8"))
        elif type(value) is dict:
            for key, child in value.items():
                public_key, public_value = (
                    _protocol_claim_field(
                        path, key, child, value,
                        authentication_categories=authentication_categories,
                        identity_alias=identity_alias,
                    )
                    if claim_categories
                    else (False, False)
                )
                if key and key not in _PUBLIC_KEYS and not public_key:
                    strings.add(key.encode("utf-8"))
                pending.append((child, depth + 1, path + (key,), public_value))
        elif type(value) is list:
            scope_list = (
                claim_categories
                and path in (("scp",), ("scope",))
                and all(type(v) is str for v in value)
            )
            pending.extend(
                (child, depth + 1, path + (None,), scope_list and child in _SCOPES)
                for child in value
            )
        else:
            _require(
                value is None or type(value) in (int, float, bool),
                "credential_claim_type_invalid",
            )
    return strings


def _claim_strings(claims, quarantine_profile):
    private = {
        k: v for k, v in claims.items() if k not in ("iss", "aud", "iat", "exp", "sub")
    }
    return _private_strings(
        private,
        claim_categories=quarantine_profile in ("credential-private-text/v2", "credential-private-text/v3", "credential-private-text/v4"),
        authentication_categories=quarantine_profile in ("credential-private-text/v3", "credential-private-text/v4"),
        identity_alias=quarantine_profile == "credential-private-text/v4",
    )


def _projection(
    raw,
    account_sha256,
    subject_sha256,
    lifetime,
    *,
    quarantine_profile="credential-private-text/v1",
):
    _require(
        quarantine_profile in _QUARANTINE_PROFILES,
        "credential_quarantine_profile_invalid",
    )
    document = _json(raw)
    _require(
        type(document) is dict
        and set(document) == {"auth_mode", "OPENAI_API_KEY", "tokens", "last_refresh"}
        and document["auth_mode"] == "chatgpt"
        and document["OPENAI_API_KEY"] is None,
        "credential_cache_shape_invalid",
    )
    tokens = document["tokens"]
    _require(
        type(tokens) is dict
        and set(tokens) == {"id_token", "access_token", "refresh_token", "account_id"}
        and all(type(value) is str and len(value) >= 12 for value in tokens.values()),
        "credential_token_shape_invalid",
    )
    refresh = document["last_refresh"]
    _require(
        type(refresh) is str
        and re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,9})?Z",
            refresh,
        ),
        "credential_refresh_time_invalid",
    )
    datetime.strptime(refresh[:19], "%Y-%m-%dT%H:%M:%S")
    _require(
        _sha(tokens["account_id"].encode()) == account_sha256,
        "credential_account_mismatch",
    )
    now = time.time()
    secrets = {
        raw,
        *(value.encode("utf-8") for value in tokens.values()),
        refresh.encode("ascii"),
    }
    for name in ("id_token", "access_token"):
        header, claims, segments = _jwt(tokens[name], now)
        _require(
            _sha(claims["sub"].encode()) == subject_sha256,
            "credential_subject_mismatch",
        )
        account = claims.get(_AUTH_CLAIM)
        _require(
            type(account) is dict
            and account.get("chatgpt_account_id") == tokens["account_id"],
            "credential_account_claim_mismatch",
        )
        if name == "access_token":
            _require(
                claims["exp"] >= now + lifetime,
                "credential_access_lifetime_insufficient",
            )
        secrets.update(segments)
        secrets.add(claims["sub"].encode())
        secrets.update(
            _private_strings(
                {k: v for k, v in header.items() if k not in ("alg", "typ")}
            )
        )
        secrets.update(_claim_strings(claims, quarantine_profile))
    projected = document | {
        "auth_mode": "chatgptAuthTokens",
        "tokens": tokens | {"refresh_token": ""},
    }
    payload = (json.dumps(projected, sort_keys=True) + "\n").encode("utf-8")
    _require(len(payload) <= _MAX_BYTES, "credential_projection_too_large")
    secrets.add(payload)
    return payload, tuple(sorted(secrets, key=lambda value: (len(value), value)))


@contextmanager
def open_codex_external_credential(
    source: Path,
    *,
    expected_source_sha256: str,
    expected_account_sha256: str,
    expected_subject_sha256: str,
    minimum_access_lifetime_seconds: int,
    quarantine_profile: str = "credential-private-text/v1",
):
    """Borrow sealed external-token input and independent exact-byte stream guards.

    Expected hashes belong to private administration and must be independently
    selected. Local JWT checks do not authenticate signatures or the provider.
    Caller owns authorization, native read-only mounting, all output guards and
    a deadline within the required lifetime. No refresh or source mutation occurs.
    Descriptor validity ends on context exit; Python secret-memory erasure and
    transformed-secret detection are not provided. Short claim strings can cause
    quarantine false positives and make an otherwise parseable cache unusable.
    Explicit v2 recognizes declared protocol fields and closed administration
    categories; equal text at private occurrences remains guarded. Neither
    profile hides all administration metadata or authorizes publication.
    """
    _require(
        quarantine_profile in _QUARANTINE_PROFILES,
        "credential_quarantine_profile_invalid",
    )
    for digest in (
        expected_source_sha256,
        expected_account_sha256,
        expected_subject_sha256,
    ):
        _require(
            type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest),
            "credential_expected_hash_invalid",
        )
    _require(
        type(minimum_access_lifetime_seconds) is int
        and 1 <= minimum_access_lifetime_seconds <= 86400,
        "credential_required_lifetime_invalid",
    )
    try:
        raw = _read_source(source, expected_source_sha256)
        payload, secrets = _projection(
            raw,
            expected_account_sha256,
            expected_subject_sha256,
            minimum_access_lifetime_seconds,
            quarantine_profile=quarantine_profile,
        )
    except ExternalCredentialError:
        raise
    except (OSError, ValueError, TypeError, RecursionError, OverflowError):
        raise ExternalCredentialError("credential_input_invalid") from None
    with _sealed_data_memfd("external-native-auth", payload) as descriptor:
        yield ExternalCodexCredential(descriptor, secrets, quarantine_profile)
