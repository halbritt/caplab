"""Domain errors raised by trackd operations."""


class TrackdError(Exception):
    """Base class for all trackd domain errors."""


class UnknownShipmentError(TrackdError):
    """Raised when an operation references a tracking id that is not registered."""


class DuplicateShipmentError(TrackdError):
    """Raised when registering a tracking id that already exists."""


class InvalidStatusError(TrackdError):
    """Raised when a scan carries a status outside the allowed set."""
