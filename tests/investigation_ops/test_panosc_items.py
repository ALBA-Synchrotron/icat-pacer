import logging

import pytest
from icat.entity import Entity
from psycopg_pool import ConnectionPool

from helpers.datacite import DataciteClient
from helpers.dataclasses import InvestigationOperationsContext
from helpers.icat_utils import ICATClient
from helpers.panosc import PaNOSCClient
from tasks.investigation_ops import InvestigationOpsTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestInvestigationOpsPSSItems(GenericPACERUnitTest):
    # entities_teardown: list = ["User"]

    def test_create_item_non_existent_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                             icat_client: ICATClient,
                                             datacite_client_mock: DataciteClient,
                                             non_existent_investigation: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.create_panosc_item(
                icat_client, non_existent_investigation, datacite_client_mock,
            )
        assert "Investigation non-existent-investigation not found" in str(exc_info.value)

    def test_create_item_investigation_with_no_dates(self, investigation_ops_tasks: InvestigationOpsTasks,
                                              icat_client: ICATClient,
                                              panosc_client_mock: PaNOSCClient,
                                              investigation_with_no_dates: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.create_panosc_item(
                icat_client, investigation_with_no_dates, panosc_client_mock,
            )
        assert "has no releaseDate, endDate or startDate, it will not be minted" in str(exc_info.value)

    def test_create_item_investigation_with_no_doi(self, investigation_ops_tasks: InvestigationOpsTasks,
                                            icat_client: ICATClient,
                                            panosc_client_mock: PaNOSCClient,
                                            investigation_with_no_doi: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.create_panosc_item(
                icat_client, investigation_with_no_doi, panosc_client_mock,
            )
        assert "has no DOI" in str(exc_info.value)

    def test_create_item_investigation_with_no_instrument(self, investigation_ops_tasks: InvestigationOpsTasks,
                                            icat_client: ICATClient,
                                            panosc_client_mock: PaNOSCClient,
                                            investigation_with_no_instrument: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.create_panosc_item(
                icat_client, investigation_with_no_instrument, panosc_client_mock,
            )
        assert "has no instruments, it will not be minted" in str(exc_info.value)

    def test_create_item_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                            icat_client: ICATClient,
                                            panosc_client_mock: PaNOSCClient,
                                            investigation_good_for_item_creation: InvestigationOperationsContext) -> None:
        investigation_ops_tasks.create_panosc_item(
            icat_client, investigation_good_for_item_creation, panosc_client_mock,
        )

    def asdtest_mint_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                   mock_psycopg_pool: ConnectionPool,
                                   icat_client: ICATClient,
                                   datacite_client_mock: DataciteClient,
                                   investigation_good_for_doi: InvestigationOperationsContext) -> None:
        investigation_ops_tasks.mint_proposal(
            mock_psycopg_pool, icat_client, datacite_client_mock, investigation_good_for_doi)

        investigation: Entity = icat_client.search("Investigation",
                                                   conditions={"name__eq": investigation_good_for_doi.name},
                                                   flatten_single=True)
        assert investigation.doi is not None

        calls: list = mock_psycopg_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.call_args_list
        sql_statements: list = [call.args[0] for call in calls]

        has_insert = any("UPDATE" in sql.upper() for sql in sql_statements)
        assert has_insert, "No INSERT statements executed"
