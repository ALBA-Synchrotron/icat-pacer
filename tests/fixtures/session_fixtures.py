import os
import random
import string
from typing import Generator, Any
from unittest.mock import MagicMock, patch

import pytest

from helpers.icat_utils import ICATClient

ICAT_AUTH_PLUGIN: str = os.getenv("ICAT_AUTH_PLUGIN", "db")
ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_AUTH_USERNAME: str = os.getenv("ICAT_AUTH_USERNAME", "")
ICAT_AUTH_PASSWORD: str = os.getenv("ICAT_AUTH_PASSWORD", "")


@pytest.fixture(scope="session")
def unittest_prefix(request) -> str:
    characters: str = string.ascii_letters + string.digits
    test_cls = getattr(request.node, "cls", None)
    if getattr(test_cls, "digit_only_prefix", False):
        characters = string.digits
    return "".join(random.choices(characters, k=5))


@pytest.fixture(scope="session")
def icat_client(unittest_prefix) -> Generator[ICATClient, Any, None]:
    client: ICATClient = ICATClient(url=ICAT_SERVER_URL, username=ICAT_AUTH_USERNAME, password=ICAT_AUTH_PASSWORD,
                                    auth_plugin=ICAT_AUTH_PLUGIN)
    yield client
    client.logout()


@pytest.fixture(scope="session")
def datacite_client_mock() -> Generator[MagicMock, Any, None]:
    with patch("helpers.datacite.DataciteClient") as DataciteClientMock:
        client_mock = DataciteClientMock.return_value
        client_mock.create_doi.return_value = None
        client_mock.__check_weight_recomputation_in_progress.return_value = False

        yield client_mock


@pytest.fixture(scope="session")
def panosc_client_mock() -> Generator[MagicMock, Any, None]:
    with patch("helpers.panosc.PaNOSCClient") as PaNOSCClientMock:
        client_mock = PaNOSCClientMock.return_value
        client_mock.item_exists.return_value = False

        yield client_mock


@pytest.fixture(scope="session")
def mock_psycopg_pool() -> Generator[MagicMock, Any, None]:
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
