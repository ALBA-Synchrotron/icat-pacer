from __future__ import absolute_import, unicode_literals

import logging

from icat.entity import Entity
from psycopg_pool import ConnectionPool

from helpers import static_settings
from helpers.dataclasses.investigation import InvestigationContext
from helpers.integrations.icat_utils import ICATClient
from helpers.integrations.visa_utils import VISALoader


class ProposalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def sync_investigation_visa(self, pg_pool: ConnectionPool, investigation_context: InvestigationContext, *_args,
                                **_kwargs) -> None:
        self.logger.info(f"VISA sync: Synchronizing proposal {investigation_context.name}")

        VISALoader.db_sync_proposal(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment_user(pg_pool, investigation_context, self.logger)

    def sync_investigation_icat(self, icat_client: ICATClient, investigation_context: InvestigationContext, *_args,
                                **_kwargs) -> None:
        self.logger.info(f"ICAT sync: Synchronizing proposal {investigation_context.name}")

        investigation: Entity = icat_client.search("Investigation", conditions={"name__eq": investigation_context.name},
                                                   flatten_single=True)
        if not investigation:
            investigation: Entity = icat_client.new("Investigation", name=investigation_context.name)
            investigation.name = investigation_context.name

        # Attributes that are always overwritten
        investigation.title = investigation_context.title
        investigation.summary = investigation_context.summary
        investigation.visitId = investigation_context.instrument.code.lower()

        # Handle FKs
        self.__handle_foreign_keys(icat_client, investigation, investigation_context)

        # SAVE Investigation
        self.__save_investigation(icat_client, investigation, investigation_context)

        # Users and Roles
        self.__handle_user_roles(icat_client, investigation, investigation_context)

    def __handle_foreign_keys(self, icat_client: ICATClient, investigation: Entity,
                              investigation_context: InvestigationContext) -> None:
        try:
            # Facility
            investigation.facility = icat_client.search(
                "Facility",
                conditions={"name__eq": investigation_context.facility},
                flatten_single=True
            )

            # InvestigationType
            investigation.type = icat_client.search(
                "InvestigationType",
                conditions={"name__eq": investigation_context.type},
                flatten_single=True
            )
        except Exception as e:
            self.logger.error(f"Error handling foreign keys for investigation {investigation_context.name}")
            self.logger.error(e)
            raise e

    def __save_investigation(self, icat_client: ICATClient, investigation: Entity,
                             investigation_context: InvestigationContext) -> None:
        if investigation.id:
            try:
                self.logger.info(f"ICAT sync: Updating investigation {investigation.name}")

                # If new dates are provided, update Investigation dates
                if investigation.startDate != investigation_context.start_date or investigation.endDate != investigation_context.end_date:
                    investigation.startDate = investigation_context.start_date
                    investigation.endDate = investigation_context.end_date
                    investigation.releaseDate = investigation_context.release_date

                    # If reimbursed, gotta update the number of parcels allowed to be reimbursed -> 1 visit = 1 parcel
                    if investigation_context.is_reimbursed:
                        self.__update_reimbursed_parcels_parameter(icat_client, investigation, investigation_context)

                investigation.update()

                # update InvestigationInstrument
                self.__update_investigation_instrument(icat_client, investigation, investigation_context)

            except Exception as e:
                self.logger.error(f"Error updating investigation {investigation.name}")
                self.logger.error(e)
                raise e
        else:
            try:
                self.logger.info(f"ICAT sync: Creating investigation {investigation.name}")

                investigation.startDate = investigation_context.start_date
                investigation.endDate = investigation_context.end_date
                investigation.releaseDate = investigation_context.release_date
                investigation.doi = ""

                investigation.create()

                # create InvestigationInstrument
                self.__create_investigation_instrument(icat_client, investigation, investigation_context)

                # create investigation statistic parameters
                self.__create_statistics_parameters(icat_client, investigation)

                # create reimbursedParcels parameter
                self.__create_reimbursed_parcels_parameter(icat_client, investigation, investigation_context)

            except Exception as e:
                self.logger.error(f"Error creating investigation {investigation.name}")
                self.logger.error(e)
                raise e

    def __update_reimbursed_parcels_parameter(self, icat_client: ICATClient, investigation: Entity,
                                              investigation_context: InvestigationContext) -> None:
        try:
            self.logger.info(f"ICAT sync: Updating reimbursedParcels parameter for investigation {investigation.name}")

            reimbursed_parcels_param_type: Entity = icat_client.search(
                "ParameterType",
                conditions={"name__eq": "reimbursedParcels"},
                flatten_single=True
            )
            reimbursed_parcels_investigation_param = icat_client.search(
                "InvestigationParameter",
                conditions={
                    "investigation.id__eq": investigation.id,
                    "type.id__eq": reimbursed_parcels_param_type.id
                },
                flatten_single=True
            )
            if not reimbursed_parcels_param_type:
                raise ValueError(
                    f"Parameter type reimbursedParcels not found in ICAT investigation {investigation_context.name}.")
            reimbursed_parcels_investigation_param.investigation = investigation
            reimbursed_parcels_investigation_param.type = reimbursed_parcels_param_type
            reimbursed_parcels_investigation_param.stringValue = str(investigation_context.visit_count)
            reimbursed_parcels_investigation_param.update()
        except Exception as e:
            self.logger.error(f"Error updating reimbursedParcels parameter for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __update_investigation_instrument(self, icat_client: ICATClient, investigation: Entity,
                                          investigation_context: InvestigationContext) -> None:
        try:
            self.logger.info(f"ICAT sync: Updating investigation instrument for {investigation.name}")

            investigation_instrument: Entity = icat_client.search(
                "InvestigationInstrument",
                conditions={"investigation.name__eq": investigation_context.name},
                flatten_single=True,
                includes=['instrument']
            )
            if not investigation_instrument:
                raise ValueError(f"InvestigationInstrument for {investigation_context.name} not found in ICAT.")

            if investigation_context.instrument.name != investigation_instrument.instrument.name:
                self.logger.info(f"ICAT sync: Instrument changed for investigation {investigation.name}")
                icat_client.delete(investigation_instrument)
                self.__create_investigation_instrument(icat_client, investigation, investigation_context)

        except Exception as e:
            self.logger.error(f"Error updating investigation instrument for {investigation.name}")
            self.logger.error(e)
            raise e

    def __create_statistics_parameters(self, icat_client: ICATClient, investigation: Entity) -> None:
        try:
            parameter_tye_list: list = ['__datasetCount', '__sampleCount', '__fileCount', '__volume']
            self.logger.info(
                f"ICAT sync: Initializing statistics parameters {parameter_tye_list} for investigation {investigation.name}")

            for param_type_name in parameter_tye_list:
                param_type: Entity = icat_client.search(
                    "ParameterType",
                    conditions={"name__eq": param_type_name},
                    flatten_single=True
                )
                if not param_type:
                    raise ValueError(f"Parameter type {param_type_name} not found in ICAT.")

                inv_param: Entity = icat_client.new('InvestigationParameter')
                inv_param.investigation = investigation
                inv_param.type = param_type
                inv_param.stringValue = '0'
                inv_param.create()
        except Exception as e:
            self.logger.error(f"Error initializing statistics parameters for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __create_reimbursed_parcels_parameter(self, icat_client: ICATClient, investigation: Entity,
                                              investigation_context: InvestigationContext) -> None:
        try:
            self.logger.info(
                f"ICAT sync: Initializing reimbursedParcels parameter for investigation {investigation.name}")

            reimbursed_parcels_param_type: Entity = icat_client.search(
                "ParameterType",
                conditions={"name__eq": "reimbursedParcels"},
                flatten_single=True
            )
            param: Entity = icat_client.new('InvestigationParameter')
            param.investigation = investigation
            param.type = reimbursed_parcels_param_type
            param.stringValue = str(investigation_context.visit_count) if investigation_context.is_reimbursed else '0'
            param.create()
        except Exception as e:
            self.logger.error(f"Error initializing reimbursedParcels parameter for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __create_investigation_instrument(self, icat_client: ICATClient, investigation: Entity,
                                          investigation_context: InvestigationContext) -> None:
        try:
            self.logger.info(f"ICAT sync: Creating investigation instrument for {investigation.name}")

            instrument: Entity = icat_client.search(
                "Instrument",
                conditions={"name__eq": investigation_context.instrument.code},
                flatten_single=True
            )
            if not instrument:
                raise ValueError(f"Instrument {investigation_context.instrument.name} not found in ICAT.")

            investigation_instrument: Entity = icat_client.new("InvestigationInstrument")
            investigation_instrument.investigation = investigation
            investigation_instrument.instrument = instrument
            investigation_instrument.create()
        except Exception as e:
            self.logger.error(f"Error creating investigation instrument for {investigation.name}")
            self.logger.error(e)
            raise e

    def __handle_user_roles(self, icat_client: ICATClient, investigation: Entity,
                            investigation_context: InvestigationContext) -> None:
        errors: list

        # Main Proposer
        self.logger.info(f"ICAT sync: Saving main proposer for investigation {investigation_context.name}")
        proposer_errors: list = self.__save_investigation_user_role_unique(icat_client, investigation,
                                                                           investigation_context,
                                                                           settings.ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR)
        # Co-Proposers
        self.logger.info(f"ICAT sync: Saving proposers for investigation {investigation_context.name}")
        co_proposer_errors: list = self.__save_investigation_user_role_set(icat_client, investigation,
                                                                           investigation_context,
                                                                           settings.ICAT_USER_ROLE_PROPOSER)
        # Local contact
        self.logger.info(f"ICAT sync: Saving local contact for investigation {investigation_context.name}")
        lc_errors: list = self.__save_investigation_user_role_set(icat_client, investigation, investigation_context,
                                                                  settings.ICAT_USER_ROLE_LOCAL_CONTACT)
        # Participants (visitors)
        self.logger.info(f"ICAT sync: Saving Participants for investigation {investigation_context.name}")
        participants_errors: list = self.__save_investigation_user_role_set(icat_client, investigation,
                                                                            investigation_context,
                                                                            settings.ICAT_USER_ROLE_PARTICIPANT)

        errors = proposer_errors + co_proposer_errors + lc_errors + participants_errors
        if errors:
            raise Exception("; ".join(f"{type(e).__name__}: {e}" for e in errors))

    def __save_investigation_user_role_unique(self, icat_client: ICATClient, investigation: Entity,
                                              investigation_context: InvestigationContext, role: str) -> list:
        errors: list = []
        try:
            try:
                context_investigation_user: Entity = \
                    [u.username for u in investigation_context.user_list if u.role.lower() == role.lower()][0]
            except IndexError:
                msg = f"InvestigationUser not found in user list provided for investigation {investigation_context.name}"
                self.logger.error(msg)
                errors.append(IndexError(msg))

            user: Entity = icat_client.search(
                "User",
                conditions={"name__eq": context_investigation_user},
                flatten_single=True
            )
            if not user:
                errors.append(ValueError(f"User {context_investigation_user} not found in ICAT."))
                return errors

            current_investigation_user = icat_client.search(
                "InvestigationUser",
                conditions={
                    "investigation.name__eq": investigation_context.name,
                    "role__eq": role
                },
                flatten_single=True,
                includes=['user']
            )
            if current_investigation_user and current_investigation_user.user.name.lower() != context_investigation_user.lower():
                icat_client.delete(current_investigation_user)

                investigation_user: Entity = icat_client.new("InvestigationUser")
                investigation_user.investigation = investigation
                investigation_user.user = user
                investigation_user.role = role
                investigation_user.create()
        except Exception as e:
            self.logger.error(f"Error saving InvestigationUser for investigation {investigation_context.name}")
            self.logger.error(e)
            errors.append(e)
        return errors

    def __save_investigation_user_role_set(self, icat_client: ICATClient, investigation: Entity,
                                           investigation_context: InvestigationContext, role: str) -> list:
        errors: list = []
        try:
            context_investigation_usernames: list[str] = [u.username.lower() for u in investigation_context.user_list
                                                          if
                                                          u.role == role]
            if not context_investigation_usernames:
                self.logger.warning(
                    f"No InvestigationUsers found for investigation {investigation_context.name} with role {role}")
                return errors

            current_investigation_users: list[Entity] = icat_client.search(
                "InvestigationUser",
                conditions={"investigation.name__eq": investigation_context.name, "role__eq": role},
                flatten_single=False,
                includes=['user']
            )
            current_investigation_usernames: list[str] = [investigation_proposer.user.name.lower() for
                                                          investigation_proposer in
                                                          current_investigation_users] if current_investigation_users else []

            for context_investigation_username in context_investigation_usernames:
                if context_investigation_username.lower() not in current_investigation_usernames:
                    user: Entity = icat_client.search(
                        "User",
                        conditions={"name__eq": context_investigation_username},
                        flatten_single=True
                    )
                    if not user:
                        errors.append(ValueError(f"User {context_investigation_username} not found in ICAT."))
                        continue

                    investigation_user: Entity = icat_client.new("InvestigationUser")
                    investigation_user.investigation = investigation
                    investigation_user.user = user
                    investigation_user.role = role
                    investigation_user.create()

            if current_investigation_users:
                for current_investigation_user in current_investigation_users:
                    if current_investigation_user.user.name.lower() not in context_investigation_usernames:
                        self.logger.info(f"Removing InvestigationUser {current_investigation_user.user.name} with role "
                                         f"{role} from investigation {investigation_context.name}")
                        icat_client.delete(current_investigation_user)

        except Exception as e:
            self.logger.error(
                f"Error saving InvestigationUsers with role {role} for investigation {investigation_context.name}")
            self.logger.error(e)
            errors.append(e)
        return errors
