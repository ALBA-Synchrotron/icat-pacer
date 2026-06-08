from enum import Enum

from pydantic import BaseModel, Field

from helpers.static_settings import INV_OPS

InvestigationOperationsEnum = Enum(
    "InvestigationOperationsEnum",
    {role.upper(): role for role in INV_OPS},
)

class InvestigationOperationsContext(BaseModel):
    name: str = Field(min_length=1)
    operations: list[InvestigationOperationsEnum]
    visit_id: str = Field(min_length=1)