config_yaml_schema: dict = {
    "multiprocessStartMethod": {
        "type": "string",
        "allowed": ["spawn", "fork", "forkserver"],
        "required": False,
    },
    "logging": {
        "type": "dict",
        "required": True,
        "check_path_if_file_is_enabled": False,
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
    "customSerializers": {
        "type": "list",
        "required": False,
        "items": [
            {
                "type": "string", "required": True
            }
        ]
    },
    "exchanges": {
        "type": "list",
        "required": True,
        "check_queues_defined_exchange": True,
        "items": [
            {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "type": {"type": "string", "required": True,
                             "allowed": ["direct", "fanout", "headers", "topic", "x-local-random"]},

                }
            }
        ]
    },
    "queues": {
        "type": "list",
        "required": True,
        "items": [
            {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "exchange": {"type": "string", "required": True},
                    "routingKey": {"type": "string", "required": True}
                }
            }
        ]
    },
    "consumers": {
        "type": "list",
        "required": True,
        "check_consumer_defined_queues": True,
        "items": [
            {
                "type": "dict",
                "schema": {
                    "className": {"type": "string", "required": True},
                    "module": {"type": "string", "required": True},
                    "enabled": {"type": "boolean", "required": True},
                    "workers": {"type": "integer", "required": True},
                    "queues": {"type": "list", "required": True, "items": [{"type": "string", "required": True}]}
                }
            },
        ]
    },
    "broker": {
        "type": "dict",
        "required": True,
        "check_both_username_password": True,
        "schema": {
            "protocol": {"type": "string",
                         "allowed": ["amqp", "amqps", "redis", "rediss", "sqs", "memory" "filesystem"],
                         "required": True},
            "host": {"type": "string", "required": True},
            "port": {"type": "integer", "required": False},
            "username": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "vHost": {"type": "string", "required": False},
        }
    }
}
