import pytest

import globals_var
from exceptions.investigation import InvestigationValidationError, InvestigationFacilityNotFound, \
    InvestigationTypeNotFound
from exceptions.user import UserNotFound
from helpers.contexts.investigation import create_investigation_context
from helpers.contexts.user import create_user_context
from helpers.static_settings import SAMPLE_ACRONYMS_PARAMETER_NAME


class TestICATInvestigationSync:

    def test_create_investigation_non_existent_instrument(self, investigation_tasks, icat_client,
                                                          investigation_non_existent_instrument):
        inv_ctx = create_investigation_context(investigation_non_existent_instrument)

        with pytest.raises(InvestigationValidationError):
            investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

    def test_create_investigation(self, investigation_tasks, icat_client, valid_investigation, valid_user_investigation,
                                  user_tasks):
        user_ctx = create_user_context(valid_user_investigation)
        user_tasks.sync_user_icat(icat_client, user_ctx)

        inv_ctx = create_investigation_context(valid_investigation)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is not None
        assert investigation.investigationInstruments is not None
        assert investigation.visitId == inv_ctx.icat_visit_id
        inv_params = [(i.type.name, i.stringValue) for i in investigation.parameters]
        assert ("__datasetCount", "0") in inv_params
        assert ("__sampleCount", "0") in inv_params
        assert ("__fileCount", "0") in inv_params
        assert ("__volume", "0") in inv_params
        assert (SAMPLE_ACRONYMS_PARAMETER_NAME, ",".join(inv_ctx.sample_acronyms)) in inv_params
        assert len(investigation.investigationUsers) == len(inv_ctx.user_list)

    def test_create_investigation_non_existent_user(self, investigation_tasks, icat_client,
                                                    investigation_non_existent_user):
        inv_ctx = create_investigation_context(investigation_non_existent_user)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        with pytest.raises(UserNotFound):
            investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is not None
        assert investigation.investigationInstruments is not None

    def test_create_investigation_non_existent_facility(self, investigation_tasks, icat_client,
                                                        investigation_non_existent_facility):
        inv_ctx = create_investigation_context(investigation_non_existent_facility)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        with pytest.raises(InvestigationFacilityNotFound):
            investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

    def test_create_investigation_non_existent_investigation_type(self, investigation_tasks, icat_client,
                                                                  investigation_non_existent_investigation_type):
        inv_ctx = create_investigation_context(investigation_non_existent_investigation_type)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        with pytest.raises(InvestigationTypeNotFound):
            investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

    def test_create_investigation_reimbursed_parcels(self, investigation_tasks, icat_client,
                                                     valid_investigation_reimbursed_parcels):
        inv_ctx = create_investigation_context(valid_investigation_reimbursed_parcels)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is not None
        assert investigation.investigationInstruments is not None
        assert ("reimbursedParcels", f"{inv_ctx.visit_count}") in [(i.type.name, i.stringValue) for i in
                                                                   investigation.parameters]

    def test_update_investigation(self, investigation_tasks, icat_client, valid_investigation_update,
                                  valid_user_investigation,
                                  user_tasks):
        user_ctx = create_user_context(valid_user_investigation)
        user_tasks.sync_user_icat(icat_client, user_ctx)

        inv_ctx = create_investigation_context(valid_investigation_update)

        investigation = icat_client.search("Investigation",
                                           conditions={"name__eq": inv_ctx.name, "visitId__eq": inv_ctx.icat_visit_id},
                                           flatten_single=True)
        assert investigation is None

        investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation",
                                           conditions={"name__eq": inv_ctx.name, "visitId__eq": inv_ctx.icat_visit_id},
                                           flatten_single=True)
        assert investigation is not None
        assert investigation.investigationInstruments is not None
        assert len(investigation.investigationUsers) == len(inv_ctx.user_list)

        inv_ctx.title = "title updated"
        prev_inv_ctx_users = inv_ctx.user_list.copy()
        inv_ctx.user_list = inv_ctx.user_list[1:]
        inv_ctx.visit_count = 10
        assert len(prev_inv_ctx_users) != len(inv_ctx.user_list)

        investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)
        investigation = icat_client.search("Investigation",
                                           conditions={"name__eq": inv_ctx.name, "visitId__eq": inv_ctx.icat_visit_id},
                                           flatten_single=True)

        assert investigation.title == inv_ctx.title
        assert len(investigation.investigationUsers) == len(inv_ctx.user_list)
        assert ("reimbursedParcels", f"{inv_ctx.visit_count}") in [(i.type.name, i.stringValue) for i in
                                                                   investigation.parameters]

    def test_create_industrial_investigation(self, investigation_tasks, icat_client,
                                             valid_investigation_industrial):
        inv_ctx = create_investigation_context(valid_investigation_industrial)
        ingestion_settings: dict = globals_var.ingestion_settings.get("investigation", {})

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is not None
        assert investigation.investigationInstruments is not None
        assert investigation.releaseDate is None
        assert investigation.type.name == ingestion_settings.get("defaultIndustrialInvestigationTypeName", "INDUSTRIAL")

    def test_create_invalid_industrial_investigation(self, investigation_tasks, icat_client,
                                                     invalid_investigation_industrial):
        inv_ctx = create_investigation_context(invalid_investigation_industrial)

        investigation = icat_client.search("Investigation", conditions={"name__eq": inv_ctx.name}, flatten_single=True)
        assert investigation is None

        with pytest.raises(InvestigationValidationError):
            investigation_tasks.sync_investigation_icat(icat_client, inv_ctx)
