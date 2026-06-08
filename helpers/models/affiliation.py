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
