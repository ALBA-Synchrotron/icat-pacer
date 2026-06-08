import pytest
from pydantic import ValidationError

from exceptions.investigation import InvestigationValidationError
from helpers.contexts.investigation import create_investigation_context


@pytest.fixture
def invalid_investigation_payload(request):
    return request.getfixturevalue(request.param)


class TestInvestigationPayloadValidation:

    @pytest.mark.parametrize("invalid_investigation_payload",
                             [
                                 "investigation_payload_empty_name", "investigation_payload_empty_facility",
                                 "investigation_payload_empty_start_date", "investigation_payload_empty_end_date",
                                 "investigation_payload_empty_title", "investigation_payload_empty_summary",
                                 "investigation_payload_empty_instrument", "investigation_payload_empty_type",
                                 "investigation_payload_invalid_missing_username",
                                 "investigation_payload_invalid_missing_email",
                                 "investigation_payload_invalid_missing_role",
                                 "investigation_payload_invalid_missing_instrument_name",
                                 "investigation_payload_invalid_missing_instrument_code",
                                 "investigation_payload_invalid_missing_icat_visit_id",
                                 "investigation_payload_invalid_missing_visa_visit_id",
                                 "investigation_payload_invalid_user_role_invalid"
                             ],
                             indirect=True)
    def test_invalid_investigation_payload(self, invalid_investigation_payload):
        with pytest.raises((ValidationError, InvestigationValidationError)):
            _ = create_investigation_context(invalid_investigation_payload)

    def test_valid_investigation_payload(self, valid_investigation):
        _ = create_investigation_context(valid_investigation)
