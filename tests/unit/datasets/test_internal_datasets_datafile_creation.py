from pathlib import Path

import pytest

from exceptions.dataset import DatasetValidationError, DatasetNotFound
from helpers.contexts.dataset import create_dataset_context


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalDatasetConsumerDatafileCreation:

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_datafiles_dataset_id_not_provided(self, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetValidationError):
            internal_dataset_tasks.create_dataset_datafiles(icat_client, dataset_ctx, 0, False)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_datafiles_non_existent_dataset(self, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetNotFound):
            internal_dataset_tasks.create_dataset_datafiles(icat_client, dataset_ctx, 99827, False)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_datafiles(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        internal_dataset_tasks.create_dataset_datafiles(icat_client, dataset_ctx, new_dataset_id, is_duplicated)

        dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert len(dataset.datafiles) == len(dataset_ctx.datafiles)
        dataset_files = [i.location for i in dataset.datafiles]
        ctx_files = [i.location for i in dataset_ctx.datafiles]
        assert set(dataset_files) == set(ctx_files)
        assert all(i.fileSize > 0 for i in dataset.datafiles)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_proc_dataset",
        "json_proc_dataset",
    ], indirect=True)
    def test_create_replace_datafiles_dupl_proc_dataset(self, dataset_tasks, internal_dataset_tasks, icat_client,
                                                        dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        for _ in range(2):
            new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
                icat_client=icat_client, dataset_ctx=dataset_ctx)
        assert is_duplicated is True
        dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        old_datafile_ids = [i.id for i in dataset.datafiles]

        internal_dataset_tasks.create_dataset_datafiles(icat_client, dataset_ctx, new_dataset_id, is_duplicated)
        dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        new_datafile_ids = [i.id for i in dataset.datafiles]
        assert set(old_datafile_ids) != set(new_datafile_ids)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_create_datafiles_max_limit(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg,
                                           monkeypatch):
        enforced_test_limit = 10
        import globals_var

        ingestion_settings = {
            "dataset": {
                "automaticDatasetLocationIndex": True,
                "maxDatafilesPerDataset": enforced_test_limit
            }}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)

        dataset_ctx = create_dataset_context(dataset_msg)
        dataset_ctx.name = f"{dataset_ctx.name}-test_create_datafiles_max_limit"
        dataset_ctx.datafiles = []

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)
        internal_dataset_tasks.create_dataset_datafiles(icat_client, dataset_ctx, new_dataset_id, is_duplicated)

        dataset = icat_client.search("Dataset", conditions={"id__eq": new_dataset_id}, flatten_single=True)
        assert sum(1 for p in Path(dataset_ctx.location).iterdir() if p.is_file()) > enforced_test_limit
        assert len(dataset.datafiles) <= enforced_test_limit
