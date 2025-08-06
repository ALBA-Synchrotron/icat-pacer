import datetime
import logging

import pytest
from icat.entity import Entity

from helpers.dataclasses import InvestigationOperationsContext
from helpers.icat_utils import ICATClient
from tasks.investigation_ops import InvestigationOpsTasks

logger: logging.Logger = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def investigation_ops_tasks() -> InvestigationOpsTasks:
    return InvestigationOpsTasks(logger)


@pytest.fixture(scope="class")
def non_existent_investigation() -> InvestigationOperationsContext:
    return InvestigationOperationsContext(name="non-existent-investigation", operations=["mint-proposal"])


@pytest.fixture(scope="class")
def investigation_with_doi(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                           icat_investigation_type: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-with-doi",
                                            facility=icat_facility, doi="10.1234/test-doi", title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest")
    investigation.create()
    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_with_no_datasets(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                   icat_investigation_type: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-no-data",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest")
    investigation.create()
    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_with_no_users(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-no-users",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_with_no_dates(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                icat_root_user: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-no-dates",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_with_no_instrument(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                     icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                     icat_root_user: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-noinstr",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest", startDate="2021-01-01", endDate="2021-01-31",
                                            releaseDate="2021-02-01")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_with_future_end_date(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                       icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                       icat_root_user: Entity, icat_instrument: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-good",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest", startDate="2021-01-01",
                                            endDate=(datetime.datetime.now() + datetime.timedelta(days=15)).strftime(
                                                "%Y-%m-%d"),
                                            releaseDate="2021-02-01")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()

    inv_str: Entity = icat_client.new("InvestigationInstrument", investigation=investigation,
                                      instrument=icat_instrument)
    inv_str.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(investigation)


@pytest.fixture(scope="class")
def investigation_good_for_doi(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                               icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                               icat_root_user: Entity, icat_instrument: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-future",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest", startDate="2021-01-01", endDate="2021-01-31",
                                            releaseDate="2021-02-01")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()
    inv_str: Entity = icat_client.new("InvestigationInstrument", investigation=investigation,
                                      instrument=icat_instrument)
    inv_str.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(inv_str)
    icat_client.delete(investigation)

@pytest.fixture(scope="class")
def investigation_good_for_item_creation(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                                         icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                                         icat_root_user: Entity, icat_instrument: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-future",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type, doi="10.1234/test-doi",
                                            visitId="bltest", startDate="2021-01-01", endDate="2021-01-31",
                                            releaseDate="2021-02-01")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()
    inv_str: Entity = icat_client.new("InvestigationInstrument", investigation=investigation,
                                      instrument=icat_instrument)
    inv_str.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(inv_str)
    icat_client.delete(investigation)

@pytest.fixture(scope="class")
def investigation_with_no_doi(icat_client: ICATClient, ascii_prefix, icat_facility: Entity,
                              icat_investigation_type: Entity, icat_acquisition_dataset_type: Entity,
                              icat_root_user: Entity, icat_instrument: Entity):
    investigation: Entity = icat_client.new("Investigation", name=f"{ascii_prefix}-investigation-nodoi",
                                            facility=icat_facility, title="test title",
                                            type=icat_investigation_type,
                                            visitId="bltest", startDate="2021-01-01", endDate="2021-01-31",
                                            releaseDate="2021-02-01")
    investigation.create()
    dataset: Entity = icat_client.new("Dataset", name=f"{ascii_prefix}-dataset",
                                      investigation=investigation, type=icat_acquisition_dataset_type)
    dataset.create()
    inv_user: Entity = icat_client.new("InvestigationUser", investigation=investigation, user=icat_root_user,
                                       role="Principal Investigator")
    inv_user.create()
    inv_str: Entity = icat_client.new("InvestigationInstrument", investigation=investigation,
                                      instrument=icat_instrument)
    inv_str.create()

    yield InvestigationOperationsContext(name=investigation.name, operations=["mint-proposal"])

    icat_client.delete(dataset)
    icat_client.delete(inv_user)
    icat_client.delete(inv_str)
    icat_client.delete(investigation)