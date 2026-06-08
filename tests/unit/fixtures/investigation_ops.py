import datetime
from unittest.mock import patch

import pytest

from helpers.contexts.investigation_ops import create_investigation_ops_context

ops = ["create-panosc-item", "mint-proposal"]


@pytest.fixture(scope="session")
def ops_investigation_with_doi(icat_client, icat_facility, icat_unittest_investigation_type):
    name = "inv_with_doi"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        doi="10.1234/test.123456789", facility=icat_facility,
                        type=icat_unittest_investigation_type, visitId=f"{name}-visitId", )
    i.create()
    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_investigation_no_datasets(icat_client, icat_facility, icat_unittest_investigation_type):
    name = "inv_no_datasets"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type, visitId=f"{name}-visitId")
    i.create()
    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_investigation_missing_end_date(icat_client, icat_facility, icat_unittest_investigation_type):
    name = "inv_missing_end_date"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type, visitId=f"{name}-visitId")
    i.create()
    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_investigation_missing_investigation_users(icat_client, icat_facility, icat_unittest_investigation_type,
                                                  dataset_type_raw):
    name = "inv_missing_investigation_users"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type, visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_investigation_missing_instrument(icat_client, icat_facility, icat_unittest_investigation_type, dataset_type_raw,
                                         random_user):
    name = "inv_missing_instrument"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type, visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_investigation_future_end_date(icat_client, icat_facility, icat_unittest_investigation_type, dataset_type_raw,
                                      random_user, random_instrument):
    name = "inv_future_end_date"
    end_date = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=end_date,
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type,
                        visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=i, instrument=random_instrument)
    inv_instr.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_non_existent_investigation():
    return create_investigation_ops_context({"name": "non_existent_investigation", "ops": ops, "visit_id": "asd"})


@pytest.fixture(scope="session")
def ops_valid_investigation(icat_client, icat_facility, icat_unittest_investigation_type, dataset_type_raw,
                            random_user, random_instrument):
    name = "inv_valid_ops"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type,
                        visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=i, instrument=random_instrument)
    inv_instr.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})

@pytest.fixture(scope="session")
def ops_industrial_investigation(icat_client, icat_facility, icat_industrial_inv_type, dataset_type_raw,
                            random_user, random_instrument):
    name = "inv_industrial_ops"
    i = icat_client.new("Investigation", name=name, title="Industrial inv",
                        summary="Industrial inv",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_industrial_inv_type,
                        visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=i, instrument=random_instrument)
    inv_instr.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_valid_investigation_with_doi(icat_client, icat_facility, icat_unittest_investigation_type, dataset_type_raw,
                                     random_user, random_instrument):
    name = "inv_valid_ops_with_doi"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type,
                        visitId=f"{name}-visitId", doi="10.1234/test.123456789")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=i, instrument=random_instrument)
    inv_instr.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def ops_valid_investigation_no_doi(icat_client, icat_facility, icat_unittest_investigation_type, dataset_type_raw,
                                   random_user, random_instrument):
    name = "inv_valid_ops_no_doi"
    i = icat_client.new("Investigation", name=name, title="Investigation without DOI",
                        summary="Investigation without DOI",
                        startDate=datetime.datetime.strptime("2018-10-10 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        endDate=datetime.datetime.strptime("2018-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        releaseDate=datetime.datetime.strptime("2021-10-24 12:33:43", "%Y-%m-%d %H:%M:%S"),
                        facility=icat_facility,
                        type=icat_unittest_investigation_type,
                        visitId=f"{name}-visitId")
    i.create()

    dataset = icat_client.new("Dataset", investigation=i, name="test_dataset", type=dataset_type_raw)
    dataset.create()
    inv_user = icat_client.new("InvestigationUser", investigation=i, user=random_user, role="Principal investigator")
    inv_user.create()
    inv_instr = icat_client.new("InvestigationInstrument", investigation=i, instrument=random_instrument)
    inv_instr.create()

    return create_investigation_ops_context({"name": i.name, "ops": ops, "visit_id": i.visitId})


@pytest.fixture(scope="session")
def datacite_client_mock():
    with patch("helpers.integrations.datacite.DataciteClient") as DataciteClientMock:
        client_mock = DataciteClientMock.return_value
        client_mock.create_doi.return_value = None
        client_mock.__check_weight_recomputation_in_progress.return_value = False

        yield client_mock


@pytest.fixture(scope="session")
def panosc_client_mock():
    with patch("helpers.integrations.panosc.PaNOSCClient") as PaNOSCClientMock:
        client_mock = PaNOSCClientMock.return_value
        client_mock.item_exists.return_value = False

        yield client_mock
