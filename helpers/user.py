from dataclasses import dataclass, field
import json


@dataclass
class Affiliation:
    id: int = 0
    name: str = ""
    code: str = ""
    department_name: str = ""
    department_code: str = ""
    unit: str = ""
    city: str = ""
    country_code: str = ""


@dataclass
class UserContext:
    first_name: str
    last_name: str
    orcid: str = ""
    email: str = None
    is_staff: bool = False
    enabled: bool = False
    uos_id: int = None
    usernames: list[str] = None
    affiliation: Affiliation = field(default_factory=Affiliation)


def get_affiliation_name(affiliation: Affiliation, limit: int = -1) -> str:
    ret: str = f"{', '.join(i for i in [affiliation.name, affiliation.unit, affiliation.department_name] if i != '')}"
    if limit > 0:
        ret = ret[:limit]
    return ret


def create_user_context(user_data: str or dict, username_prefix: str = "") -> UserContext:
    user_dict: dict = json.loads(user_data) if isinstance(user_data, str) else user_data
    aff = user_dict.get("affiliation", {})
    return UserContext(
        first_name=user_dict.get("first_name"),
        last_name=user_dict.get("last_name"),
        orcid=user_dict.get("ORCID"),
        email=user_dict.get("email"),
        is_staff=user_dict.get("is_staff", False),
        enabled=user_dict.get("enabled", False),
        uos_id=user_dict.get("id"),
        usernames=[f"{username_prefix}{i.get('username')}" for i in user_dict.get("user_list", [])],
        affiliation=Affiliation(
            id=aff.get("id") or 0,
            name=aff.get("name") or "",
            code=aff.get("code") or "",
            department_name=aff.get("department_name") or "",
            department_code=aff.get("department_code") or "",
            unit=aff.get("unit") or "",
            city=aff.get("city") or "",
            country_code=aff.get("country_code", ""),
        )
    )
