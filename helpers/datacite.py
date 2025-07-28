import json
import logging
from itertools import chain

import requests
from requests import Response


class DataciteClient:
    data_catalogue_doi_base_url: str
    publisher: str
    prefix: str
    session_suffix: str
    username: str
    password: str
    api_url: str
    language: str
    rights_name: str
    rights_scheme_uri: str
    rights_uri: str
    rights_identifier_scheme: str
    rights_identifier: str
    funder_name: str
    funder_identifier: str
    funder_identifier_type: str
    logger: logging.Logger

    def __init__(self, data_catalogue_doi_base_url: str, publisher: str, prefix: str, session_suffix: str,
                 username: str, password: str, api_url: str, language: str, rights_name: str,
                 rights_scheme_uri: str, rights_uri: str, rights_identifier_scheme: str, rights_identifier: str,
                 funder_name: str, funder_identifier: str, funder_identifier_type: str, logger: logging.Logger) -> None:
        self.data_catalogue_doi_base_url = data_catalogue_doi_base_url
        self.publisher = publisher
        self.prefix = prefix
        self.session_suffix = session_suffix
        self.username = username
        self.password = password
        self.api_url = api_url
        self.language = language
        self.rights_name = rights_name
        self.rights_scheme_uri = rights_scheme_uri
        self.rights_uri = rights_uri
        self.rights_identifier_scheme = rights_identifier_scheme
        self.rights_identifier = rights_identifier
        self.funder_name = funder_name
        self.funder_identifier = funder_identifier
        self.funder_identifier_type = funder_identifier_type
        self.logger = logger

    @classmethod
    def generate_user_data_structure(cls, *args) -> list:
        users: list = list(chain.from_iterable(args))
        ret: list = []

        for inv_user in users:
            ret.append({
                "nameType": "Personal",
                "givenName": inv_user.givenName,
                "familyName": inv_user.familyName,
                "affiliation": [
                    {
                        "name": inv_user.affiliation
                    }
                ],
                **(
                    {"nameIdentifiers": [
                        {
                            "nameIdentifier": inv_user.orcidId,
                            "nameIdentifierScheme": "ORCID",
                            "schemeUri": "https://orcid.org/"
                        }
                    ]} if inv_user.orcidId else {}
                )
            })
        return ret

    def create_proposal_doi(self, identifiers: list, creators: list, titles: list, publication_year: int,
                            subjects: list, contributors: list, dates: list, types: dict, descriptions: list,
                            funding_references: list, doi_landing_url: str, doi: str) -> None:
        data: dict = {
            "type": "dois",
            "attributes": {
                "prefix": self.prefix, "identifiers": identifiers, "creators": creators, "titles": titles,
                "publisher": self.publisher, "publicationYear": publication_year, "subjects": subjects,
                "contributors": contributors, "language": self.language, "dates": dates, "types": types,
                "rightsList": [
                    {
                        "rights": self.rights_name, "rightsUri": self.rights_uri,
                        "schemeUri": self.rights_scheme_uri, "rightsIdentifier": self.rights_identifier,
                        "rightsIdentifierScheme": self.rights_identifier_scheme,
                        "lang": self.language
                    }
                ],
                "descriptions": descriptions, "fundingReferences": funding_references, "url": doi_landing_url,
                "doi": doi, "event": "publish",
            }
        }
        resp: Response = requests.post(url=f"{self.api_url}/dois", json={"data": data},
                                       auth=(self.username, self.password),
                                       headers={"Accept": "application/vnd.api+json",
                                                "Content-Type": "application/json"})
        if resp.status_code != 201:
            error_msg: str = f"Error creating DOI {identifiers}, error: {resp.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)


def get_datacite_client(config: dict, logger: logging.Logger) -> DataciteClient:
    datacite_config: dict = config.get("integrations", {}).get("datacite", {})
    if not datacite_config:
        return None
    return DataciteClient(
        data_catalogue_doi_base_url=datacite_config.get("dataCatalogueDoiBaseUrl"),
        publisher=datacite_config.get("publisher"),
        prefix=datacite_config.get("prefix"),
        session_suffix=datacite_config.get("sessionSuffix"),
        username=datacite_config.get("username"),
        password=datacite_config.get("password"),
        api_url=datacite_config.get("apiUrl"),
        language=datacite_config.get("language"),
        rights_name=datacite_config.get("rightsName"),
        rights_scheme_uri=datacite_config.get("rightsSchemeUri"),
        rights_uri=datacite_config.get("rightsUri"),
        rights_identifier_scheme=datacite_config.get("rightsIdentifierScheme"),
        rights_identifier=datacite_config.get("rightsIdentifier"),
        funder_name=datacite_config.get("funderName"),
        funder_identifier=datacite_config.get("funderIdentifier"),
        funder_identifier_type=datacite_config.get("funderIdentifierType"),
        logger=logger
    )
