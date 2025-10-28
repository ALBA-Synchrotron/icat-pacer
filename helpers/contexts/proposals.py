import json
from datetime import datetime

from dateutil.relativedelta import relativedelta

from helpers.dataclasses.investigation import InvestigationContext, InvestigationInstrumentContext, \
    InvestigationUserContext
from helpers.utils.datetime import try_parse_datetime


def create_investigation_context(investigation_data: str | dict, ingestion_settings: dict,
                                 name_prefix: str = '') -> InvestigationContext:
    inv_ctx: InvestigationContext
    investigation_dict: dict = json.loads(investigation_data) if isinstance(investigation_data,
                                                                            str) else investigation_data

    investigation_name: str = f"{name_prefix}{investigation_dict.get('name')}"
    facility_name: str = investigation_dict.get('facility', ingestion_settings.get("defaultFacilityName", ""))
    start_date_str: str = investigation_dict.get("start_date", "")
    end_date_str: str = investigation_dict.get("end_date", "")
    investigation_title: str = investigation_dict.get("title", "")
    investigation_summary: str = investigation_dict.get("summary", "")
    instrument: dict = investigation_dict.get("instrument", {})
    investigation_type: str = investigation_dict.get("type", "")
    investigation_user_list: list = investigation_dict.get("user_list", [])
    investigation_visit_count: int = investigation_dict.get("visit_count", 0)
    is_investigation_reimbursed: bool = investigation_dict.get("is_reimbursed", False)
    sync_with_icat: bool = investigation_dict.get("icat_sync", False)
    sync_with_visa: bool = investigation_dict.get("visa_sync", False)

    start_date: datetime = try_parse_datetime(start_date_str)
    end_date: datetime = try_parse_datetime(end_date_str)

    release_date_str: str = investigation_dict.get("release_date", "")
    if release_date_str:
        release_date: datetime = try_parse_datetime(release_date_str)
    else:
        release_date: datetime = end_date + relativedelta(years=ingestion_settings.get("defaultEmbargoYears", 9999))

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
        user_list=[
            InvestigationUserContext(username=i.get("username", ""), email=i.get("email", ""), role=i.get("role", ""))
            for i in investigation_user_list],
        visit_count=investigation_visit_count,
        is_reimbursed=is_investigation_reimbursed,
        visa_sync=sync_with_visa,
        icat_sync=sync_with_icat,
    )

    return inv_ctx
