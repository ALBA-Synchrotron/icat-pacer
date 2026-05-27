from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity
from psycopg_pool import ConnectionPool

import globals_var
from exceptions.investigation import InvestigationValidationError, InvestigationFacilityNotFound, \
    InvestigationTypeNotFound
from exceptions.parameter import ParameterTypeNotFound
from exceptions.user import UserNotFound
from helpers.dataclasses.investigation import InvestigationContext
from helpers.integrations.icat.extended_client import ICATClient
from helpers.integrations.visa_utils import VISALoader
from helpers.static_settings import ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR, ICAT_USER_ROLE_PROPOSER, \
    ICAT_USER_ROLE_LOCAL_CONTACT, ICAT_USER_ROLE_PARTICIPANT, SAMPLE_ACRONYMS_PARAMETER_NAME
from helpers.utils.base_tasks import BaseTasks
from helpers.utils.investigation import get_investigation_parameter, set_investigation_parameter


class ProposalTasks(BaseTasks):
    ingestion_settings: dict = globals_var.ingestion_settings.get("investigation", {})

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)

    def sync_investigation_visa(self, pg_pool: ConnectionPool, investigation_context: InvestigationContext, *_args,
                                **_kwargs) -> None:
        self.logger.info(f"VISA sync: Synchronizing proposal {investigation_context.name}")

        VISALoader.db_sync_proposal(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment_user(pg_pool, investigation_context, self.logger)

    def sync_investigation_icat(self, icat_client: ICATClient, investigation_context: InvestigationContext, *_args,
                                **_kwargs) -> None:
        self.logger.info(f"ICAT sync: Synchronizing proposal {investigation_context.name}")

        if investigation_context.is_industrial and investigation_context.type != self.ingestion_settings.get(
                "defaultIndustrialInvestigationTypeName", "INDUSTRIAL"):
            raise InvestigationValidationError("Mismatch between investigation type and is_industrial flag")

        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_context.name,
                                                                                "visitId__eq": investigation_context.icat_visit_id},
                                                   flatten_single=True)
        if not investigation:
            investigation: Entity = icat_client.new("Investigation", name=investigation_context.name)
            investigation.name = investigation_context.name

        investigation.title = investigation_context.title
        investigation.summary = investigation_context.summary
        investigation.visitId = investigation_context.icat_visit_id

        self.__handle_foreign_keys(icat_client, investigation, investigation_context)

        investigation.startDate = investigation_context.start_date
        investigation.endDate = investigation_context.end_date
        investigation.releaseDate = investigation_context.release_date

        instrument: Entity = icat_client.search(
            "Instrument",
            conditions={"name__eq": investigation_context.instrument.code},
            flatten_single=True
        )

        if not instrument:
            raise InvestigationValidationError(f"Instrument {investigation_context.instrument.name} not found in ICAT.")

        if investigation.id:
            investigation.update()

        else:
            investigation.doi = ""

            investigation_instrument: Entity = icat_client.new("InvestigationInstrument")
            investigation_instrument.investigation = investigation
            investigation_instrument.instrument = instrument

            investigation.create()
            investigation_instrument.create()

            self.__create_investigation_statistics_parameters(icat_client, investigation)

        self.__update_reimbursed_parcels_parameter(icat_client, investigation, investigation_context)

        if investigation_context.sample_acronyms:
            sample_acronym_param = get_investigation_parameter(icat_client, SAMPLE_ACRONYMS_PARAMETER_NAME,
                                                               entity=investigation)
            _ = set_investigation_parameter(sample_acronym_param, ",".join(investigation_context.sample_acronyms))

        # Users and Roles
        self.__handle_user_roles(icat_client, investigation, investigation_context)

    def __handle_foreign_keys(self, icat_client: ICATClient, investigation: Entity,
                              investigation_context: InvestigationContext) -> None:

        facility = icat_client.search(
            "Facility",
            conditions={"name__eq": investigation_context.facility},
            flatten_single=True
        )

        if not facility:
            raise InvestigationFacilityNotFound(">" + investigation_context.facility + "<")

        inv_type = icat_client.search(
            "InvestigationType",
            conditions={"name__eq": investigation_context.type},
            flatten_single=True
        )

        if not inv_type:
            raise InvestigationTypeNotFound(">" + investigation_context.type + "<")

        investigation.facility = facility
        investigation.type = inv_type

    def __update_reimbursed_parcels_parameter(self, icat_client: ICATClient, investigation: Entity,
                                              investigation_context: InvestigationContext) -> None:
        try:
            self.logger.info(f"ICAT sync: Updating reimbursedParcels parameter for investigation {investigation.name}")

            inv_reimbursed_parcels_param = get_investigation_parameter(icat_client, "reimbursedParcels",
                                                                       entity=investigation)
            set_investigation_parameter(inv_reimbursed_parcels_param, str(investigation_context.visit_count))

        except Exception as e:
            self.logger.error(f"Error updating reimbursedParcels parameter for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __create_investigation_statistics_parameters(self, icat_client: ICATClient, investigation: Entity) -> None:
        try:
            parameter_type_list: list = ['__datasetCount', '__sampleCount', '__fileCount', '__volume']
            self.logger.info(
                f"ICAT sync: Initializing statistics parameters {parameter_type_list} for investigation {investigation.name}")

            for param_type_name in parameter_type_list:
                param = get_investigation_parameter(icat_client, param_type_name, entity=investigation)
                set_investigation_parameter(param, "0")

        except Exception as e:
            self.logger.error(f"Error initializing statistics parameters for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __handle_user_roles(self, icat_client: ICATClient, investigation: Entity,
                            investigation_context: InvestigationContext) -> None:
        errors: list

        # Main Proposer
        self.logger.info(f"ICAT sync: Saving main proposer for investigation {investigation_context.name}")
        proposer_errors: list = self.__save_investigation_user_role(icat_client, investigation,
                                                                    investigation_context,
                                                                    ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR)
        # Co-Proposers
        self.logger.info(f"ICAT sync: Saving proposers for investigation {investigation_context.name}")
        co_proposer_errors: list = self.__save_investigation_user_role(icat_client, investigation,
                                                                       investigation_context,
                                                                       ICAT_USER_ROLE_PROPOSER)
        # Local contact
        self.logger.info(f"ICAT sync: Saving local contact for investigation {investigation_context.name}")
        lc_errors: list = self.__save_investigation_user_role(icat_client, investigation, investigation_context,
                                                              ICAT_USER_ROLE_LOCAL_CONTACT)
        # Participants (visitors)
        self.logger.info(f"ICAT sync: Saving Participants for investigation {investigation_context.name}")
        participants_errors: list = self.__save_investigation_user_role(icat_client, investigation,
                                                                        investigation_context,
                                                                        ICAT_USER_ROLE_PARTICIPANT)

        errors = proposer_errors + co_proposer_errors + lc_errors + participants_errors
        if errors:
            raise UserNotFound("; ".join(f"{type(e).__name__}: {e}" for e in errors))

    def __save_investigation_user_role(self, icat_client: ICATClient, investigation: Entity,
                                       investigation_context: InvestigationContext, role: str) -> list:
        errors: list = []

        inv_users = [u.username.lower() for u in investigation_context.user_list if u.role.lower() == role.lower()]

        current_investigation_users = icat_client.search(
            "InvestigationUser",
            conditions={
                "investigation.id__eq": investigation.id,
                "role__eq": role
            },
            flatten_single=False,
        ) or []

        for inv_user in current_investigation_users:
            if inv_user.user.name.lower() in inv_users:
                inv_users.remove(inv_user.user.name.lower())
            else:
                icat_client.delete(inv_user)
        try:
            for new_user in inv_users:
                user = icat_client.search("User", conditions={"name__eq": new_user}, flatten_single=True)
                if not user:
                    raise UserNotFound(f"User {new_user} not found in ICAT.")

                investigation_user: Entity = icat_client.new("InvestigationUser")
                investigation_user.investigation = investigation
                investigation_user.user = user
                investigation_user.role = role
                investigation_user.create()

        except UserNotFound as e:
            self.logger.error(f"Error saving InvestigationUser for investigation {investigation_context.name}")
            self.logger.error(e)
            errors.append(e)
        return errors
