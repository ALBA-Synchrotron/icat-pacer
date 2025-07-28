from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity
from psycopg_pool import ConnectionPool
from helpers.dataclasses import InvestigationOperationsContext
from helpers.icat_utils import ICATClient
from helpers.datacite import DataciteClient
from helpers.visa_utils import VISALoader


class InvestigationOpsTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    @classmethod
    def __get_investigation_users_by_role(cls, inv_users: list) -> dict:
        ret: dict = {}
        for inv_user in inv_users:
            if inv_user.role not in ret:
                ret[inv_user.role] = []
            ret[inv_user.role].append(inv_user.user)
        return ret

    def mint_proposal(self, pg_pool: ConnectionPool, icat_client: ICATClient, datacite_client: DataciteClient,
                      inv_ops_ctx: InvestigationOperationsContext, *_args, **_kwargs) -> None:
        self.logger.info(f"Investigation mint: Creating a DOI for proposal {inv_ops_ctx.name}")

        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": inv_ops_ctx.name},
                                                   flatten_single=True,
                                                   includes=["datasets", "investigationUsers",
                                                             "investigationUsers.user", "type",
                                                             "investigationInstruments",
                                                             "investigationInstruments.instrument",
                                                             "facility"])
        if not investigation:
            error_msg: str = f"Investigation mint: Investigation {inv_ops_ctx.name} not found"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        if not investigation.datasets and 5 == 6:
            error_msg: str = f"Investigation mint: Investigation {inv_ops_ctx.name} has no datasets, it will not be minted"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        investigation_users_role: dict = self.__get_investigation_users_by_role(investigation.investigationUsers)
        if not investigation_users_role:
            error_msg: str = f"Investigation mint: Investigation {inv_ops_ctx.name} has no users, it will not be minted"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        instrument_names: list = [i.instrument.name for i in investigation.investigationInstruments]

        doi: str = f"{datacite_client.prefix}/{datacite_client.session_suffix}-{investigation.name}"
        doi_landing_url: str = f"{datacite_client.data_catalogue_doi_base_url}/{doi}"
        identifiers: list = [
            {"identifier": doi, "identifierType": "DOI"}]
        self.logger.debug(
            f"Investigation mint: Identifiers: {identifiers}, DOI: {doi}, DOI landing URL: {doi_landing_url}")

        creators: list = datacite_client.generate_user_data_structure(
            investigation_users_role.get("Principal investigator", []), investigation_users_role.get("Participant"), [])
        contributors: list = datacite_client.generate_user_data_structure(investigation_users_role.get("Local contact"))
        self.logger.debug(f"Investigation mint: Total {len(creators)} creators,{len(contributors)} contributors")

        titles: list = [{"title": investigation.title.replace("\n", "")}]
        descriptions: list = [{"description": investigation.summary, "descriptionType": "Abstract"}]
        subjects: list = [
            {
                "subject": investigation.type.description,
                "subjectScheme": "Proposal Type Description",
            },
            {
                "subject": investigation.name,
                "subjectScheme": "Proposal",
            }
        ]
        if instrument_names:
            subjects.append(
                {
                    "subject": ", ".join(instrument_names),
                    "subjectScheme": f"Instrument{'s' if len(instrument_names) > 1 else ''}",
                }
            )

        if not investigation.releaseDate or not investigation.startDate:
            error_msg: str = f"Investigation mint: Investigation {inv_ops_ctx.name} has no releaseDate or startDate, it will not be minted"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        dates: list = [
            {
                "date": investigation.startDate.isoformat(),
                "dateType": "Collected"
            },
            {
                "date": investigation.releaseDate.isoformat(),
                "dateType": "Available"
            }
        ]

        publication_year: int = investigation.releaseDate.year if investigation.releaseDate else 9999
        types: dict = {
            "resourceTypeGeneral": "Dataset",
            "resourceType": "Experiment session"
        }
        funding_references: list = [
            {
                "funderName": datacite_client.funder_name,
                "funderIdentifier": datacite_client.funder_identifier,
                "funderIdentifierType": datacite_client.funder_identifier_type,
                "awardNumber": investigation.name,
                "awardTitle": investigation.title
            }
        ]
        datacite_client.create_proposal_doi(identifiers, creators, titles, publication_year, subjects, contributors,
                                            dates, types, descriptions, funding_references, doi_landing_url, doi)
        self.logger.info(f"Investigation mint: DOI minted for proposal {inv_ops_ctx.name}")
        return

        investigation.doi = doi
        investigation.update()
        self.logger.info(f"Investigation mint: Investigation {inv_ops_ctx.name} updated in ICAT with new DOI {doi}")

        VISALoader.db_update_investigation_doi(pg_pool, investigation.name, doi, doi_landing_url, self.logger)
        self.logger.info(f"Investigation mint: Investigation {inv_ops_ctx.name} updated in VISA with new DOI {doi}")
