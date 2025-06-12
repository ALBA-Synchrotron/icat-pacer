
# TODO: Look if Kombu has a client mock utility -> url = 'memory://'

# while True:
#     with Connection('memory:///') as conn:
#         producer = conn.Producer(serializer='json')
#         producer.publish({"foo": "bar"}, exchange=media_exchange, routing_key='video', declare=task_queues)
#     sleep(0.1)

# see: https://github.com/celery/kombu/issues/606


