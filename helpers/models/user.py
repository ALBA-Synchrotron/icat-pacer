from __future__ import annotations
from __future__ import annotations

from pydantic import BaseModel, Field

from helpers.models.affiliation import Affiliation


class UserContext(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    enabled: bool
    uos_id: int = Field(gt=0)
    usernames: list[str] = Field(min_length=1)
    affiliation: Affiliation
    orcid: str = ""
    is_staff: bool = False
