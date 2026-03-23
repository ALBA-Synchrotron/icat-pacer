import datetime
import logging
import os
import random
import tempfile
import time
from unittest.mock import patch

import pytest
import requests

from helpers.integrations.icat.extended_client import ICATClient
from helpers.static_settings import INPUT_DATASET_PARAMETER_NAME
from helpers.utils.dataset import set_dataset_parameter, get_dataset_parameter

PACER_TEST_BACKEND: str = os.getenv("PACER_TEST_BACKEND", "testbox")

ICAT_TESTBOX_SERVER_PROTOCOL: str = os.getenv("ICAT_TESTBOX_SERVER_PROTOCOL", "http")
ICAT_TESTBOX_SERVER_HOST: str = os.getenv("ICAT_TESTBOX_SERVER_HOST", "")
ICAT_TESTBOX_SERVER_PORT: int = int(os.getenv("ICAT_TESTBOX_SERVER_PORT", 5000))
ICAT_TESTBOX_AUTHN_DB_VERSION: str = os.getenv("ICAT_TESTBOX_AUTHN_DB_VERSION", "3.0.0")
ICAT_TESTBOX_ICAT_SERVER_VERSION: str = os.getenv("ICAT_TESTBOX_ICAT_SERVER_VERSION", "6.2.0")
ICAT_TESTBOX_DB_FIXTURE_LOAD: bool = bool(os.getenv("ICAT_TESTBOX_DB_FIXTURE_LOAD", True))
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
def dataset_type_processed(icat_client, icat_facility):
    return icat_client.search("DatasetType", conditions={"name__eq": "processed"}, flatten_single=True)


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


