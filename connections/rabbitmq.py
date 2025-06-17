from __future__ import absolute_import, unicode_literals

from kombu import Connection

from conf.kombu_config import RABBITMQ_URL


def get_rabbitmq_connection():
    return (RABBITMQ_URL)
