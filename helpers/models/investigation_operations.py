from pydantic import BaseModel, Field, field_validator

from exceptions.investigation_ops import InvestigationOpsValidationError
from helpers.static_settings import INV_OPS


class InvestigationOperationsContext(BaseModel):
    name: str = Field(min_length=1)
    operations: list = Field(min_length=1)
    visit_id: str = Field(min_length=1)

    @field_validator("operations")
    @classmethod
    def validate_role(cls, v):
        invalid = [i for i in v if i not in INV_OPS.values()]
        if invalid:
            raise InvestigationOpsValidationError(f"Invalid operations, valid options are: {','.join(INV_OPS.values())}")

        return v
