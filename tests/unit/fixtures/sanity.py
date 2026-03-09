import pytest

from tests.unit.fixtures.icat import PACER_TEST_BACKEND, ICAT_TESTBOX_ICAT_SERVER_VERSION


@pytest.fixture(scope="session", autouse=True)
def tests_sanity_pre_check(icat_client):
    # Check if testing environment is correctly set up for executing the tests
    assert icat_client is not None
    assert icat_client.apiversion is not None
    if PACER_TEST_BACKEND == "testbox":
        assert icat_client.apiversion == ICAT_TESTBOX_ICAT_SERVER_VERSION