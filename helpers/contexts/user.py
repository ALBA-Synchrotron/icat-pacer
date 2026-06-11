import json

from helpers.models.user import UserContext


def create_user_context(
        user_data: str | dict,
        username_prefix: str = "",
) -> UserContext:
    user_dict = (
        json.loads(user_data)
        if isinstance(user_data, str)
        else user_data
    )

    aff = user_dict.get("affiliation", {})

    return UserContext.model_validate(
        {
            "first_name": user_dict.get("first_name"),
            "last_name": user_dict.get("last_name"),
            "orcid": user_dict.get("ORCID", "") or "",
            "email": user_dict.get("email"),
            "is_staff": user_dict.get("is_staff", False),
            "enabled": user_dict.get("enabled"),
            "uos_id": user_dict.get("id"),
            "usernames": [
                f"{username_prefix}{u['username']}"
                for u in user_dict.get("user_list", [])
            ],
            "affiliation": {
                "id": aff.get("id", 0),
                "name": aff.get("name", "") or "",
                "code": aff.get("code", "") or "",
                "department_name": aff.get("department_name", "") or "",
                "department_code": aff.get("department_code", "") or "",
                "unit": aff.get("unit", "") or "",
                "city": aff.get("city", "") or "",
                "country_code": aff.get("country_code", "") or "",
            },
        }
    )
