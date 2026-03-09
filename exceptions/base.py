class PACERError(Exception):
    pass


class ConfigError(PACERError):
    """Configuration related errors."""


class ValidationError(PACERError):
    """Input validation errors."""
