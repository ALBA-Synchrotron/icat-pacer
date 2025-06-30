from dataclasses import dataclass, field
import json


@dataclass
class Affiliation:
    name: str = ""
    code: str = ""
    department_name: str = ""
    department_code: str = ""
    unit: str = ""
    city: str = ""


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


def create_user_context(user_data: str or dict, username_prefix: str = "") -> UserContext:
    user_dict: dict = json.loads(user_data) if isinstance(user_data, str) else user_data
    aff = user_dict.get("affiliation", {})
    return UserContext(
        first_name=user_dict.get("first_name"),
        last_name=user_dict.get("last_name"),
        orcid=user_dict.get("ORCID", ""),
        email=user_dict.get("email"),
        is_staff=user_dict.get("is_staff", False),
        enabled=user_dict.get("enabled", False),
        uos_id=user_dict.get("id"),
        usernames=[f"{username_prefix}{i.get("username")}" for i in user_dict.get("user_list", [])],
        affiliation=Affiliation(
            name=aff.get("name", ""),
            code=aff.get("code", ""),
            department_name=aff.get("department_name", ""),
            department_code=aff.get("department_code", ""),
            unit=aff.get("unit", ""),
            city=aff.get("city", ""),
        )
    )
