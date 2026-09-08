"""User-facing error types and their stable CLI boundary."""


class CutoffGuardError(ValueError):
    """Base class for expected input/configuration failures."""

    exit_code = 4


class InputFormatError(CutoffGuardError):
    """The input file or record is malformed."""


class SchemaError(CutoffGuardError):
    """A structured input does not satisfy its declared schema."""


class AuditConfigurationError(CutoffGuardError):
    """The audit command was given an invalid configuration."""
