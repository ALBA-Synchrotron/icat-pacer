from dataclasses import dataclass

from exceptions.user import UserValidationError


@dataclass
class Affiliation:
    id: int
    name: str
    code: str
    department_name: str
    department_code: str
    unit: str
    city: str
    country_code: str

    def __post_init__(self):
        if not self.id:
            raise UserValidationError("Affiliation ID is required")

    def get_affiliation_name(self, limit: int = -1) -> str:
        ret: str = f"{', '.join(i for i in [self.name, self.unit, self.department_name] if i != '')}"
        if limit > 0:
            ret = ret[:limit]
        return ret

@dataclass
class UserContext:
    first_name: str
    last_name: str
    email: str
    enabled: bool
    uos_id: int
    usernames: list[str]
    affiliation: Affiliation
    orcid: str = ""
    is_staff: bool = False

    def __post_init__(self):
        if not self.first_name:
            raise UserValidationError("First name is required")

        if not self.last_name:
            raise UserValidationError("Last name is required")

        if not self.email:
            raise UserValidationError("Email is required")

        if not hasattr(self, "enabled") or self.enabled is None:
            raise UserValidationError("Enabled is required")

        if not self.uos_id:
            raise UserValidationError("UOS ID is required")

        if not self.usernames:
            raise UserValidationError("Usernames is required")

        if not self.affiliation:
            raise UserValidationError("Affiliation is required")
