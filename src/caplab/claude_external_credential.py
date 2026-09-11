"""Borrow a pinned Claude access token without delivering refresh authority."""
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
import re
import time

from caplab.codex_external_credential import ExternalCredentialError, _json, _read_source, _require
from caplab.revbench.codex import ExactSecretStreamQuarantine, _sealed_data_memfd


@dataclass(frozen=True)
class ExternalClaudeCredential:
    descriptor: int
    _secrets: tuple[bytes, ...] = field(repr=False)

    def quarantine_factory(self):
        return ExactSecretStreamQuarantine(self._secrets)


@contextmanager
def open_claude_external_credential(source: Path, *, expected_source_sha256: str,
                                   minimum_access_lifetime_seconds: int):
    """Yield a sealed descriptor containing only the access token.

    Reuse the existing bounded, non-following, pinned source reader and exact
    stream guard. The caller owns authorization, native environment delivery,
    deadline, and guarding every durable output. Local expiry and scope checks
    do not authenticate the provider or identify an account. This function
    never refreshes credentials or changes the source. Exact-byte quarantine
    does not detect transformed secrets or guarantee memory erasure.
    """
    _require(type(expected_source_sha256) is str and
             re.fullmatch(r'[0-9a-f]{64}',expected_source_sha256), 'credential_expected_hash_invalid')
    _require(type(minimum_access_lifetime_seconds) is int and
             1<=minimum_access_lifetime_seconds<=86400, 'credential_required_lifetime_invalid')
    try:
        document=_json(_read_source(source,expected_source_sha256))
        _require(type(document) is dict and type(document.get('claudeAiOauth')) is dict,
                 'claude_credential_shape_invalid')
        oauth=document['claudeAiOauth'];tokens=[]
        for key in ('accessToken','refreshToken'):
            value=oauth.get(key)
            _require(type(value) is str and 24<=len(value)<=8192 and
                     re.fullmatch(r'[A-Za-z0-9._~+/-]+=*',value), 'claude_credential_token_invalid')
            tokens.append(value.encode('ascii'))
        expiry=oauth.get('expiresAt');scopes=oauth.get('scopes')
        _require(type(expiry) is int and
                 expiry >= (time.time()+minimum_access_lifetime_seconds)*1000,
                 'claude_credential_lifetime_insufficient')
        _require(type(scopes) is list and all(type(v) is str for v in scopes)
                 and 'user:inference' in scopes, 'claude_credential_scope_invalid')
    except ExternalCredentialError:
        raise
    except (OSError,ValueError,TypeError,RecursionError,OverflowError):
        raise ExternalCredentialError('claude_credential_input_invalid') from None
    with _sealed_data_memfd('native-claude-access',tokens[0]) as descriptor:
        yield ExternalClaudeCredential(descriptor,tuple(tokens))
