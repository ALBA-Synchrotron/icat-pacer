from __future__ import absolute_import, unicode_literals

from kombu import Exchange, Queue

"""
This file defines the exchanges and queues used in the application.

When defining new exchanges or queues consider using slashes (-) to separate the components of the name and dots (.)
to separate keywords on routing keys, as recommended by RabbitMQ documentation:
    
    - https://www.rabbitmq.com/tutorials/tutorial-five-python#topic-exchange
"""

users_exchange = Exchange('users-exchange', type='direct')

EXCHANGES = [
    users_exchange,
]

user_create_queue = Queue('user-create', exchange=users_exchange, routing_key='user.create')

QUEUES = [
    user_create_queue
]

CUSTOM_SERIALIZER_REGISTER_FUNCTIONS = [
    'serializers.xml.register_xml',
]
