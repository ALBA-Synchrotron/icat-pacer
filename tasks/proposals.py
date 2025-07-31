from __future__ import absolute_import, unicode_literals

import logging

from dateutil.relativedelta import relativedelta
from psycopg_pool import ConnectionPool

from helpers.dataclasses import InvestigationContext
from helpers.icat_utils import ICATClient
from helpers.visa_utils import VISALoader
from icat.entity import Entity
from helpers import labels


class ProposalTasks:

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def sync_investigation_visa(self, pg_pool: ConnectionPool, investigation_context: InvestigationContext, *_args,
                                **_kwargs):
        self.logger.info(f"VISA sync: Synchronizing proposal {investigation_context.name}")

        VISALoader.db_sync_proposal(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment(pg_pool, investigation_context, self.logger)
        VISALoader.db_sync_experiment_user(pg_pool, investigation_context, self.logger)

    def sync_investigation_icat(self, icat_client: ICATClient, investigation_context: InvestigationContext, *_args,
                                **_kwargs):
        self.logger.info(f"ICAT sync: Synchronizing proposal {investigation_context.name}")

        investigation: Entity = icat_client.search("Investigation", conditions={"name": investigation_context.name},
                                                   flatten_single=False)
        if not investigation:
            investigation: Entity = icat_client.new("Investigation", name=investigation_context.name)
            investigation.name = investigation_context.name

        # Attributes that are always overwritten
        investigation.title = investigation_context.title
        investigation.summary = investigation_context.summary
        investigation.visitId = investigation_context.instrument['code'].lower()

        # Handle FKs
        self.__handle_foreign_keys(icat_client, investigation, investigation_context)

        # SAVE Investigation
        self.__save_investigation(icat_client, investigation, investigation_context)

        # Users and Roles
        self.__handle_user_roles(icat_client, investigation, investigation_context)

    def __handle_foreign_keys(self, icat_client: ICATClient, investigation: Entity, investigation_context: InvestigationContext):
        try:
            # Facility
            investigation.facility = icat_client.search(
                "Facility",
                conditions={"name": investigation_context.facility},
                flatten_single=True
            )

            # InvestigationType
            investigation.type = icat_client.search(
                "InvestigationType",
                conditions={"name": investigation_context.type},
                flatten_single=True
            )
        except Exception as e:
            self.logger.error(f"Error handling foreign keys for investigation {investigation_context.name}")
            self.logger.error(e)
            raise e

    def __save_investigation(self, icat_client: ICATClient, investigation: Entity, investigation_context: InvestigationContext):
        if investigation.id:
            try:
                self.logger.info(f"ICAT sync: Updating investigation {investigation.name}")

                if investigation.doi is None:
                    investigation.doi = ""

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
                investigation.doi = investigation_context.doi or ""

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
                                              investigation_context: InvestigationContext):
        try:
            self.logger.info(f"ICAT sync: Updating reimbursedParcels parameter for investigation {investigation.name}")

            reimbursed_parcels_param_type: Entity = icat_client.search(
                "ParameterType",
                conditions={"name__in": "reimbursedParcels"},
                flatten_single=True
            )
            reimbursed_parcels_investigation_param = icat_client.search(
                "InvestigationParameter",
                conditions={
                    "investigation__id": investigation.id,
                    "type__id": reimbursed_parcels_param_type.id
                },
                flatten_single=True
            )
            reimbursed_parcels_investigation_param.stringValue = str(investigation_context.visit_count)
            reimbursed_parcels_investigation_param.update()
        except Exception as e:
            self.logger.error(f"Error updating reimbursedParcels parameter for investigation {investigation.name}")
            self.logger.error(e)
            raise e

    def __update_investigation_instrument(self, icat_client: ICATClient, investigation: Entity,
                                          investigation_context: InvestigationContext):
        try:
            self.logger.info(f"ICAT sync: Updating investigation instrument for {investigation.name}")

            investigation_instrument: Entity = icat_client.search(
                "InvestigationInstrument",
                conditions={"investigation__name": investigation_context.name},
                flatten_single=True
            )
            if investigation_context.instrument.get("name") != investigation_instrument.instrument.name:
                self.logger.info(f"ICAT sync: Instrument changed for investigation {investigation.name}")
                icat_client.delete(investigation_instrument)
                self.__create_investigation_instrument(icat_client, investigation, investigation_context)

        except Exception as e:
            self.logger.error(f"Error updating investigation instrument for {investigation.name}")
            self.logger.error(e)
            raise e

    def __create_statistics_parameters(self, icat_client: ICATClient, investigation: Entity):
        try:
            self.logger.info(f"ICAT sync: Initializing statistics parameters [] for investigation {investigation.name}")

            parameter_tye_list: list = ['__datasetCount', '__sampleCount', '__fileCount', '__volume']
            for param_type_name in parameter_tye_list:
                param_type: Entity = icat_client.search(
                    "ParameterType",
                    conditions={"name": param_type_name},
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
                                              investigation_context: InvestigationContext):
        try:
            self.logger.info(
                f"ICAT sync: Initializing reimbursedParcels parameter for investigation {investigation.name}")

            reimbursed_parcels_param_type: Entity = icat_client.search(
                "ParameterType",
                conditions={"name": "reimbursedParcels"},
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
                                          investigation_context: InvestigationContext):
        try:
            self.logger.info(f"ICAT sync: Creating investigation instrument for {investigation.name}")

            instrument: Entity = icat_client.search(
                "Instrument",
                conditions={"name": investigation_context.instrument.get("name")},
                flatten_single=True
            )
            if not instrument:
                raise ValueError(f"Instrument {investigation_context.instrument.get('name')} not found in ICAT.")

            investigation_instrument: Entity = icat_client.new("InvestigationInstrument")
            investigation_instrument.investigation = investigation
            investigation_instrument.instrument = instrument
            investigation_instrument.create()
        except Exception as e:
            self.logger.error(f"Error creating investigation instrument for {investigation.name}")
            self.logger.error(e)
            raise e

    def __handle_user_roles(self, icat_client: ICATClient, investigation: Entity, investigation_context: InvestigationContext):
        # Main Proposer
        self.__save_investigation_user_role_unique(icat_client, investigation, investigation_context,
                                                   labels.ICAT_USER_ROLE_PRINCIPAL_INVESTIGATOR)
        # Proposers
        self.__save_investigation_user_role_set(icat_client, investigation, investigation_context, labels.ICAT_USER_ROLE_PROPOSER)
        # Local contact
        self.__save_investigation_user_role_unique(icat_client, investigation, investigation_context,
                                                   labels.ICAT_USER_ROLE_LOCAL_CONTACT)
        # Collaborators
        self.__save_investigation_user_role_set(icat_client, investigation, investigation_context, labels.ICAT_USER_ROLE_COLLABORATOR)

    def __save_investigation_user_role_unique(self, icat_client: ICATClient, investigation: Entity,
                                              investigation_context: InvestigationContext, role: str):
        try:
            try:
                context_investigation_user: Entity = [u['username'] for u in investigation_context.user_list if u['role'] == role][0]
            except IndexError:
                msg = f"InvestigationUser not found in user list provided for investigation {investigation_context.name}"
                self.logger.error(msg)
                raise IndexError(msg)

            user: Entity = icat_client.search(
                "User",
                conditions={"name": context_investigation_user},
                flatten_single=True
            )
            if not user:
                raise ValueError(f"User {context_investigation_user} not found in ICAT.")

            current_investigation_user = icat_client.search(
                "InvestigationUser",
                conditions={"investigation__name": investigation_context.name,
                            "role": role},
                flatten_single=True
            )
            if current_investigation_user and current_investigation_user.user.name != context_investigation_user:
                icat_client.delete(current_investigation_user)

            investigation_user: Entity = icat_client.new("InvestigationUser")
            investigation_user.investigation = investigation
            investigation_user.user = user
            investigation_user.role = role
        except Exception as e:
            self.logger.error(f"Error saving InvestigationUser for investigation {investigation_context.name}")
            self.logger.error(e)
            raise e

    def __save_investigation_user_role_set(self, icat_client: ICATClient, investigation: Entity,
                                           investigation_context: InvestigationContext, role: str):
        try:
            self.logger.info(f"ICAT sync: Saving InvestigationUsers with role {role} for investigation {investigation_context.name}")

            context_investigation_usernames: list[str] = [u['username'] for u in investigation_context.user_list if u['role'] == role]
            if not context_investigation_usernames:
                self.logger.warning(f"No InvestigationUsers found for investigation {investigation_context.name} with role {role}")
                return

            current_investigation_users: list[Entity] = icat_client.search(
                "InvestigationUser",
                conditions={"investigation__name": investigation_context.name, "role": role},
                flatten_single=False
            )
            current_investigation_usernames: list[str] = [investigation_proposer.user.name for investigation_proposer in
                                                          current_investigation_users]

            for context_investigation_username in context_investigation_usernames:
                if context_investigation_username not in current_investigation_usernames:
                    user: Entity = icat_client.search(
                        "User",
                        conditions={"name": context_investigation_username},
                        flatten_single=True
                    )
                    if not user:
                        raise ValueError(f"User {context_investigation_username} not found in ICAT.")

                    investigation_user: Entity = icat_client.new("InvestigationUser")
                    investigation_user.investigation = investigation
                    investigation_user.user = user
                    investigation_user.role = role
                    investigation_user.create()

            for current_investigation_user in current_investigation_users:
                if current_investigation_user.user.name not in context_investigation_usernames:
                    self.logger.info(f"Removing InvestigationUser {current_investigation_user.user.name} with role "
                                     f"{role} from investigation {investigation_context.name}")
                    icat_client.delete(current_investigation_user)

        except Exception as e:
            self.logger.error(f"Error saving InvestigationUsers with role {role} for investigation {investigation_context.name}")
            self.logger.error(e)
            raise e
