from exceptions.base import ValidationError


class DatasetValidationError(ValidationError):
    pass


class PayloadParsingError(DatasetValidationError):
    pass


class DatasetParameterValidationError(DatasetValidationError):
    pass


class DatasetDatafileValidationError(DatasetValidationError):
    pass


class DatasetSampleValidationError(DatasetValidationError):
    pass


class DatasetDatafileLimitExceeded(DatasetValidationError):
    pass


class DatasetTypeNotFound(DatasetValidationError):
    pass

class DatasetNotFound(DatasetValidationError):
    pass

class DatasetIndexingError(DatasetValidationError):
    pass