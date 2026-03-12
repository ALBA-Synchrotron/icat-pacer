import datetime
import logging
import os
import tempfile
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
ICAT_TESTBOX_DELETE_AFTER_TESTS_RUN: bool = bool(os.getenv("ICAT_TESTBOX_DELETE_AFTER_TESTS_RUN", False))

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
            testbox_identifier = None
            try:
                with open(os.path.join(tempfile.gettempdir(), "testbox_identifier"), "r") as f:
                    previous_testbox = f.read()
            except FileNotFoundError:
                previous_testbox = None
                logger.info("Testbox identifier file not found. Provisioning new one")

            if previous_testbox:
                testbox_identifier, icat_server_url = previous_testbox.split(";")
                resp = requests.post(
                    f"{ICAT_TESTBOX_SERVER_PROTOCOL}://{ICAT_TESTBOX_SERVER_HOST}:{ICAT_TESTBOX_SERVER_PORT}/testbox/{testbox_identifier}")
                if resp.status_code != 200:
                    testbox_identifier = None

            if not testbox_identifier:

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

                with open(os.path.join(tempfile.gettempdir(), "testbox_identifier"), "w") as f:
                    f.write(f"{testbox_identifier};{icat_server_url}")

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
            logger.info(f"ICAT client failed connection to testbox, retrying in 1 seconds: {e}")
            time.sleep(1)

    client: ICATClient = ICATClient(url=icat_server_url, username=icat_auth_username,
                                    password=icat_auth_password,
                                    auth_plugin=icat_auth_plugin, ids=False)

    yield client

    match PACER_TEST_BACKEND:
        case "testbox":
            if ICAT_TESTBOX_DELETE_AFTER_TESTS_RUN:
                resp = requests.delete(
                    f"http://{ICAT_TESTBOX_SERVER_HOST}:{ICAT_TESTBOX_SERVER_PORT}/testbox/{testbox_identifier}")
                if resp.status_code != 200:
                    raise Exception(f"Testbox server returned {resp.status_code}")
        case "server":
            pass
        case _:
            raise ValueError(f"Unknown PACER_TEST_BACKEND: {PACER_TEST_BACKEND}")


@pytest.fixture(scope="session")
def test_logger():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@pytest.fixture(scope="session")
def icat_facility(icat_client):
    facility = icat_client.search("Facility", flatten_single=False)[0]
    return facility


@pytest.fixture(scope="session")
def icat_unittest_investigation_type(icat_client, icat_facility):
    investigation_type = icat_client.new("InvestigationType", name="unittest", facility=icat_facility)
    investigation_type.create()
    return investigation_type


@pytest.fixture(scope="session")
def dataset_type_raw(icat_client, icat_facility):
    return icat_client.search("DatasetType", conditions={"name__eq": "acquisition"}, flatten_single=True)


@pytest.fixture(scope="session")
def random_user(icat_client, icat_facility):
    manolo = icat_client.new("User", name="Manolín")
    manolo.create()
    return manolo


@pytest.fixture(scope="session")
def random_instrument(icat_client, icat_facility):
    instrument = icat_client.new("Instrument", name="bl1984", facility=icat_facility)
    instrument.create()
    return instrument


@pytest.fixture(scope="session")
def random_instrument_2(icat_client, icat_facility):
    instrument = icat_client.new("Instrument", name="bl1986", facility=icat_facility)
    instrument.create()
    return instrument


@pytest.fixture(scope="session")
def test_investigation(icat_client, icat_facility, random_instrument, icat_unittest_investigation_type):
    investigation = icat_client.new("Investigation", name="2026090911", facility=icat_facility,
                                    visitId="2026090911-visitId", title="unittest",
                                    type=icat_unittest_investigation_type)
    investigation.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=investigation, instrument=random_instrument)
    inv_instr.create()
    return investigation


@pytest.fixture(scope="session")
def test_investigation_overlapping_1(icat_client, icat_facility, random_instrument, icat_unittest_investigation_type):
    investigation = icat_client.new("Investigation", name="2026090922", facility=icat_facility,
                                    visitId="2026090922-visitId-1", title="unittest",
                                    startDate=datetime.datetime(day=23, month=9, year=2025, hour=7, minute=0, second=0,
                                                                microsecond=0, tzinfo=datetime.timezone.utc),
                                    endDate=datetime.datetime(day=23, month=9, year=2025, hour=11, minute=0, second=0,
                                                              microsecond=0, tzinfo=datetime.timezone.utc),
                                    type=icat_unittest_investigation_type)
    investigation.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=investigation, instrument=random_instrument)
    inv_instr.create()
    return investigation


@pytest.fixture(scope="session")
def test_investigation_overlapping_2(icat_client, icat_facility, random_instrument, icat_unittest_investigation_type):
    investigation = icat_client.new("Investigation", name="2026090922", facility=icat_facility,
                                    visitId="2026090922-visitId-2", title="unittest",
                                    startDate=datetime.datetime(day=23, month=9, year=2025, hour=10, minute=0, second=0,
                                                                microsecond=0, tzinfo=datetime.timezone.utc),
                                    endDate=datetime.datetime(day=23, month=9, year=2025, hour=23, minute=0, second=0,
                                                              microsecond=0, tzinfo=datetime.timezone.utc),
                                    type=icat_unittest_investigation_type)
    investigation.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=investigation, instrument=random_instrument)
    inv_instr.create()
    return investigation


@pytest.fixture(scope="session")
def raw_dataset(icat_client, test_investigation, dataset_type_raw):
    dataset = icat_client.new("Dataset", name="test_dataset", type=dataset_type_raw, investigation=test_investigation)
    dataset.create()
    return dataset


@pytest.fixture(scope="session")
def test_parameter_types(icat_client, icat_facility):
    params = []
    for i in range(5):
        parameter_type = icat_client.new("ParameterType", name=f"parameter_type_{i}", facility=icat_facility, units="NA", valueType="STRING")
        parameter_type.create()
        params.append(parameter_type)
    return params
