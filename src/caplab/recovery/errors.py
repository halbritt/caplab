"""Typed failures for the P5-only custody surface."""


class RecoveryError(RuntimeError):
    """Base class for an expected P5 custody refusal."""


class AuthorizationMismatch(RecoveryError):
    """The requested effect is outside the frozen P5 authority."""


class AuthorizationExpired(RecoveryError):
    """The P5 authority is no longer active."""


class RecoverySourceMismatch(RecoveryError):
    """The proposed recovery source is absent or does not match its identity."""


class RecoveryTargetMismatch(RecoveryError):
    """The recovered target failed read-back verification."""


class UnknownPurgeIdentity(RecoveryError):
    """No live registration matches the requested purge identity."""


class DependencyRetained(RecoveryError):
    """A retained dependency prevents deletion of the P5 closure."""


class InjectedInterruption(RecoveryError):
    """The selected P5 registration checkpoint interrupted as requested."""
