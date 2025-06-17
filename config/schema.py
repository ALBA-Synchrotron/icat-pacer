config_yaml_schema: dict = {
    "multiprocessStartMethod": {
        "type": "string",
        "allowed": ["spawn", "fork", "forkserver"],
        "required": False,
    },
    "logging": {
        "type": "dict",
        "required": True,
        "check_path_if_file_is_enabled": True,
        "schema": {
            "logLevel": {"type": "string", "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                         "required": False},
            "printFormat": {"type": "string", "required": False},
            "console": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True}
                }
            },
            "file": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "path": {"type": "string", "required": False}}
            }
        }

    },
    "consumers": {
        "type": "list",
        "required": True,
        "items": [
            {
                "type": "dict",
                "schema": {
                    "module": {"type": "string", "required": True},
                    "enabled": {"type": "boolean", "required": True},
                    "workers": {"type": "integer", "required": True}
                }
            },
        ]

    }
}
