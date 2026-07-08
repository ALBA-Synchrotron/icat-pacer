from elasticsearch import Elasticsearch


def get_elastic_client(config: dict) -> Elasticsearch | None:
    elastic_config: dict = config.get("integrations", {}).get("elastic", {})

    if not elastic_config or not elastic_config.get("enabled"):
        return None

    return Elasticsearch(
        elastic_config.get("url", ""),
        basic_auth=(
            elastic_config.get("username", ""),
            elastic_config.get("password", ""),
        ),
    )
