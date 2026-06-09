import pytest
from pydantic import ValidationError

from exceptions.investigation_ops import InvestigationOpsValidationError
from helpers.contexts.investigation_ops import create_investigation_ops_context
from helpers.models.investigation_operations import InvestigationOperationsContext


@pytest.fixture
def inv_ops_str(request):
    return request.getfixturevalue(request.param)


class TestInvestigationOpsPayloadValidation:

    @pytest.mark.parametrize("inv_ops_str",
                             [
                                 "inv_ops_invalid_payload_empty_name",
                                 "inv_ops_invalid_payload_empty_operations",
                                 "inv_ops_invalid_payload_invalid_operations",
                                 "inv_ops_invalid_payload_empty_visit_id"
                             ],
                             indirect=True)
    def test_inv_ops_payload_validation(self, icat_client, inv_ops_str):
        with pytest.raises((ValidationError, InvestigationOpsValidationError)):
            _: InvestigationOperationsContext = create_investigation_ops_context(inv_ops_str)

