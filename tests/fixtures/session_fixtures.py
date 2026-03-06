import logging
import os
import time

import pytest
import requests

from helpers.integrations.icat.extended_client import ICATClient

PACER_TEST_BACKEND: str = os.getenv("PACER_TEST_BACKEND", "testbox")

ICAT_TESTBOX_SERVER_PROTOCOL: str = os.getenv("ICAT_TESTBOX_SERVER_PROTOCOL", "http")
ICAT_TESTBOX_SERVER_HOST: str = os.getenv("ICAT_TESTBOX_SERVER_HOST", "")
ICAT_TESTBOX_SERVER_PORT: int = int(os.getenv("ICAT_TESTBOX_SERVER_PORT", 5000))
ICAT_TESTBOX_AUTHN_DB_VERSION: str = os.getenv("ICAT_TESTBOX_AUTHN_DB_VERSION", "3.0.0")
ICAT_TESTBOX_ICAT_SERVER_VERSION: str = os.getenv("ICAT_TESTBOX_ICAT_SERVER_VERSION", "6.2.0")
ICAT_TESTBOX_DB_FIXTURE_LOAD: bool = bool(os.getenv("ICAT_TESTBOX_ICAT_SERVER_VERSION", True))

ICAT_AUTH_PLUGIN: str = os.getenv("ICAT_AUTH_PLUGIN", "db")
ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_AUTH_USERNAME: str = os.getenv("ICAT_AUTH_USERNAME", "")
ICAT_AUTH_PASSWORD: str = os.getenv("ICAT_AUTH_PASSWORD", "")

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def icat_client():
    icat_server_url, icat_auth_username, icat_auth_password, icat_auth_plugin = "", "", "", ""

    match PACER_TEST_BACKEND:
        case "testbox":
            body: dict = {
                "icat_version": ICAT_TESTBOX_ICAT_SERVER_VERSION,
                "authn_db_version": ICAT_TESTBOX_AUTHN_DB_VERSION,
                "init_database": ICAT_TESTBOX_DB_FIXTURE_LOAD
            }
            resp = requests.post(
                f"{ICAT_TESTBOX_SERVER_PROTOCOL}://{ICAT_TESTBOX_SERVER_HOST}:{ICAT_TESTBOX_SERVER_PORT}/testbox",
                json=body)
            if resp.status_code != 200:
                raise Exception(f"Testbox server returned {resp.status_code}")
            testbox_identifier = resp.json()["identifier"]
            testbox_port = resp.json()["host_port"]
            icat_server_url = f"http://{ICAT_TESTBOX_SERVER_HOST}:{testbox_port}/ICATService/ICAT?wsdl"

        case "server":
            icat_server_url = ICAT_SERVER_URL
        case _:
            raise ValueError(f"Unknown PACER_TEST_BACKEND: {PACER_TEST_BACKEND}")

    icat_auth_username = ICAT_AUTH_USERNAME
    icat_auth_password = ICAT_AUTH_PASSWORD
    icat_auth_plugin = ICAT_AUTH_PLUGIN

    while True:
        try:
            resp = requests.get(icat_server_url)
            if resp.status_code == 200:
                break
        except Exception as e:
            logger.info(f"ICAT client failed connection to testbox, retrying in 2 seconds: {e}")
            time.sleep(2)

    client: ICATClient = ICATClient(url=icat_server_url, username=icat_auth_username,
                                   password=icat_auth_password,
                                   auth_plugin=icat_auth_plugin, ids=False)

    yield client

    match PACER_TEST_BACKEND:
        case "testbox":
            resp = requests.delete(
                f"http://{ICAT_TESTBOX_SERVER_HOST}:{ICAT_TESTBOX_SERVER_PORT}/testbox/{testbox_identifier}")
            if resp.status_code != 200:
                raise Exception(f"Testbox server returned {resp.status_code}")
        case "server":
            pass
        case _:
            raise ValueError(f"Unknown PACER_TEST_BACKEND: {PACER_TEST_BACKEND}")
