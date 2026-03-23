import base64
import logging
from pathlib import Path
from urllib.parse import urlencode

import requests
from requests import Response

from exceptions.integrations import ICATPlusClientError
from helpers.dataclasses.dataset import DatasetContext


class ICATPlusClient:
    url: str
    api_key: str
    logger: logging.Logger

    def __init__(self, url: str, api_key: str, logger: logging.Logger):
        self.url = url
        self.api_key = api_key
        self.logger = logger

    def upload_gallery_files(self, file_paths: list[str], dataset_ctx: DatasetContext,
                             direct_link: bool = True) -> str | None:
        base_url: str = f"{self.url}/dataacquisition/{self.api_key}/base64"

        params: dict = {
            "investigationName": dataset_ctx.investigation,
            "instrumentName": dataset_ctx.instrument,
            **({"returnDirectLink": "true"} if direct_link else {})
        }

        icat_plus_url: str = f"{base_url}?{urlencode(params)}"
        resource_ids: str = ""

        for file_path in file_paths:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not Path(file_path).is_file():
                raise ICATPlusClientError(f"Not a file: {file_path}")

            with open(file_path, "rb") as f:
                file_bytes = f.read()
                data: dict = {
                    "investigationId": dataset_ctx.investigation_id,
                    "base64": base64.b64encode(file_bytes).decode("utf-8")
                }

                self.logger.info("Uploading gallery file to ICAT Plus...")
                response: Response = requests.post(icat_plus_url, json=data)
                if not response.status_code == 200:
                    raise ICATPlusClientError(
                        f"ICAT Plus upload gallery files failed: {response.status_code} - {response.text}")

                self.logger.info("200 - Gallery file uploaded successfully.")

                response_data = response.json()
                resource_id = response_data.get('_id')
                resource_ids += f"{resource_id} "
        return resource_ids.rstrip()


def get_icat_plus_client(config: dict, logger: logging.Logger) -> ICATPlusClient | None:
    icat_plus_config: dict = config.get("integrations", {}).get("icatPlus", {})

    if not icat_plus_config or not icat_plus_config.get("enabled"):
        return None

    icat_plus_server_config = icat_plus_config.get("server", {})

    return ICATPlusClient(
        url=icat_plus_server_config.get("url", ""),
        api_key=icat_plus_server_config.get("apiKey", ""),
        logger=logger,
    )
