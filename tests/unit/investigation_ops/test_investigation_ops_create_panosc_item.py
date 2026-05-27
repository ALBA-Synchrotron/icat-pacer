import pytest

from exceptions.investigation import InvestigationNotFound
from exceptions.investigation_ops import InvestigationOpsValidationError


@pytest.fixture
def invalid_investigation_ops_investigation(request):
    return request.getfixturevalue(request.param)


class TestInvestigationOpsInvestigationValidation:

    @pytest.mark.parametrize("invalid_investigation_ops_investigation",
                             [
                                 "ops_investigation_missing_end_date",
                                 "ops_investigation_missing_instrument",
                                 "ops_valid_investigation_no_doi"
                             ],
                             indirect=True)
    def test_create_panosc_item_invalid_investigation(self, icat_client, investigation_ops_tasks,
                                                      invalid_investigation_ops_investigation):
        with pytest.raises(InvestigationOpsValidationError):
            investigation_ops_tasks.create_panosc_item(icat_client, invalid_investigation_ops_investigation, None)


    def test_create_panosc_item_non_existent_investigation(self, icat_client, investigation_ops_tasks,
                                                           ops_non_existent_investigation):
        with pytest.raises(InvestigationNotFound):
            investigation_ops_tasks.create_panosc_item(icat_client, ops_non_existent_investigation, None)

    def test_create_panosc_item_valid_investigation(self, icat_client, investigation_ops_tasks,
                                                    ops_valid_investigation_with_doi, panosc_client_mock):
        investigation_ops_tasks.create_panosc_item(icat_client, ops_valid_investigation_with_doi, panosc_client_mock)

    def test_create_panosc_item_industrial_investigation(self, icat_client, investigation_ops_tasks,
                                                         ops_industrial_investigation, panosc_client_mock):
        with pytest.raises(InvestigationOpsValidationError):
            investigation_ops_tasks.create_panosc_item(icat_client, ops_industrial_investigation, panosc_client_mock)
