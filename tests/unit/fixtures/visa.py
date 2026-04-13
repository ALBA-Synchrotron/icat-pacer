from typing import Generator, Any
from unittest.mock import MagicMock, patch

import pytest


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
