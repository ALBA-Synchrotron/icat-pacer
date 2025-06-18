from cerberus import Validator


class PACERValidator(Validator):
    def __get_child_validator(self, *args, **kwargs) -> Validator:
        return self.__class__(*args, **kwargs)

    def _validate_check_path_if_file_is_enabled(self, check, field, _) -> None:
        """
        The rule's arguments are validated against this schema:

        {'type': 'boolean'}
        """
        # For some reason custom  rules are not checked when set on a nested schema.
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
        # For some reason custom  rules are not checked when set on a nested schema.
        # This rule is a workaround that checks that the both username and password are set in the broker.
        if not check:
            return

        broker = self.document.get("broker")

        if broker:
            username = broker.get("username")
            password = broker.get("password")
            if not username or not password:
                self._error(field, "'username' and 'password' are required when one of them is set")
