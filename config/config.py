import os

import yaml
from config.schema import config_yaml_schema
from config.validator import PACERValidator


class ConfigParser:

    @classmethod
    def __load_yaml_file(cls, config_location: str) -> dict | None:
        if not os.path.exists(config_location):
            raise FileNotFoundError(f"The configuration file at '{config_location}' does not exist.")
        with open(config_location, "r") as config_file:
            try:
                return yaml.safe_load(config_file)
            except yaml.YAMLError as exc:
                print(exc)
        return None

    @classmethod
    def __validate_config(cls, data: dict) -> dict | None:
        validator: PACERValidator = PACERValidator(config_yaml_schema)

        if not validator.validate(data):
            print(validator.errors)
            raise ValueError("The configuration file is invalid.")

        return validator.normalized(data)

    @classmethod
    def load_config(cls, config_location: str) -> dict:
        data: dict = cls.__load_yaml_file(config_location)
        data = cls.__validate_config(data)
        return data
