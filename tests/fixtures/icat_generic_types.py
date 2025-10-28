import pytest
from icat.entity import Entity

from helpers.integrations.icat_utils import ICATClient


@pytest.fixture(scope="session")
def icat_acquisition_dataset_type(icat_client: ICATClient) -> Entity:
    dataset_type: Entity = icat_client.search("DatasetType", conditions={"name__eq": "acquisition"},
                                              flatten_single=True)
    return dataset_type


@pytest.fixture(scope="session")
def icat_facility(icat_client: ICATClient) -> Entity:
    facility: Entity = icat_client.search("Facility", flatten_single=True)
    return facility


@pytest.fixture(scope="session")
def icat_root_user(icat_client: ICATClient) -> Entity:
    root_user: Entity = icat_client.search("User", conditions={"name__eq": "root"}, flatten_single=True)
    return root_user


@pytest.fixture(scope="session")
def icat_investigation_type(icat_client: ICATClient, icat_facility: Entity) -> Entity:
    investigation_type: Entity = icat_client.search("InvestigationType", conditions={"name__eq": "TEST"},
                                                    flatten_single=True)
    return investigation_type


@pytest.fixture(scope="session")
def icat_instrument(icat_client: ICATClient, icat_facility: Entity) -> Entity:
    instrument: Entity = icat_client.search("Instrument", conditions={"name__eq": "BL00"}, flatten_single=True)
    return instrument
