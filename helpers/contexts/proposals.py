import json
from datetime import datetime

from dateutil.relativedelta import relativedelta

import globals_var
from exceptions.investigation import InvestigationValidationError
from helpers.dataclasses.investigation import InvestigationContext, InvestigationInstrumentContext, \
    InvestigationUserContext
from helpers.static_settings import ICAT_USER_ROLE_PARTICIPANT
from helpers.utils.datetime import try_parse_datetime


def simplify_redundant_user_roles(user_list: list) -> list:
    ret: list = []
    usernames: list = list(set([i.username for i in user_list]))
    for username in usernames:
        user_roles = list(filter(lambda x: x.username == username, user_list))
        if len(user_roles) > 1 and ICAT_USER_ROLE_PARTICIPANT in [i.role for i in user_roles]:
            user_roles = list(filter(lambda x: x.role != ICAT_USER_ROLE_PARTICIPANT, user_roles))
        if user_roles not in ret:
            ret.extend(user_roles)
    return ret


def create_investigation_context(investigation_data: str | dict,
                                 name_prefix: str = '') -> InvestigationContext:
    inv_ctx: InvestigationContext
    investigation_dict: dict = json.loads(investigation_data) if isinstance(investigation_data,
                                                                            str) else investigation_data
    ingestion_settings: dict = globals_var.ingestion_settings.get("investigation", {})

    investigation_name: str = f"{name_prefix}{investigation_dict.get('name')}"
    facility_name: str = investigation_dict.get('facility', ingestion_settings.get("defaultFacilityName", ""))
    start_date_str: str = investigation_dict.get("start_date")
    end_date_str: str = investigation_dict.get("end_date")
    investigation_title: str = investigation_dict.get("title", "")
    investigation_summary: str = investigation_dict.get("summary", "")
    instrument: dict = investigation_dict.get("instrument")
    investigation_type: str = investigation_dict.get("type", "")
    investigation_user_list: list = investigation_dict.get("user_list", [])
    investigation_visit_count: int = investigation_dict.get("visit_count", 0)
    is_investigation_reimbursed: bool = investigation_dict.get("is_reimbursed", False)
    sync_with_icat: bool = investigation_dict.get("icat_sync", False)
    sync_with_visa: bool = investigation_dict.get("visa_sync", False)
    icat_visit_id: str = investigation_dict.get("icat_visit_id",
                                                instrument.get("code", "").lower() if instrument else "")
    visa_visit_id: int = investigation_dict.get("visa_visit_id",
                                                int(investigation_name.replace("-", "") if investigation_name else "0"))
    sample_acronyms: list = investigation_dict.get("sample_acronyms", [])
    is_industrial: bool = investigation_dict.get("is_industrial", False)

    investigation_users_ctx: list = [
        InvestigationUserContext(username=i.get("username", ""), email=i.get("email", ""), role=i.get("role", ""))
        for i in investigation_user_list]

    if not start_date_str or not end_date_str:
        raise InvestigationValidationError("Start and end dates must be provided")

    start_date: datetime = try_parse_datetime(start_date_str)
    end_date: datetime = try_parse_datetime(end_date_str)

    release_date_str: str = investigation_dict.get("release_date", "")
    if is_industrial:
        release_date = None
    elif release_date_str:
        release_date: datetime = try_parse_datetime(release_date_str)
    else:
        release_date: datetime = end_date + relativedelta(years=ingestion_settings.get("defaultEmbargoYears", 3))

    if not instrument:
        raise InvestigationValidationError("Instrument must be provided")

    inv_ctx = InvestigationContext(
        name=investigation_name,
        facility=facility_name,
        start_date=start_date,
        end_date=end_date,
        release_date=release_date,
        title=investigation_title,
        summary=investigation_summary,
        instrument=InvestigationInstrumentContext(name=instrument.get("name", ""), code=instrument.get("code", "")),
        type=investigation_type,
        user_list=simplify_redundant_user_roles(investigation_users_ctx),
        visit_count=investigation_visit_count,
        is_reimbursed=is_investigation_reimbursed,
        visa_sync=sync_with_visa,
        icat_sync=sync_with_icat,
        icat_visit_id=icat_visit_id,
        visa_visit_id=visa_visit_id,
        sample_acronyms=sample_acronyms,
        is_industrial=is_industrial,
    )

    return inv_ctx
