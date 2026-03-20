from exceptions.base import ValidationError


class UserValidationError(ValidationError):
    pass

class UserNotFound(UserValidationError):
    pass