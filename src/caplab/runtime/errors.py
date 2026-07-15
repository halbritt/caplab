"""Explicit failures at CAPLAB runtime trust boundaries."""


class RuntimeContractError(RuntimeError):
    """Base class for a refused runtime operation."""


class OperationConflict(RuntimeContractError):
    """An operation ID was reused for a different request."""


class ObjectMismatch(RuntimeContractError):
    """Garage bytes do not match their content-derived identity."""


class CopyMismatch(RuntimeContractError):
    """The independent local copy does not match its identity."""


class LocatorMismatch(RuntimeContractError):
    """A retained locator differs from the canonical locator."""


class MetadataMismatch(RuntimeContractError):
    """Registered metadata does not match its retained identity."""


class RegistrationMissing(RuntimeContractError):
    """No completed registration exists for an operation."""
