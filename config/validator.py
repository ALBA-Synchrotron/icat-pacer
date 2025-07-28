from cerberus import Validator
from pygments.lexers import q


class PACERValidator(Validator):
    def __get_child_validator(self, *args, **kwargs) -> Validator:
        return self.__class__(*args, **kwargs)

    def _validate_check_path_if_file_is_enabled(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the 'logging.file.path' field is set when 'logging.file.enabled' is True.
        if not check:
            return

        logging = self.document.get("logging")

        if logging:
            file = logging.get("file")
            if file:
                file_enabled = file.get("enabled")
                if file_enabled and file_enabled is True:
                    if not file.get("path"):
                        self._error(field, "'path' is required when 'enabled' is True")

    def _validate_check_both_username_password(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the both username and password are set in the broker.
        if not check:
            return

        broker = self.document.get("brokers").get("main")

        if broker:
            username = broker.get("username")
            password = broker.get("password")
            if (username and not password) or (password and not username):
                self._error(field, "'username' and 'password' are required when one of them is set")

        broker_recipients = self.document.get("brokers").get("recipients")
        if broker_recipients:
            for recipient in broker_recipients:
                username = recipient.get("username")
                password = recipient.get("password")
                if (username and not password) or (password and not username):
                    self._error(field, "'username' and 'password' are required when one of them is set")

    def _validate_check_queues_defined_exchange(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the exchanges defined in the queues are actually defined
        # as exchanges in the configuration.
        if not check:
            return

        exchanges = self.document.get("exchanges")
        queues = self.document.get("queues")
        if exchanges and queues:
            exchanges_names: list = [i.get("name") for i in exchanges]
            for i in queues:
                exchange_name = i.get("exchange")
                if exchange_name and exchange_name not in exchanges_names:
                    self._error(field, f"Exchange '{exchange_name}' is not defined in 'exchanges'")

    def _validate_check_consumer_defined_queues(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the queues defined in the consumers are actually defined
        # as queues in the configuration.
        if not check:
            return

        consumers = self.document.get("consumers")
        queues = self.document.get("queues")
        if consumers and queues:
            queues_names: list = [i.get("name") for i in queues]
            for i in consumers:
                if i.get("queues"):
                    for queue in i.get("queues"):
                        if queue not in queues_names:
                            self._error(field, f"Queue '{queue}' is not defined in 'queues'")

    def _validate_check_consumer_defined_integrations(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the integrations defined in the consumers are actually defined
        # as integrations in the configuration.
        if not check:
            return

        consumers = self.document.get("consumers")
        integrations = self.document.get("integrations")
        if consumers and integrations:
            integrations_names: list = integrations.keys()
            for i in consumers:
                if i.get("integrations"):
                    for integration in i.get("integrations"):
                        if integration not in integrations_names:
                            self._error(field, f"Integration '{integration}' is not defined in 'integrations'")

    def _validate_check_broker_recipients_forwarding_rules(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the integrations defined in the consumers are actually defined
        # as integrations in the configuration.
        if not check:
            return

        broker_recipients = self.document.get("brokers").get("recipients")
        if broker_recipients:
            exchanges = self.document.get("exchanges")
            queues = self.document.get("queues")
            if exchanges and queues:
                exchanges_names: list = [i.get("name") for i in exchanges]
                queue_routing_keys: list = [i.get("routingKey") for i in queues]

                broker_recipients_names: list = [i.get("name") for i in broker_recipients]

                broker_recipients_fw_rules: list = [rule for i in broker_recipients for rule in
                                                    i.get("forwardingRules")]

                if broker_recipients_fw_rules:
                    for rule in broker_recipients_fw_rules:
                        if rule.get("fromExchange") not in exchanges_names:
                            self._error(field, f"Exchange '{rule.get('fromExchange')}' is not defined in 'exchanges'")
                        if rule.get("withRoutingKey") not in queue_routing_keys:
                            self._error(field,
                                        f"Queue with routing_key '{rule.get('withRoutingKey')}' is not defined in 'queues'")
                        if rule.get("toBroker") not in broker_recipients_names:
                            self._error(field,
                                        f"Broker '{rule.get('toBroker')}' is not defined in 'brokers.recipients'")

    def _validate_check_elastic_settings(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the integrations defined in the consumers are actually defined
        # as integrations in the configuration.
        if not check:
            return

        elastic = self.document.get("logging").get("elastic")
        if elastic.get("enabled") is True:
            if not elastic.get("indexName"):
                self._error(field, "'index' is required when 'logging.elastic.enabled' is True")
            if not elastic.get("serverUrl"):
                self._error(field, "'host' is required when 'logging.elastic.enabled' is True")
            if not elastic.get("serviceName"):
                self._error(field, "'service_name' is required when 'logging.elastic.enabled' is True")
            if not elastic.get("serviceEnvironment"):
                self._error(field, "'service_environment' is required when 'logging.elastic.enabled' is True")

    def _validate_check_visa_integration_settings(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that if the visa integration is enabled, the exchangeName and
        # routingKey are also set.
        if not check:
            return

        visa = self.document.get("integrations").get("visa")
        if visa.get("enabled") is True:
            visa_db = visa.get("database")
            if visa_db:
                host = visa_db.get("host")
                port = visa_db.get("port")
                database = visa_db.get("database")
                username = visa_db.get("username")
                password = visa_db.get("password")

                if not host or not port or not database or not username or not password:
                    self._error(field,
                                "'host', 'port', 'database', 'username' and 'password' are required when 'integrations.visa.enabled' is True")
            if not visa_db:
                self._error(field, "'db' is required when 'integrations.visa.enabled' is True")

    def _validate_check_dashboard_integration_settings(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that if the dashboard integration is enabled, the exchangeName and
        # routingKey are also set.
        if not check:
            return

        dashboard = self.document.get("integrations").get("dashboard")
        if dashboard.get("enabled") is True:
            exchange_name = dashboard.get("exchangeName")
            routing_key = dashboard.get("routingKey")
            celery_task = dashboard.get("celeryTask")

            if not exchange_name or not routing_key or not celery_task:
                self._error(field,
                            "'exchangeName', 'routingKey' and 'celeryTask' are required when 'integrations.dashboard.enabled' is True")

    def _validate_check_datacite_integration_settings(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that if the dashboard integration is enabled, the exchangeName and
        # routingKey are also set.
        if not check:
            return

        datacite = self.document.get("integrations").get("datacite")
        if datacite.get("enabled") is True:
            catalogue_doi_base_url = datacite.get("dataCatalogueDoiBaseUrl")
            publisher = datacite.get("publisher")
            prefix = datacite.get("prefix")
            session_suffix = datacite.get("sessionSuffix")
            username = datacite.get("username")
            password = datacite.get("password")
            apiUrl = datacite.get("apiUrl")
            rights_name = datacite.get("rightsName")
            rights_scheme_uri = datacite.get("rightsSchemeUri")
            rights_uri = datacite.get("rightsUri")
            rights_identifier_scheme = datacite.get("rightsIdentifierScheme")
            rights_identifier = datacite.get("rightsIdentifier")
            funder_name = datacite.get("funderName")
            funder_identifier = datacite.get("funderIdentifier")
            funder_identifier_type = datacite.get("funderIdentifierType")

            if not catalogue_doi_base_url or not publisher or not prefix or not session_suffix or not username or not password or not apiUrl or not rights_name or not rights_scheme_uri or not rights_uri or not rights_identifier_scheme or not rights_identifier or not funder_name or not funder_identifier or not funder_identifier_type:
                self._error(field,
                            "'dataCatalogueDoiBaseUrl', 'publisher', 'prefix', 'sessionSuffix', 'username', 'password', 'apiUrl', 'rightsName', 'rightsSchemeUri', 'rightsUri', 'rightsIdentifierScheme', 'rightsIdentifier', 'funderName', 'funderIdentifier', 'funderIdentifierType' are required when 'integrations.datacite.enabled' is True")

    def _validate_check_panosc_integration_settings(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that if the dashboard integration is enabled, the exchangeName and
        # routingKey are also set.
        if not check:
            return

        panosc = self.document.get("integrations").get("panosc")
        if panosc.get("enabled") is True:
            scoring_url = panosc.get("scoringSvcUrl")
            scoring_username = panosc.get("scoringSvcUsername")
            scoring_password = panosc.get("scoringSvcPassword")
            search_api_url = panosc.get("searchApiUrl")

            if not scoring_url or not scoring_username or not scoring_password or not search_api_url:
                self._error(field,
                            "'scoringSvcUrl', 'scoringSvcUsername', 'scoringSvcPassword' and 'searchApiUrl' are required when 'integrations.panosc.enabled' is True")
