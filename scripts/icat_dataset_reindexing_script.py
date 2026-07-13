import os
from time import sleep
from urllib.parse import quote

from kombu import Connection

from helpers.integrations.icat.extended_client import ICATClient
from helpers.models.dataset import DatasetIndexingContext
from pacer import PACER
from producers.generic import GenericProducer

ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_SERVER_AUTH_METHOD: str = os.getenv("ICAT_SERVER_AUTH_METHOD", "db")
ICAT_SERVER_USERNAME: str = os.getenv("ICAT_SERVER_USERNAME", "")
ICAT_SERVER_PASSWORD: str = os.getenv("ICAT_SERVER_PASSWORD", "")

INGESTION_EXCHANGE: str = os.getenv("INGESTION_EXCHANGE", "dataset-internal-ingest-exchange")
INGESTION_ROUTING_KEY: str = os.getenv("INGESTION_ROUTING_KEY", "dataset.indexing")

INDEX_NAME: str = os.getenv("INDEX_NAME", "all_datasets_prod")
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 2000))

RMQ_HOST: str = os.getenv("RMQ_HOST", "localhost")
RMQ_PORT: int = int(os.getenv("RMQ_PORT", 5672))
RMQ_USERNAME: str = quote(os.getenv("RMQ_USERNAME", "guest"))
RMQ_PASSWORD: str = quote(os.getenv("RMQ_PASSWORD", ""))
RMQ_VHOST: str = quote(os.getenv("RMQ_VHOST", "/"))
RMQ_PROTOCOL: str = os.getenv("RMQ_PROTOCOL", "amqp")

if __name__ == "__main__":
    client: ICATClient = ICATClient(url=ICAT_SERVER_URL, auth_plugin=ICAT_SERVER_AUTH_METHOD,
                                    username=ICAT_SERVER_USERNAME, password=ICAT_SERVER_PASSWORD)


    broker_url: str = PACER._construct_broker_url(RMQ_PROTOCOL, RMQ_HOST, RMQ_PORT, RMQ_USERNAME, RMQ_PASSWORD, RMQ_VHOST)
    broker_conn: Connection = Connection(broker_url)

    max_dataset_id = client.search("Dataset", flatten_single=True, order=[("id", "DESC")], limit=(0, 1)).id

    for i in range(max_dataset_id, 0, -BATCH_SIZE):
        end = i
        start = max(1, i - BATCH_SIZE + 1)
        print(f"Processing datasets from {start} to {end}")
        datasets = client.search("Dataset", conditions={"id__gte": start, "id__lte": end}, limit=(0, BATCH_SIZE),
                                 order=[("id", "DESC")], flatten_single=False)

        for dataset in datasets:
            GenericProducer.send_message(conn=broker_conn, exchange_name=INGESTION_EXCHANGE,
                                         routing_key=INGESTION_ROUTING_KEY,
                                         ctx=DatasetIndexingContext.model_validate({
                                             "dataset_id": dataset.id,
                                             "index_name": INDEX_NAME
                                         }).model_dump_json())

            print(f"Sent message to broker dataset: {dataset.id}")
        client.auto_refresh_session()
        sleep(40)

