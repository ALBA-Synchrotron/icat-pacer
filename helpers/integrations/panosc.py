import json
import logging
import time

import requests
from requests import Response

from exceptions.integrations import PaNOSCClientError

MAX_RECOMPUTATION_TRIGGER_ATTEMPTS: int = 10
RECOMPUTATION_TRIGGER_WAIT_TIME: int = 15


class PaNOSCClient:
    url: str
    username: str
    password: str
    search_api_url: str
    logger: logging.Logger

    def __init__(self, url: str, username: str, password: str, search_api_url: str, logger: logging.Logger) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.search_api_url = search_api_url
        self.logger = logger

    def __generic_pss_call(self, url: str, method: str, data: dict = None) -> Response:
        basic_auth: tuple = (self.username, self.password) if self.username and self.password else ()
        resp: Response = requests.request(method=method, url=url,
                                          **({"data": json.dumps(data)} if data else {}),
                                          **({"auth": basic_auth} if self.username and self.password else {}))
        return resp

    def item_exists(self, pss_id: str) -> bool:
        self.logger.debug(f"Checking if investigation {pss_id} item exists in PSS database")
        url: str = f"{self.url}/items/{pss_id}"
        resp: Response = self.__generic_pss_call(url=url, method="GET")

        return resp.status_code == 200

    @classmethod
    def __construct_item_payload(cls, pss_id: str, investigation_info: dict) -> dict:
        ret: dict = {
            "id": pss_id,
            "group": "documents",
            "fields": investigation_info
        }
        return ret

    def __check_weight_recomputation_in_progress(self) -> bool:
        url: str = f"{self.url}/compute"
        resp: Response = self.__generic_pss_call(url=url, method="GET")

        if resp.status_code != 200:
            error_msg: str = f"Error checking if recomputation of weights is in progress"
            self.logger.error(error_msg)
            raise PaNOSCClientError(error_msg)

        resp_json: dict = resp.json()
        return resp_json["inProgress"] == True

    def recompute_weights(self) -> None:
        self.logger.info("Recomputing all PSS weights")
        iterations: int = 0
        while iterations < MAX_RECOMPUTATION_TRIGGER_ATTEMPTS:
            if self.__check_weight_recomputation_in_progress():
                iterations -= -1
                self.logger.info("Recomputation of weights is already in progress, waiting to retrigger")
                time.sleep(RECOMPUTATION_TRIGGER_WAIT_TIME)
            else:
                break

        if iterations < MAX_RECOMPUTATION_TRIGGER_ATTEMPTS:
            self.logger.info("Triggering weight recomputation")
            url: str = f"{self.url}/compute"
            resp: Response = self.__generic_pss_call(url=url, method="POST")

            if resp.status_code != 200:
                error_msg: str = f"Error triggering weights recomputation"
                self.logger.error(error_msg)
                raise PaNOSCClientError(error_msg)
        else:
            error_msg: str = f"Previous weight recomputation took too long (more than {RECOMPUTATION_TRIGGER_WAIT_TIME * MAX_RECOMPUTATION_TRIGGER_ATTEMPTS} seconds), recomputation aborted"
            self.logger.error(error_msg)
            raise PaNOSCClientError(error_msg)
        self.logger.info("Weights recomputation finished")

    def create_item(self, pss_id: str, investigation_info: dict) -> None:
        self.logger.info(f"Creating investigation {pss_id} item in PSS database")
        payload: dict = self.__construct_item_payload(pss_id, investigation_info)

        url: str = f"{self.url}/items/"
        resp: Response = self.__generic_pss_call(url=url, method="POST", data=payload)
        if resp.status_code != 201:
            error_msg: str = f"Error creating investigation item {pss_id} item in PSS database"
            self.logger.error(error_msg)
            raise PaNOSCClientError(error_msg)

    def update_item(self, pss_id: str, investigation_info: dict) -> None:
        self.logger.info(f"Updating investigation {pss_id} item in PSS database")
        payload: dict = self.__construct_item_payload(pss_id, investigation_info)
        url: str = f"{self.url}/items/{pss_id}"
        resp: Response = self.__generic_pss_call(url=url, method="PUT", data=payload)
        if resp.status_code != 200:
            error_msg: str = f"Error updating investigation item {pss_id} item in PSS database"
            self.logger.error(error_msg)

    def retrieve_public_investigation_info(self, investigation_name: str) -> dict:
        self.logger.debug(f"Retrieving public investigation info for {investigation_name} through search API")
        basic_auth: tuple = (self.username, self.password) if self.username and self.password else ()
        params: dict = {"where": json.dumps({"pid": {"eq": investigation_name}})}

        resp: Response = requests.get(url=f"{self.search_api_url}/Documents", params=params,
                                      **({"auth": basic_auth} if self.username and self.password else {}))

        if resp.status_code != 200:
            error_msg: str = f"Error retrieving public investigation info through search-api for inv={investigation_name}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        resp_json: dict = resp.json()
        if type(resp_json) != list or len(resp_json) == 0:
            error_msg: str = f"No public investigation info found in search api for {investigation_name}"
            self.logger.error(error_msg)
            raise PaNOSCClientError(error_msg)

        if len(resp_json) > 1:
            error_msg: str = f"Multiple investigations returned in search-api for filter {params}"
            self.logger.error(error_msg)
            raise PaNOSCClientError(error_msg)

        return resp_json[0]


def get_panosc_client(config: dict, logger: logging.Logger) -> PaNOSCClient | None:
    panosc_config: dict = config.get("integrations", {}).get("panosc", {})
    if not panosc_config or not panosc_config.get("enabled"):
        return None
    return PaNOSCClient(
        url=panosc_config.get("apiUrl", ""),
        username=panosc_config.get("username", ""),
        password=panosc_config.get("password", ""),
        search_api_url=panosc_config.get("searchApiUrl", ""),
        logger=logger,
    )
