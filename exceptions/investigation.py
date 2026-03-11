from exceptions.base import ValidationError


class InvestigationValidationError(ValidationError):
    pass

class InvestigationFacilityNotFound(InvestigationValidationError):
    pass

class InvestigationTypeNotFound(InvestigationValidationError):
    pass

class InvestigationNotFound(InvestigationValidationError):
    pass

class InvestigationInstrumentMismatch(InvestigationValidationError):
    pass