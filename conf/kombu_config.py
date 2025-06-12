from __future__ import absolute_import, unicode_literals

import os
import json
import logging

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# RABBITMQ settings
try:
    with open(os.path.join(BASE_DIR, '..', 'config', 'rabbitmq.json')) as rabbitmq_conf:
        RABBITMQ_SETTINGS = json.load(rabbitmq_conf)
except FileNotFoundError as e:
    # logger.error(e)
    RABBITMQ_SETTINGS = {
        "USER": "",
        "PSSWRD": "",
        "HOST": "",
        "VHOST": "",
    }

RABBITMQ_URL = f'amqp://{RABBITMQ_SETTINGS["USER"]}:{RABBITMQ_SETTINGS["PSSWRD"]}@{RABBITMQ_SETTINGS["HOST"]}/{RABBITMQ_SETTINGS["VHOST"] if "VHOST" in RABBITMQ_SETTINGS else "/"}'
