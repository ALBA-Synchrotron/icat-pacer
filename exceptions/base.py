class PACERError(Exception):
    pass


class ConfigError(PACERError):
    pass


class ValidationError(PACERError):
    pass

class TooEarlyForRetry(PACERError):
    pass