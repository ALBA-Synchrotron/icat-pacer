broker_schema_fields: dict = {
    "protocol": {
        "type": "string",
        "allowed": ["amqp", "amqps", "redis", "rediss", "sqs", "memory" "filesystem"],
        "required": True
    },
    "host": {"type": "string", "required": True},
    "port": {"type": "integer", "required": False},
    "username": {"type": "string", "required": False},
    "password": {"type": "string", "required": False},
    "vHost": {"type": "string", "required": False}
}

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
        "check_elastic_settings": True,
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
                    "path": {"type": "string", "required": False},
                    "rotate": {"type": "boolean", "required": False},
                    "maxMBytes": {"type": "integer", "required": False},
                    "backupCount": {"type": "integer", "required": False}
                }
            },
            "elastic": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "serverUrl": {"type": "string", "required": False},
                    "serviceName": {"type": "string", "required": False},
                    "serviceEnvironment": {"type": "string", "required": False},
                    "indexName": {"type": "string", "required": False}
                }
            }
        }
    },
    "exchanges": {
        "type": "list",
        "required": True,
        "check_queues_defined_exchange": True,
        "schema":
            {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "type": {"type": "string", "required": True,
                             "allowed": ["direct", "fanout", "headers", "topic", "x-local-random"]},

                }
            }
    },
    "queues": {
        "type": "list",
        "required": True,
        "schema":
            {
                "type": "dict",
                "schema": {
                    "name": {"type": "string", "required": True},
                    "exchange": {"type": "string", "required": True},
                    "routingKey": {"type": "string", "required": True},
                    "priorityEnabled": {"type": "boolean", "required": True, "default": False},
                    "maxPriorityLevel": {"type": "integer", "required": False, "default": 10}
                }
            }
    },
    "consumers": {
        "type": "list",
        "required": True,
        "check_consumer_defined_queues": True,
        "check_consumer_defined_integrations": True,
        "schema":
            {
                "type": "dict",
                "schema": {
                    "className": {"type": "string", "required": True},
                    "module": {"type": "string", "required": True},
                    "enabled": {"type": "boolean", "required": True},
                    "workers": {"type": "integer", "required": True},
                    "queues": {"type": "list", "required": True,
                               "schema": {"type": "string", "required": True}},
                    "integrations": {"type": "list", "required": True,
                                     "schema": {"type": "string", "required": True}}
                }
            },
    },
    "brokers": {
        "type": "dict",
        "required": True,
        "check_both_username_password": True,
        "check_broker_recipients_forwarding_rules": True,
        "schema": {
            "main": {
                "required": True,
                "type": "dict",
                "schema": broker_schema_fields
            },
            "recipients": {
                "required": False,
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        **broker_schema_fields,
                        "name": {"type": "string", "required": True},
                        "forwardingRules": {
                            "type": "list",
                            "required": True,
                            "schema": {
                                "type": "dict",
                                "schema": {
                                    "fromExchange": {"type": "string", "required": True},
                                    "withRoutingKey": {"type": "string", "required": True},
                                    "toBroker": {"type": "string", "required": True}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "ingestionSettings": {
        "type": "dict",
        "required": True,
        "check_allowed_root_location_paths": True,
        "schema": {
            "messageProcessingRetries": {"type": "integer", "required": True},
            "dataset": {
                "type": "dict",
                "required": True,
                "schema": {
                    "acceptXMLPayloads": {"type": "boolean", "required": True},
                    "mandatoryPathsExistence": {"type": "boolean", "required": True},
                    "mandatorySampleType": {"type": "boolean", "required": True},
                    "checkAllowedLocationPaths": {"type": "boolean", "required": True},
                    "allowedRootLocationPaths": {
                        "type": "list", "required": False, "nullable": True,
                        "schema": {"type": "string", "required": True}
                    },
                    "internalDatasetExchangeName": {"type": "string", "required": True},
                    "internalDatasetRoutingKey": {"type": "string", "required": True},
                    "internalStatisticsRoutingKey": {"type": "string", "required": True},
                    "internalDatasetLinksRoutingKey": {"type": "string", "required": True},
                    "automaticDatasetLocationIndex": {"type": "boolean", "required": True},
                    "maxDatafilesPerDataset": {"type": "integer", "required": True},
                    "galleryFolderName": {"type": "string", "required": True, "default": "gallery"},
                    "xmlNamespacesTransform": {"type": "list", "schema": {"type": "dict", "schema": {
                        "schema": {"type": "string", "required": True}, "to": {"type": "string", "nullable": True}}},
                                               "default": []},
                    "galleryAcceptedUploadTypes": {
                        "type": "list",
                        "default": [
                            ".jpg", ".jpeg", ".png", ".gif", ".bmp",
                            ".tiff", ".tif", ".webp", ".svg", ".ico",
                            ".heic", ".heif",
                            ".cr2", ".nef", ".arw", ".dng"
                        ],
                        "schema": {
                            "type": "string"
                        }
                    },
                }
            },
            "investigation": {
                "type": "dict",
                "required": True,
                "schema": {
                    "defaultEmbargoYears": {"type": "integer", "required": True},
                    "defaultFacilityName": {"type": "string", "required": True},
                    "defaultIndustrialInvestigationTypeName": {"type": "string", "required": True, "default": "INDUSTRIAL"},
                }
            },
            "parameters": {
                "type": "dict",
                "required": True,
                "schema": {
                    "storeParametersValuesAlsoAsString": {"type": "boolean", "required": True},
                }
            },
        }
    },
    "integrations": {
        "type": "dict",
        "required": True,
        "check_visa_integration_settings": True,
        "check_dashboard_integration_settings": True,
        "check_datacite_integration_settings": True,
        "check_panosc_integration_settings": True,
        "schema": {
            "messageForwarding": {
                "type": "dict",
                "required": False,
                "nullable": True,
                "schema": {}
            },
            "visa": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "database": {
                        "type": "dict",
                        "required": False,
                        "schema": {
                            "host": {"type": "string", "required": False},
                            "port": {"type": "integer", "required": False},
                            "database": {"type": "string", "required": False},
                            "username": {"type": "string", "required": False},
                            "password": {"type": "string", "required": False},
                        }
                    }
                }
            },
            "icat": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "server": {
                        "type": "dict",
                        "required": False,
                        "schema": {
                            "url": {"type": "string", "required": True},
                            "authPlugin": {"type": "string", "required": True},
                            "username": {"type": "string", "required": True},
                            "password": {"type": "string", "required": True},
                        }
                    }
                }
            },
            "dashboard": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "exchangeName": {"type": "string", "required": False},
                    "routingKey": {"type": "string", "required": False},
                    "celeryTask": {"type": "string", "required": False},
                }
            },
            "datacite": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "dataCatalogueDoiBaseUrl": {"type": "string", "required": False},
                    "publisher": {"type": "string", "required": False},
                    "prefix": {"type": "string", "required": False},
                    "sessionSuffix": {"type": "string", "required": False},
                    "username": {"type": "string", "required": False},
                    "password": {"type": "string", "required": False},
                    "apiUrl": {"type": "string", "required": False},
                    "language": {"type": "string", "required": False},
                    "rightsName": {"type": "string", "required": False},
                    "rightsSchemeUri": {"type": "string", "required": False},
                    "rightsUri": {"type": "string", "required": False},
                    "rightsIdentifierScheme": {"type": "string", "required": False},
                    "rightsIdentifier": {"type": "string", "required": False},
                    "funderName": {"type": "string", "required": False},
                    "funderIdentifier": {"type": "string", "required": False},
                    "funderIdentifierType": {"type": "string", "required": False},
                }
            },
            "panosc": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "apiUrl": {"type": "string", "required": False},
                    "username": {"type": "string", "required": False},
                    "password": {"type": "string", "required": False},
                    "searchApiUrl": {"type": "string", "required": False},
                }
            },
            "icatPlus": {
                "type": "dict",
                "schema": {
                    "enabled": {"type": "boolean", "required": True},
                    "server": {
                        "type": "dict",
                        "required": False,
                        "schema": {
                            "url": {"type": "string", "required": True},
                            "apiKey": {"type": "string", "required": True},
                        }
                    }
                }
            }
        }
    }
}
