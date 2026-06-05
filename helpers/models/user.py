from __future__ import annotations
from __future__ import annotations

from pydantic import BaseModel, Field


class Affiliation(BaseModel):
    id: int = Field(gt=0)
    name: str = ""
    code: str = ""
    department_name: str = ""
    department_code: str = ""
    unit: str = ""
    city: str = ""
    country_code: str = ""

    def get_affiliation_name(self, limit: int = -1) -> str:
        ret = ", ".join(
            x for x in [self.name, self.unit, self.department_name] if x
        )
        return ret[:limit] if limit > 0 else ret


class UserContext(BaseModel):
    first_name: str
    last_name: str
    email: str
    enabled: bool
    uos_id: int = Field(gt=0)
    usernames: list[str] = Field(min_length=1)
    affiliation: Affiliation
    orcid: str = ""
    is_staff: bool = False

