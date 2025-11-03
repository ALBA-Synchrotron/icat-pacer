import json
from dataclasses import dataclass, field
from datetime import datetime

from dateutil.relativedelta import relativedelta

from helpers import settings
from helpers.dataclasses import InvestigationContext
from helpers.datetime import try_parse_datetime
from helpers.settings import ICAT_USER_ROLE_PARTICIPANT


def simplify_redundant_user_roles(user_list: list) -> list:
    ret: list = []
    for user in user_list:
        username: str = user.get("username")
        user_roles = list(filter(lambda x: x["username"] == username, user_list))
        if len(user_roles) > 1 and ICAT_USER_ROLE_PARTICIPANT in [i["role"] for i in user_roles]:
            user_roles = list(filter(lambda x: x["role"] != ICAT_USER_ROLE_PARTICIPANT, user_roles))
        if user_roles not in ret:
            ret.extend(user_roles)
    return ret

def create_investigation_context(investigation_data: str or dict, name_prefix: str = '') -> InvestigationContext:
    investigation_dict: dict = json.loads(investigation_data) if isinstance(investigation_data,
                                                                            str) else investigation_data

    if not investigation_dict.get("name", ""):
        raise ValueError("Investigation name must be provided.")

    start_date_str: str = investigation_dict.get("start_date", "")
    end_date_str: str = investigation_dict.get("end_date", "")
    if not start_date_str or not end_date_str:
        raise ValueError("Start date and End date must be provided.")

    start_date: datetime = try_parse_datetime(start_date_str)
    end_date: datetime = try_parse_datetime(end_date_str)

    release_date_str: str = investigation_dict.get("release_date", "")
    if release_date_str:
        release_date: datetime = try_parse_datetime(release_date_str)
    else:
        release_date: datetime = end_date + relativedelta(years=settings.ICAT_EMBARGO_YEARS_AMOUNT)

    users_list: list = investigation_dict.get("user_list", [])

    return InvestigationContext(
        name=f"{name_prefix}{investigation_dict.get('name')}",
        facility=investigation_dict.get("facility", "ALBA"),
        start_date=start_date,
        end_date=end_date,
        release_date=release_date,
        title=investigation_dict.get("title", ""),
        summary=investigation_dict.get("summary", ""),
        instrument=investigation_dict.get("instrument", {"name": "", "code": ""}),
        type=investigation_dict.get("type", ""),
        user_list=simplify_redundant_user_roles(users_list),
        visit_count=investigation_dict.get("visit_count", 0),
        is_reimbursed=investigation_dict.get("is_reimbursed", False),
        doi=investigation_dict.get("doi", ""),
        url=investigation_dict.get("url", ""),
        visa_sync=investigation_dict.get("visa_sync", False),
        icat_sync=investigation_dict.get("icat_sync", False)
    )
