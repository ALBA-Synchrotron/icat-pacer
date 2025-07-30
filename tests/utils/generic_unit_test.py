import json
import os
from typing import Any, Generator

import pytest

from helpers.icat_utils import ICATClient


class GenericPACERUnitTest:
    fixtures_dict: dict = {}
    fixtures: list
    entities_teardown: list

    @pytest.fixture(scope="class", autouse=True)
    def load_fixtures(self) -> None:
        self.__load_fixtures()

    def __load_fixtures(self) -> None:
        if hasattr(self, 'fixtures') and isinstance(self.fixtures, list):
            for fixture_file in self.fixtures:
                name, _ = fixture_file.split(".")

                fixture_path: str = os.path.join("tests", 'fixtures', 'json', fixture_file)
                with open(fixture_path, "r") as f:
                    self.fixtures_dict[name] = json.load(f)

    @pytest.fixture(scope="class", autouse=True)
    def class_cleanup(self, icat_client: ICATClient, unittest_user_prefix: str) -> Generator[None, Any, None]:
        yield
        if hasattr(self, 'entities_teardown') and isinstance(self.entities_teardown, list):
            for entity in self.entities_teardown:
                results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                                   flatten_single=False)
                if results is not None:
                    for i in results:
                        icat_client.delete(i)

                    results: list = icat_client.search(entity, conditions={"name__startswith": unittest_user_prefix},
                                                       flatten_single=False)
                    assert results is None
