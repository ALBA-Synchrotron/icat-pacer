from unittest.mock import patch

import pytest


@pytest.fixture()
def mock_elasticsearch_client():
    with patch("elasticsearch.Elasticsearch") as MockElasticsearch:
        mock_client = MockElasticsearch.return_value

        yield mock_client