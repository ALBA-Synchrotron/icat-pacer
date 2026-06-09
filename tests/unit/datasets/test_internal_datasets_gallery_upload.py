import pytest

import globals_var
from exceptions.dataset import DatasetValidationError, DatasetNotFound
from helpers.contexts.dataset import create_dataset_context
from helpers.models.dataset import DatasetParameterContext
from helpers.static_settings import DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS
from tests.unit.fixtures.icat import mock_icat_plus_client


@pytest.fixture
def dataset_msg(request):
    return request.getfixturevalue(request.param)


class TestInternalDatasetConsumerGalleryUpload:

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_upload_gallery_missing_dataset_id(self, mock_icat_plus_client, internal_dataset_tasks, icat_client,
                                               dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetValidationError):
            internal_dataset_tasks.create_dataset_gallery(mock_icat_plus_client, icat_client, dataset_ctx, 0)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_upload_gallery_non_existent_dataset(self, mock_icat_plus_client, internal_dataset_tasks, icat_client,
                                                 dataset_msg):
        dataset_ctx = create_dataset_context(dataset_msg)
        with pytest.raises(DatasetNotFound):
            internal_dataset_tasks.create_dataset_gallery(mock_icat_plus_client, icat_client, dataset_ctx, 99999999)

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_upload_gallery_unlisted_gallery(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg,
                            mock_icat_plus_client, monkeypatch):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        ingestion_settings = {"dataset": {"galleryAcceptedUploadTypes": [".png"]}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)

        internal_dataset_tasks.create_dataset_gallery(mock_icat_plus_client, icat_client, dataset_ctx, new_dataset_id)
        files, _ = mock_icat_plus_client.method_calls[0].args
        assert mock_icat_plus_client.upload_gallery_files.called
        assert len(files) == 3

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_upload_gallery_listed_gallery(self, dataset_tasks, internal_dataset_tasks, icat_client, dataset_msg,
                                             mock_icat_plus_client, monkeypatch):
        dataset_ctx = create_dataset_context(dataset_msg)
        dataset_ctx.parameters.append(DatasetParameterContext(name=DATASET_PARAMETER_RESOURCE_GALLERY_FILE_PATHS,
                                                              value=f"{dataset_ctx.location}/gallery/image3.png"))

        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        ingestion_settings = {"dataset": {"galleryAcceptedUploadTypes": [".png"]}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)

        internal_dataset_tasks.create_dataset_parameters(icat_client, dataset_ctx, new_dataset_id, is_duplicated)
        internal_dataset_tasks.create_dataset_gallery(mock_icat_plus_client, icat_client, dataset_ctx, new_dataset_id)
        files, _ = mock_icat_plus_client.method_calls[0].args
        assert mock_icat_plus_client.upload_gallery_files.called
        assert len(files) == 1

    @pytest.mark.parametrize("dataset_msg", [
        "xml_raw_dataset",
        "json_raw_dataset",
    ], indirect=True)
    def test_upload_gallery_unaccepted_file_extensions(self, dataset_tasks, internal_dataset_tasks, icat_client,
                                                       dataset_msg,
                                                       mock_icat_plus_client, monkeypatch):
        dataset_ctx = create_dataset_context(dataset_msg)
        new_dataset_id, investigation_id, is_duplicated = dataset_tasks.create_base_dataset_icat(
            icat_client=icat_client, dataset_ctx=dataset_ctx)

        ingestion_settings = {"dataset": {"galleryAcceptedUploadTypes": [".jpg"]}}

        monkeypatch.setattr(globals_var, "ingestion_settings", ingestion_settings)

        internal_dataset_tasks.create_dataset_gallery(mock_icat_plus_client, icat_client, dataset_ctx, new_dataset_id)
        assert not mock_icat_plus_client.upload_gallery_files.called
