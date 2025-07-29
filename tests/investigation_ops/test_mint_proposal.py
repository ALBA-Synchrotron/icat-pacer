import logging

import pytest
from icat.entity import Entity
from psycopg_pool import ConnectionPool

from helpers.datacite import DataciteClient
from helpers.dataclasses import InvestigationOperationsContext
from helpers.icat_utils import ICATClient
from helpers.user import create_user_context, UserContext
from tasks.investigation_ops import InvestigationOpsTasks
from tasks.users import UserTasks
from tests.utils.generic_unit_test import GenericPACERUnitTest

logger: logging.Logger = logging.getLogger(__name__)


class TestInvestigationOpsMint(GenericPACERUnitTest):
    # entities_teardown: list = ["User"]

    @pytest.fixture(scope="class")
    def investigation_ops_tasks(self) -> InvestigationOpsTasks:
        return InvestigationOpsTasks(logger)

    @pytest.fixture(scope="class")
    def non_existent_investigation(self) -> InvestigationOperationsContext:
        return InvestigationOperationsContext(name="non-existent-investigation", operations=["mint-proposal"])

    @pytest.fixture(scope="class")
    def investigation_with_doi(self, icat_client: ICATClient, unittest_user_prefix: str, icat_facility: Entity,
                               icat_investigation_type: Entity):
        investigation: Entity = icat_client.new("Investigation", name=f"{unittest_user_prefix}-investigation-with-doi",
                                                facility=icat_facility, doi="10.1234/test-doi", title="test title",
                                                type=icat_investigation_type,
                                                visitId="bltest")
        investigation.create()
        yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

        icat_client.delete(investigation)

    @pytest.fixture(scope="class")
    def investigation_with_no_datasets(self, icat_client: ICATClient, unittest_user_prefix: str, icat_facility: Entity,
                                       icat_investigation_type: Entity):
        investigation: Entity = icat_client.new("Investigation", name=f"{unittest_user_prefix}-investigation-no-data",
                                                facility=icat_facility, title="test title",
                                                type=icat_investigation_type,
                                                visitId="bltest")
        investigation.create()
        yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

        icat_client.delete(investigation)

    @pytest.fixture(scope="class")
    def investigation_with_no_users(self, icat_client: ICATClient, unittest_user_prefix: str, icat_facility: Entity,
                                    icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity):
        investigation: Entity = icat_client.new("Investigation", name=f"{unittest_user_prefix}-investigation-no-users",
                                                facility=icat_facility, title="test title",
                                                type=icat_investigation_type,
                                                visitId="bltest")
        investigation.create()
        dataset: Entity = icat_client.new("Dataset", name=f"{unittest_user_prefix}-dataset",
                                          investigation=investigation, type=icat_acquisition_dataset_type)
        dataset.create()

        yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

        icat_client.delete(dataset)
        icat_client.delete(investigation)

    @pytest.fixture(scope="class")
    def investigation_with_no_dates(self, icat_client: ICATClient, unittest_user_prefix: str, icat_facility: Entity,
                                    icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                    icat_root_user: Entity):
        investigation: Entity = icat_client.new("Investigation", name=f"{unittest_user_prefix}-investigation-no-dates",
                                                facility=icat_facility, title="test title",
                                                type=icat_investigation_type,
                                                visitId="bltest")
        investigation.create()
        dataset: Entity = icat_client.new("Dataset", name=f"{unittest_user_prefix}-dataset",
                                          investigation=investigation, type=icat_acquisition_dataset_type)
        dataset.create()
        inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                           role="Principal Investigator")
        inv_user.create()

        yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

        icat_client.delete(dataset)
        icat_client.delete(inv_user)
        icat_client.delete(investigation)

    @pytest.fixture(scope="class")
    def investigation_good_for_doi(self, icat_client: ICATClient, unittest_user_prefix: str, icat_facility: Entity,
                                   icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                   icat_root_user: Entity):
        investigation: Entity = icat_client.new("Investigation", name=f"{unittest_user_prefix}-investigation-good",
                                                facility=icat_facility, title="test title",
                                                type=icat_investigation_type,
                                                visitId="bltest", startDate="2021-01-01", endDate="2021-01-31",
                                                releaseDate="2021-02-01")
        investigation.create()
        dataset: Entity = icat_client.new("Dataset", name=f"{unittest_user_prefix}-dataset",
                                          investigation=investigation, type=icat_acquisition_dataset_type)
        dataset.create()
        inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                           role="Principal Investigator")
        inv_user.create()

        yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

        icat_client.delete(dataset)
        icat_client.delete(inv_user)
        icat_client.delete(investigation)

    def test_mint_existent_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
                                         mock_psycopg_pool: ConnectionPool,
                                         icat_client: ICATClient,
                                         datacite_client_mock: DataciteClient,
                                         non_existent_investigation: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, non_existent_investigation)
        assert "Investigation non-existent-investigation not found" in str(exc_info.value)

    def test_mint_investigation_already_minted(self, investigation_ops_tasks: InvestigationOpsTasks,
                                               mock_psycopg_pool: ConnectionPool,
                                               icat_client: ICATClient,
                                               datacite_client_mock: DataciteClient,
                                               investigation_with_doi: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_doi)
        assert "already has a DOI" in str(exc_info.value)

    def test_mint_investigation_with_no_datasets(self, investigation_ops_tasks: InvestigationOpsTasks,
                                                 mock_psycopg_pool: ConnectionPool,
                                                 icat_client: ICATClient,
                                                 datacite_client_mock: DataciteClient,
                                                 investigation_with_no_datasets: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_datasets)
        assert "has no datasets, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_with_no_users(self, investigation_ops_tasks: InvestigationOpsTasks,
                                              mock_psycopg_pool: ConnectionPool,
                                              icat_client: ICATClient,
                                              datacite_client_mock: DataciteClient,
                                              investigation_with_no_users: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_users)
        assert "has no users, it will not be minted" in str(exc_info.value)

    def test_mint_investigation_with_no_dates(self, investigation_ops_tasks: InvestigationOpsTasks,
                                              mock_psycopg_pool: ConnectionPool,
                                              icat_client: ICATClient,
                                              datacite_client_mock: DataciteClient,
                                              investigation_with_no_dates: InvestigationOperationsContext) -> None:
        with pytest.raises(Exception) as exc_info:
            investigation_ops_tasks.mint_proposal(
                mock_psycopg_pool, icat_client, datacite_client_mock, investigation_with_no_dates)
        assert "has no releaseDate or startDate, it will not be minted" in str(exc_info.value)

    def test_mint_investigation(self, investigation_ops_tasks: InvestigationOpsTasks,
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
