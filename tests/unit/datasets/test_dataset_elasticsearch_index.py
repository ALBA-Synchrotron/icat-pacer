from helpers.models.dataset import DatasetIndexingContext
from helpers.utils.dataset import get_dataset_parameter, set_dataset_parameter


class TestDatasetIndexerConsumer:

    def test_create_dataset_document(self, icat_client, datasets_indexing_tasks, internal_statistics_tasks,
                                     generate_raw_proc_datasets):
        _, proc_dataset = generate_raw_proc_datasets(2, 1, 4)

        test_params: list = [("test_parameter_1", "lel"), ("cola_name", "value1 value2 value3"),
                             ("cola_value", "10 20 30")]

        for name, value in test_params:
            param = get_dataset_parameter(icat_client, name, entity=proc_dataset)
            _ = set_dataset_parameter(param, value)

        internal_statistics_tasks.update_dataset_statistics(icat_client, proc_dataset.id)

        doc: dict = datasets_indexing_tasks.create_dataset_document(icat_client, proc_dataset.id)
        mandatory_keys: list = ["id", "name", "startDate", "endDate", "location", "type", "sampleName", "sampleId",
                                "instrumentName", "parametersCount", "investigationId", "investigationName",
                                "investigationSummary", "investigationTitle", "investigationVisitId", "releaseDate",
                                "investigationDOI", "instrumentId", "escompactsearch", "estype"]
        assert all(key in doc for key in
                   mandatory_keys), f"Missing mandatory keys in document. Expected: {mandatory_keys}, Got: {list(doc.keys())}"

    def test_index_dataset_document(self, icat_client, mock_elasticsearch_client, datasets_indexing_tasks,
                                    internal_statistics_tasks, generate_raw_proc_datasets, monkeypatch):
        _, proc_dataset = generate_raw_proc_datasets(2, 1, 4)

        indexing_ctx: DatasetIndexingContext = DatasetIndexingContext.model_validate({
            "dataset_id": proc_dataset.id,
            "index_name": "test_index"
        })

        calls = []

        def fake_bulk(client, actions, *args, **kwargs):
            calls.append((client, actions))
            return 1, []

        monkeypatch.setattr("tasks.datasets_indexing.bulk", fake_bulk)

        datasets_indexing_tasks.index_dataset_elasticsearch(icat_client, mock_elasticsearch_client, indexing_ctx)

        assert len(calls) == 1
        assert type(calls[0][1][0]) == dict