@pytest.fixture
def test_investigation(icat_client, icat_facility, random_instrument, icat_unittest_investigation_type, random_str):
    investigation = icat_client.new("Investigation", name=f"2026090911-{random_str}", facility=icat_facility,
                                    visitId=f"2026090911-visitId_{random_str}", title="unittest",
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


@pytest.fixture()
def raw_dataset(icat_client, test_investigation, dataset_type_raw, random_str):
    dataset = icat_client.new("Dataset", name=f"test_dataset_{random_str}", type=dataset_type_raw,
                              investigation=test_investigation)
    dataset.create()
    return dataset


@pytest.fixture()
def proc_dataset(icat_client, test_investigation, dataset_type_processed, random_str):
    dataset = icat_client.new("Dataset", name=f"test_dataset_{random_str}", type=dataset_type_processed,
                              investigation=test_investigation)
    dataset.create()
    return dataset


@pytest.fixture(scope="session")
def test_parameter_types(icat_client, icat_facility):
    params = []
    for i in range(5):
        parameter_type = icat_client.new("ParameterType", name=f"parameter_type_{i}", facility=icat_facility,
                                         units="NA", valueType="STRING", applicableToDataset=True)
        parameter_type.create()
        params.append(parameter_type)
    return params


@pytest.fixture()
def generate_raw_proc_datasets(icat_client, test_investigation, random_str, dataset_type_raw, dataset_type_processed):
    def create_datasets(amount_raw: int = 1, amount_proc: int = 1, datafile_amount: int = 0, investigation=None,
                        file_size: int = 1000,
                        start_date=None, end_date=None):
        raw_datasets, proc_datasets = [], []

        if not start_date:
            start_date = datetime.datetime(day=23, month=9, year=2025, hour=7, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.datetime(day=23, month=9, year=2025, hour=11, minute=0, second=0, microsecond=0)

        if not investigation:
            investigation = test_investigation

        sample = icat_client.new("Sample", name=f"sample_{random_str}", investigation=investigation)
        sample.create()

        for i in range(amount_raw):
            raw_dataset = icat_client.new("Dataset", name=f"raw_{random_str}_{i}", type=dataset_type_raw,
                                          investigation=investigation, location=f"/tmp/raw_{random_str}/{i}/",
                                          startDate=start_date, endDate=end_date,
                                          sample=sample)
            raw_dataset.create()
            raw_datasets.append(raw_dataset)

        for i in range(amount_proc):
            proc_dataset = icat_client.new("Dataset", name=f"proc_{random_str}_{i}", type=dataset_type_processed,
                                           investigation=investigation, location=f"/tmp/proc_{random_str}/{i}/",
                                           startDate=start_date, endDate=end_date,
                                           sample=sample)
            proc_dataset.create()
            proc_datasets.append(proc_dataset)

        if datafile_amount:
            for i in raw_datasets + proc_datasets:
                for j in range(datafile_amount):
                    datafile = icat_client.new("Datafile", name=f"datafile_{random_str}_{j}", dataset=i,
                                               fileSize=file_size)
                    datafile.create()

        return raw_datasets[0] if len(raw_datasets) == 1 else raw_datasets, proc_datasets[0] if len(
            proc_datasets) == 1 else proc_datasets

    return create_datasets


@pytest.fixture()
def create_raw_proc_datasets_relation(icat_client):
    def create_raw_proc_datasets_relation(origin_datasets, destination_dataset):
        if type(origin_datasets) != list:
            datasets = [origin_datasets]
        else:
            datasets = origin_datasets.copy()

        proc_input_dataset_param = get_dataset_parameter(icat_client, INPUT_DATASET_PARAMETER_NAME,
                                                         dataset_id=destination_dataset.id)
        set_dataset_parameter(proc_input_dataset_param, ",".join(i.location for i in datasets))

    return create_raw_proc_datasets_relation


@pytest.fixture()
def test_investigation_statistics(icat_client, test_parameter_types, random_str, generate_raw_proc_datasets,
                                  icat_facility, icat_unittest_investigation_type):
    amount_raw = 3
    amount_proc = 3
    file_size = 26
    datafile_amount = 3
    start_date = datetime.datetime(day=23, month=9, year=2025, hour=7, minute=0, second=0, microsecond=0)
    end_date = datetime.datetime(day=23, month=9, year=2025, hour=11, minute=0, second=0, microsecond=0)

    expected_statistics = {}

    inv = icat_client.new("Investigation", name=f"inv-statistics-{random_str}", title="unittest",
                          visitId=f"inv-statistics-{random_str}",
                          facility=icat_facility, type=icat_unittest_investigation_type)
    inv.create()

    raw_datasets, proc_datasets = generate_raw_proc_datasets(amount_raw=amount_raw, amount_proc=amount_proc,
                                                             datafile_amount=datafile_amount,
                                                             investigation=inv, file_size=file_size,
                                                             start_date=start_date,
                                                             end_date=end_date)

    expected_statistics["total_datasets"] = str(amount_raw + amount_proc)
    expected_statistics["total_raw_datasets"] = str(amount_raw)
    expected_statistics["total_proc_datasets"] = str(amount_proc)
    expected_statistics["total_samples"] = str(1)
    expected_statistics["total_volume"] = str(datafile_amount * file_size * (amount_raw + amount_proc))
    expected_statistics["total_raw_volume"] = str(datafile_amount * file_size * amount_raw)
    expected_statistics["total_proc_volume"] = str(datafile_amount * file_size * amount_proc)
    expected_statistics["total_elapsed_time"] = str(
        int((end_date - start_date).total_seconds()) * (amount_raw + amount_proc))
    expected_statistics["total_file_count"] = str(datafile_amount * (amount_raw + amount_proc))
    expected_statistics["total_raw_file_count"] = str(datafile_amount * amount_raw)
    expected_statistics["total_proc_file_count"] = str(datafile_amount * amount_proc)

    expected_statistics["sample_dataset_count"] = str(amount_raw + amount_proc)
    expected_statistics["sample_raw_dataset_count"] = str(amount_raw)
    expected_statistics["sample_proc_dataset_count"] = str(amount_proc)
    expected_statistics["sample_total_file_count"] = str(datafile_amount * (amount_raw + amount_proc))
    expected_statistics["sample_total_raw_file_count"] = str(datafile_amount * amount_raw)
    expected_statistics["sample_total_proc_file_count"] = str(datafile_amount * amount_proc)
    expected_statistics["sample_total_volume"] = str(datafile_amount * file_size * (amount_raw + amount_proc))
    expected_statistics["sample_total_raw_volume"] = str(datafile_amount * file_size * amount_raw)
    expected_statistics["sample_total_proc_volume"] = str(datafile_amount * file_size * amount_proc)

    return raw_datasets, proc_datasets, expected_statistics


@pytest.fixture()
def mock_icat_plus_client():
    with patch("helpers.integrations.icat.icat_plus.ICATPlusClient") as MockICATPlusClient:
        mock_client = MockICATPlusClient.return_value

        mock_client.upload_gallery_files.return_value = "0x18A"

        yield mock_client
