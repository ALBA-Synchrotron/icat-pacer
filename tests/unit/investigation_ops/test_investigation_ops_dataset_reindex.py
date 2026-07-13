class TestInvestigationOpsDatasetReindex:

    def test_investigation_reindex_list(self, icat_client, investigation_ops_tasks,
                                        ops_valid_investigation_with_doi):
        dataset_reindex_list = investigation_ops_tasks.fetch_investigation_datasets_reindex(icat_client,
                                                                                            ops_valid_investigation_with_doi)

        datasets_count = icat_client.search("Dataset", conditions={
            "investigation.name__eq": ops_valid_investigation_with_doi.name,
            "investigation.visitId__eq": ops_valid_investigation_with_doi.visit_id,
        }, aggregate="COUNT")

        assert len(dataset_reindex_list) == datasets_count
