from __future__ import absolute_import, unicode_literals

import datetime
import logging

from icat.entity import Entity
from psycopg_pool import ConnectionPool

import globals_var
from exceptions.investigation import InvestigationNotFound
from exceptions.investigation_ops import InvestigationOpsValidationError
from helpers.integrations.icat.extended_client import ICATClient
from helpers.integrations.datacite import DataciteClient
from helpers.integrations.panosc import PaNOSCClient
from helpers.models.investigation import InvestigationOperationsContext
from helpers.static_settings import ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR, ICAT_USER_ROLE_PARTICIPANT, \
    DATACITE_CONTRIBUTOR_DATA_COLLECTOR, ICAT_USER_ROLE_LOCAL_CONTACT, DATACITE_CONTRIBUTOR_PROJECT_MANAGER, \
    DATACITE_CONTRIBUTOR_PROJECT_MEMBER, ICAT_USER_ROLE_PROPOSER
from helpers.integrations.visa_utils import VISALoader
from helpers.utils.base_tasks import BaseTasks
from helpers.utils.utils import generate_doi_visit_suffix


class InvestigationOpsTasks(BaseTasks):

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    @classmethod
    def __get_investigation_users_by_role(cls, inv_users: list) -> dict:
        ret: dict = {}
        for inv_user in inv_users:
            if inv_user.role not in ret:
                ret[inv_user.role] = []
            ret[inv_user.role].append(inv_user.user)
        return ret

    def __general_investigation_check(self, investigation: Entity, check_doi=True, check_datasets=True,
                                      check_users=True, check_dates=True, check_instruments=True,
                                      check_end_date_today=False, check_no_doi=False,
                                      check_industrial: bool = True) -> None:
        ingestion_settings: dict = globals_var.ingestion_settings.get("investigation", {})
        industrial_type_inv_name: str = ingestion_settings.get("defaultIndustrialInvestigationTypeName", "INDUSTRIAL")

        if check_industrial and investigation.type.name == industrial_type_inv_name:
            raise InvestigationOpsValidationError(
                f"Investigation: Investigation {investigation.name} is of type {industrial_type_inv_name} and cannot be minted")

        if check_doi and investigation.doi:
            error_msg: str = f"Investigation: Investigation {investigation.name} already has a DOI {investigation.doi}"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_datasets and not investigation.datasets:
            error_msg: str = f"Investigation: Investigation {investigation.name} has no datasets, it will not be minted"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_dates and not investigation.releaseDate or not investigation.startDate or not investigation.endDate:
            error_msg: str = f"Investigation: Investigation {investigation.name} has no releaseDate, endDate or startDate, it will not be minted"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_users and not investigation.investigationUsers:
            error_msg: str = f"Investigation: Investigation {investigation.name} has no users, it will not be minted"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_instruments and not investigation.investigationInstruments:
            error_msg: str = f"Investigation: Investigation {investigation.name} has no instruments, it will not be minted"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_end_date_today and investigation.endDate and investigation.endDate.timestamp() > datetime.datetime.now().timestamp():
            error_msg: str = f"Investigation: Investigation {investigation.name} has an end date in the future, it will not be minted"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

        if check_no_doi and not investigation.doi:
            error_msg: str = f"Investigation: Investigation {investigation.name} has no DOI"
            self.logger.error(error_msg)
            raise InvestigationOpsValidationError(error_msg)

    def create_panosc_item(self, icat_client: ICATClient, inv_ops_ctx: InvestigationOperationsContext,
                           panosc_client: PaNOSCClient, *_args,
                           **_kwargs) -> None:
        self.logger.info(f"PaNOSC item creation: Creating item for proposal {inv_ops_ctx.name}")
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": inv_ops_ctx.name,
                                                                                "visitId__eq": inv_ops_ctx.visit_id, },
                                                   flatten_single=True)
        if not investigation:
            error_msg: str = f"PaNOSC item creation: Investigation {inv_ops_ctx.name} not found"
            self.logger.error(error_msg)
            raise InvestigationNotFound(error_msg)

        self.__general_investigation_check(investigation, check_doi=False, check_no_doi=True, check_datasets=False,
                                           check_users=False)
        public_investigation_info: dict = panosc_client.retrieve_public_investigation_info(investigation.name)

        pss_id: str = f"{investigation.name}/{investigation.visitId}"

        if panosc_client.item_exists(pss_id):
            self.logger.info(f"Investigation PaNOSC indexes: Index for proposal {investigation.name} already exists")
            panosc_client.update_item(pss_id, public_investigation_info)
        else:
            self.logger.info(f"Investigation PaNOSC indexes: Index for proposal {investigation.name} does not exist")
            panosc_client.create_item(pss_id, public_investigation_info)

        self.logger.info(
            f"Item exists for proposal {investigation.name}: {panosc_client.item_exists(investigation.name)}")
        panosc_client.recompute_weights()

    def mint_proposal(self, pg_pool: ConnectionPool, icat_client: ICATClient, datacite_client: DataciteClient,
                      inv_ops_ctx: InvestigationOperationsContext, *_args, **_kwargs) -> None:
        self.logger.info(f"Investigation mint: Creating a DOI for proposal {inv_ops_ctx.name}")
        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": inv_ops_ctx.name,
                                                                                "visitId__eq": inv_ops_ctx.visit_id},
                                                   flatten_single=True, includes=["facility"])
        if not investigation:
            error_msg: str = f"Investigation mint: Investigation {inv_ops_ctx.name} not found"
            self.logger.error(error_msg)
            raise InvestigationNotFound(error_msg)

        self.__general_investigation_check(investigation, check_end_date_today=True)

        investigation_users_role: dict = self.__get_investigation_users_by_role(investigation.investigationUsers)
        instrument_names: list = [i.instrument.name for i in investigation.investigationInstruments]

        visit_suffix: str = generate_doi_visit_suffix(f"{inv_ops_ctx.name}-{investigation.visitId}")
        doi: str = f"{datacite_client.prefix}/{datacite_client.session_suffix}-{investigation.name}-{visit_suffix}"
        doi_landing_url: str = f"{datacite_client.data_catalogue_doi_base_url}/{doi}"
        identifiers: list = [
            {"identifier": doi, "identifierType": "DOI"}]
        self.logger.debug(
            f"Investigation mint: Identifiers: {identifiers}, DOI: {doi}, DOI landing URL: {doi_landing_url}")

        creators: list = datacite_client.generate_user_data_structure(
            investigation_users_role.get(ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR, []),
            investigation_users_role.get(ICAT_USER_ROLE_PARTICIPANT, [])
        )
        contributor_data_collector: list = datacite_client.generate_user_data_structure(
            investigation_users_role.get(ICAT_USER_ROLE_LOCAL_CONTACT, []),
            contributor_type=DATACITE_CONTRIBUTOR_DATA_COLLECTOR)
        contributor_project_manager: list = datacite_client.generate_user_data_structure(
            investigation_users_role.get(ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR, []),
            contributor_type=DATACITE_CONTRIBUTOR_PROJECT_MANAGER)
        contributor_project_member: list = datacite_client.generate_user_data_structure(
            investigation_users_role.get(ICAT_USER_ROLE_PROPOSER, []),
            contributor_type=DATACITE_CONTRIBUTOR_PROJECT_MEMBER)

        contributors: list = contributor_data_collector + contributor_project_manager + contributor_project_member
        self.logger.debug(f"Investigation mint: Total {len(creators)} creators,{len(contributors)} contributors")

        titles: list = [{"title": investigation.title, "lang": datacite_client.language}]
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

        investigation.doi = doi
        investigation.update()
        self.logger.info(f"Investigation mint: Investigation {inv_ops_ctx.name} updated in ICAT with new DOI {doi}")

        if pg_pool:
            VISALoader.db_update_investigation_doi(pg_pool, f"{investigation.name}/{investigation.visitId}", doi,
                                                   doi_landing_url, self.logger)
            self.logger.info(f"Investigation mint: Investigation {inv_ops_ctx.name} updated in VISA with new DOI {doi}")
