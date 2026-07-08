import json
import os
from time import sleep
from urllib.parse import quote

from kombu import Connection

from helpers.integrations.icat.extended_client import ICATClient
from pacer import PACER
from producers.generic import GenericProducer

ICAT_SERVER_URL: str = os.getenv("ICAT_SERVER_URL", "")
ICAT_SERVER_AUTH_METHOD: str = os.getenv("ICAT_SERVER_AUTH_METHOD", "db")
ICAT_SERVER_USERNAME: str = os.getenv("ICAT_SERVER_USERNAME", "")
ICAT_SERVER_PASSWORD: str = os.getenv("ICAT_SERVER_PASSWORD", "")

INGESTION_EXCHANGE: str = os.getenv("INGESTION_EXCHANGE", "dataset-ingest-exchange")
INGESTION_ROUTING_KEY: str = os.getenv("INGESTION_ROUTING_KEY", "dataset.ingest")

PARAMETER_TYPE_IGNORE_LIST: list[str] = ["output_datasetIds", "output_datasetNames", "output_datasets",
                                         "input_datasetIds", "ResourcesGallery"]

RMQ_HOST: str = os.getenv("RMQ_HOST", "localhost")
RMQ_PORT: int = int(os.getenv("RMQ_PORT", 5672))
RMQ_USERNAME: str = quote(os.getenv("RMQ_USERNAME", "guest"))
RMQ_PASSWORD: str = quote(os.getenv("RMQ_PASSWORD", ""))
RMQ_VHOST: str = quote(os.getenv("RMQ_VHOST", "/"))
RMQ_PROTOCOL: str = os.getenv("RMQ_PROTOCOL", "amqp")

if __name__ == "__main__":
    client: ICATClient = ICATClient(url=ICAT_SERVER_URL, auth_plugin=ICAT_SERVER_AUTH_METHOD,
                                    username=ICAT_SERVER_USERNAME, password=ICAT_SERVER_PASSWORD)
    investigation_name: str = input("Investigation name: ")
    investigations = client.search("Investigation", conditions={"name__eq": investigation_name}, flatten_single=False)

    if len(investigations) > 1:
        print("Multiple investigations found, select by visit ID:")
        for index, investigation in enumerate(investigations):
            print(f"[{index}] {investigation.name} - {investigation.visitId}")
        selection: int = int(input("Select row: "))
        if selection >= len(investigations):
            print(f"Invalid selection, must be between 0 and {len(investigations) - 1}")
            exit(1)
        investigation = investigation[selection]
    else:
        investigation = investigations[0]

    msg_common: dict = {
        "investigation": investigation.name,
        "instrument": investigation.investigationInstruments[0].instrument.name
    }

    broker_url: str = PACER._construct_broker_url(RMQ_PROTOCOL, RMQ_HOST, RMQ_PORT, RMQ_USERNAME, RMQ_PASSWORD, RMQ_VHOST)
    broker_conn: Connection = Connection(broker_url)

    indices = []
    left, right = 0, len(investigation.datasets) - 1

    while left <= right:
        indices.append(left)
        if left != right:
            indices.append(right)
        left += 1
        right -= 1

    for index in indices:
        dataset = investigation.datasets[index]
        msg: dict = {**msg_common,
                     "name": str(dataset.name),
                     "location": str(dataset.location),
                     "start_date": dataset.startDate.isoformat(timespec='milliseconds'),
                     "end_date": dataset.endDate.isoformat(timespec='milliseconds'),
                     "sample": {
                         "name": str(dataset.sample.name)},
                     "datafiles": [{"location": str(i.location)} for i in dataset.datafiles],
                     "parameters": [
                         {"name": str(i.type.name), "value": str(i.stringValue)} for i in dataset.parameters if
                          (i.type.name not in PARAMETER_TYPE_IGNORE_LIST and not i.type.name.startswith("__"))
                     ]
                     }

        GenericProducer.send_message(conn=broker_conn, exchange_name=INGESTION_EXCHANGE,
                                     routing_key=INGESTION_ROUTING_KEY,
                                     ctx=json.dumps(msg))
        print(f"Sent message to broker dataset: {dataset.id}")
        client.auto_refresh_session()
        sleep(50)
