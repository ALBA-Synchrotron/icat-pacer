from elasticsearch import Elasticsearch


class ElasticClient(Elasticsearch):

    def __init__(self, host, port, scheme, username, password):
        super().__init__([{'host': host, 'port': port, 'scheme': scheme}],
                         basic_auth=(username, password))


def get_elastic_client(config: dict) -> ElasticClient | None:
    elastic_config: dict = config.get("integrations", {}).get("elastic", {})

    if not elastic_config or not elastic_config.get("enabled"):
        return None

    return ElasticClient(
        host=elastic_config.get("host", ""),
        port=elastic_config.get("port", ""),
        scheme=elastic_config.get("scheme", ""),
        username=elastic_config.get("username", ""),
        password=elastic_config.get("password", "")
    )
