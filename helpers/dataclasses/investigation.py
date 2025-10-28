from dataclasses import dataclass


@dataclass
class InvestigationOperationsContext:
    name: str
    operations: list

@dataclass
class InvestigationInstrumentContext:
    name: str
    code: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("Investigation's instrument name must be provided")

        if not self.code:
            raise ValueError("Investigation's instrument code must be provided")

@dataclass
class InvestigationUserContext:
    username: str
    email: str
    role: str

    def __post_init__(self):
        if not self.username:
            raise ValueError("InvestigationUser's username must be provided")

        if not self.email:
            raise ValueError("InvestigationUser's email must be provided")

        if not self.role:
            raise ValueError("InvestigationUser's role must be provided")

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
    visit_count: int = 0
    is_reimbursed: bool = False
    visa_sync: bool = False
    icat_sync: bool = False

    def __post_init__(self):
        if not self.name:
            raise ValueError("Investigation name must be provider")

        if not self.facility:
            raise ValueError("Investigation facility must be provided")

        if not self.start_date:
            raise ValueError("Investigation start date must be provided")

        if not self.end_date:
            raise ValueError("Investigation end date must be provided")

        if not self.title:
            raise ValueError("Investigation title must be provided")

        if not self.summary:
            raise ValueError("Investigation summary must be provided")

        if not self.instrument:
            raise ValueError("Investigation instrument must be provided")

        if not self.type:
            raise ValueError("Investigation type must be provided")





