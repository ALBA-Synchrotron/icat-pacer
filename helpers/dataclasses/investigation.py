from dataclasses import dataclass

from exceptions.investigation import InvestigationValidationError


@dataclass
class InvestigationOperationsContext:
    name: str
    operations: list
    visit_id: str


@dataclass
class InvestigationInstrumentContext:
    name: str
    code: str

    def __post_init__(self):
        if not self.name:
            raise InvestigationValidationError("Investigation's instrument name must be provided")

        if not self.code:
            raise InvestigationValidationError("Investigation's instrument code must be provided")


@dataclass
class InvestigationUserContext:
    username: str
    email: str
    role: str

    def __post_init__(self):
        if not self.username:
            raise InvestigationValidationError("InvestigationUser's username must be provided")

        if not self.email:
            raise InvestigationValidationError("InvestigationUser's email must be provided")

        if not self.role:
            raise InvestigationValidationError("InvestigationUser's role must be provided")


@dataclass
class InvestigationContext:
    name: str
    facility: str
    start_date: str
    end_date: str
    release_date: str
    title: str
    summary: str
    instrument: InvestigationInstrumentContext
    type: str
    user_list: list[InvestigationUserContext]
    icat_visit_id: str
    visa_visit_id: int
    sample_acronyms: list[str]
    visit_count: int = 0
    is_reimbursed: bool = False
    visa_sync: bool = False
    icat_sync: bool = False

    def __post_init__(self):
        if not self.name:
            raise InvestigationValidationError("Investigation name must be provided")

        if not self.facility:
            raise InvestigationValidationError("Investigation facility must be provided")

        if self.start_date is None or self.start_date == "":
            raise InvestigationValidationError("Investigation start date must be provided")

        if not self.end_date:
            raise InvestigationValidationError("Investigation end date must be provided")

        if not self.title:
            raise InvestigationValidationError("Investigation title must be provided")

        if not self.summary:
            raise InvestigationValidationError("Investigation summary must be provided")

        if not self.instrument:
            raise InvestigationValidationError("Investigation instrument must be provided")

        if not self.type:
            raise InvestigationValidationError("Investigation type must be provided")

        if not self.icat_visit_id:
            raise InvestigationValidationError("Investigation icat_visit_id must be provided")

        if not self.visa_visit_id:
            raise InvestigationValidationError("Investigation visa_visit_id must be provided")

        if not self.sample_acronyms:
            self.sample_acronyms = []
