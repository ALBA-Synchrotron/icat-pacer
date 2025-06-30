import json
import os
import random
import string
from typing import Generator, Any

import pytest

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
    def load_fixtures(self):
        self.__load_fixtures()

    @pytest.fixture(scope="session")
    def unittest_user_prefix(self) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=5))

    @pytest.fixture(scope="session")
    def icat_client(self, unittest_user_prefix: str) -> Generator[ICATClient, Any, None]:
        client: ICATClient = ICATClient(url=ICAT_SERVER_URL, username=ICAT_AUTH_USERNAME, password=ICAT_AUTH_PASSWORD,
                                        auth_plugin=ICAT_AUTH_PLUGIN)
        yield client
        self.teardown_unittest_entities(client, unittest_user_prefix)

    def __load_fixtures(self) -> None:
        for fixture_file in self.fixtures:
            name, _ = fixture_file.split(".")

            fixture_path: str = os.path.join("tests", 'fixtures', 'json', fixture_file)
            with open(fixture_path, "r") as f:
                self.fixtures_dict[name] = json.load(f)

    def teardown_unittest_entities(self, icat_client: ICATClient, unittest_user_prefix: str):

        for entity in self.entities_teardown:
            results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                               flatten_single=False)
            for i in results:
                icat_client.delete(i)

            results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                               flatten_single=False)
            assert results is None
