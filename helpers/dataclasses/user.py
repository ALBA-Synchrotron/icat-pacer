from dataclasses import dataclass


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
            raise ValueError("First name is required")

        if not self.last_name:
            raise ValueError("Last name is required")

        if not self.email:
            raise ValueError("Email is required")

        if not self.enabled:
            raise ValueError("Enabled is required")

        if not self.uos_id:
            raise ValueError("UOS ID is required")

        if not self.usernames:
            raise ValueError("Usernames is required")

        if not self.affiliation:
            raise ValueError("Affiliation is required")
