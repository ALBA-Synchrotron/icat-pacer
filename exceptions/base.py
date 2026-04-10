class PACERError(Exception):
    def __init__(self, message: str, original_exception: Exception = None):
        if original_exception and original_exception.__traceback__:
            tb = original_exception.__traceback__
            message = f"{message} @ {tb.tb_frame.f_code.co_filename}:{tb.tb_lineno}"

        super().__init__(message)


class ConfigError(PACERError):
    pass


class ValidationError(PACERError):
    pass

class TooEarlyForRetry(PACERError):
    pass