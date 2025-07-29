import json
import os
import random
import string
from typing import Generator, Any
from unittest.mock import patch, MagicMock

import pytest
from icat.entity import Entity

from helpers.icat_utils import ICATClient

ICAT_AUTH_PLUGIN: str = os.getenv("ICAT_AUTH_PLUGIN", "db")
ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_AUTH_USERNAME: str = os.getenv("ICAT_AUTH_USERNAME", "")
ICAT_AUTH_PASSWORD: str = os.getenv("ICAT_AUTH_PASSWORD", "")


class GenericPACERUnitTest:
    fixtures_dict: dict = {}
    fixtures: list
    entities_teardown: list

    @pytest.fixture(scope="class", autouse=True)
    def load_fixtures(self) -> None:
        self.__load_fixtures()

    @pytest.fixture(scope="session")
    def unittest_user_prefix(self) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=5))

    @pytest.fixture(scope="session")
    def icat_client(self, unittest_user_prefix: str) -> Generator[ICATClient, Any, None]:
        client: ICATClient = ICATClient(url=ICAT_SERVER_URL, username=ICAT_AUTH_USERNAME, password=ICAT_AUTH_PASSWORD,
                                        auth_plugin=ICAT_AUTH_PLUGIN)
        yield client
        self.__teardown_unittest_entities(client, unittest_user_prefix)

    @pytest.fixture(scope="session")
    def datacite_client_mock(self) -> Generator[MagicMock, Any, None]:
        with patch("helpers.datacite.DataciteClient") as DataciteClientMock:
            client_mock = DataciteClientMock.return_value
            client_mock.create_doi.return_value = None

            yield client_mock

    @pytest.fixture(scope="session")
    def mock_psycopg_pool(self) -> Generator[MagicMock, Any, None]:
        with patch("psycopg_pool.ConnectionPool") as MockPool:
            mock_pool = MockPool.return_value

            mock_conn = MagicMock()
            mock_pool.connection.return_value.__enter__.return_value = mock_conn

            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

            mock_cursor.execute.return_value = None
            mock_cursor.fetchall.return_value = [(1,)]
            mock_cursor.fetchone.return_value = [(1,)]

            yield mock_pool

    @pytest.fixture(scope="session")
    def icat_acquisition_dataset_type(self, icat_client: ICATClient) -> Entity:
        dataset_type: Entity = icat_client.search("DatasetType", conditions={"name__eq": "acquisition"},
                                                  flatten_single=True)
        return dataset_type

    @pytest.fixture(scope="session")
    def icat_facility(self, icat_client: ICATClient) -> Generator[Entity, Any, None]:
        facility: Entity = icat_client.new("Facility", name="ICAT Facility")
        facility.create()
        yield facility
        icat_client.delete(facility)

    @pytest.fixture(scope="session")
    def icat_root_user(self, icat_client: ICATClient) -> Entity:
        root_user: Entity = icat_client.search("User", conditions={"name__eq": "root"}, flatten_single=True)
        return root_user

    @pytest.fixture(scope="session")
    def icat_investigation_type(self, icat_client: ICATClient, icat_facility: Entity) -> Generator[Entity, Any, None]:
        investigation_type: Entity = icat_client.new("InvestigationType", name="ICAT Investigation Type",
                                                     facility=icat_facility, description="ICAT Investigation Type")
        investigation_type.create()
        yield investigation_type
        icat_client.delete(investigation_type)

    def __load_fixtures(self) -> None:
        if hasattr(self, 'fixtures') and isinstance(self.fixtures, list):
            for fixture_file in self.fixtures:
                name, _ = fixture_file.split(".")

                fixture_path: str = os.path.join("tests", 'fixtures', 'json', fixture_file)
                with open(fixture_path, "r") as f:
                    self.fixtures_dict[name] = json.load(f)

    def __teardown_unittest_entities(self, icat_client: ICATClient, unittest_user_prefix: str) -> None:
        if hasattr(self, 'entities_teardown') and isinstance(self.entities_teardown, list):
            for entity in self.entities_teardown:
                results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                                   flatten_single=False)
                for i in results:
                    icat_client.delete(i)

                results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                                   flatten_single=False)
                assert results is None
