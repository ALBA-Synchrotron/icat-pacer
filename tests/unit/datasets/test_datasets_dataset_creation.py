import re

import pytest

from exceptions.instrument import InstrumentNotFound
from exceptions.investigation import InvestigationNotFound, InvestigationInstrumentMismatch, MultipleInvestigationsFound
from exceptions.sample import SampleTypeNotFound
from helpers.contexts.dataset import create_dataset_context


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestDatasetsConsumer:

    @pytest.mark.parametrize("dataset_msg", [
        "xml_dataset_non_existent_instrument",
        "json_dataset_non_existent_instrument"
    ], indirect=True)
    def test_create_dataset_non_existent_instrument(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InstrumentNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_dataset_non_existent_investigation",
        "json_dataset_non_existent_investigation"
    ], indirect=True)
    def test_create_dataset_non_existent_investigation(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InvestigationNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset_investigation_instrument_mismatch",
        "json_raw_dataset_investigation_instrument_mismatch"
    ], indirect=True)
    def test_create_dataset_investigation_instrument_mismatch(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(InvestigationInstrumentMismatch):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset_invalid_sample_type",
        "json_raw_dataset_invalid_sample_type"
    ], indirect=True)
    def test_create_dataset_invalid_sample_type(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(SampleTypeNotFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
        "xml_raw_dataset_investigation_instrument_mismatch_investigation_id",
        "json_raw_dataset_investigation_instrument_mismatch_investigation_id"
    ], indirect=True)
    def test_create_dataset(self, dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        new_dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert new_dataset.name == dataset_ctx.name
        assert new_dataset.location == dataset_ctx.location
        assert new_dataset.investigation.name == dataset_ctx.investigation
        assert is_duplicated is False

        new_dataset_versions_name_pattern = fr"^{dataset_ctx.name} \[\d{{2}}/\d{{2}}/\d{{4}} \d{{2}}:\d{{2}}:\d{{2}}\]$"

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        new_dataset_bis = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert re.match(new_dataset_versions_name_pattern, new_dataset_bis.name)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset_investigation_overlapping_sessions",
        "json_raw_dataset_investigation_overlapping_sessions"
    ], indirect=True)
    def test_create_dataset_multiple_investigation_collision(self, dataset_tasks, dataset_msg, icat_client):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(MultipleInvestigationsFound):
            _, _, _ = dataset_tasks.create_base_dataset_icat(icat_client=icat_client, dataset_ctx=dataset_ctx)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_proc_dataset",
        "json_proc_dataset"
    ], indirect=True)
    def test_ingest_duplicate_proc_dataset_same_sample(self, dataset_tasks, dataset_msg, icat_client):
        dataset_ctx = create_dataset_context(dataset_msg)

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        dupl_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        assert is_duplicated is True
        assert dupl_dataset_id == new_dataset_id

    @pytest.mark.parametrize("dataset_msg", [
        "xml_proc_dataset",
        "json_proc_dataset"
    ], indirect=True)
    def test_ingest_duplicate_proc_dataset_different_sample(self, dataset_tasks, dataset_msg, icat_client):
        dataset_ctx = create_dataset_context(dataset_msg)

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        dataset_ctx.sample.name = "different_sample"

        dupl_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        assert is_duplicated is False
        assert dupl_dataset_id != new_dataset_id