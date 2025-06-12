from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from multiprocessing import Process
import xml.etree.ElementTree as ET


# TODO: REVIEW THIS GEPETO CODE
class XMLWorker(ConsumerMixin):
    def __init__(self, conn_url, queue_name, routing_key):
        self.connection = Connection(conn_url)
        self.exchange = Exchange('xml_ingest', type='direct')
        self.queue = Queue(queue_name, exchange=self.exchange, routing_key=routing_key)

    def get_consumers(self, Consumer, channel):
        return [Consumer(
            queues=[self.queue],
            callbacks=[self.handle_message],
            accept=['text/plain']  # adjust to 'application/xml' if needed
        )]

    def handle_message(self, body, message):
        try:
            xml_data = ET.fromstring(body)
            print(f"[{self.queue.name}] Parsed XML root: {xml_data.tag}")
            # TODO: Insert into database here
            message.ack()
        except Exception as e:
            print(f"[{self.queue.name}] Error: {e}")
            message.reject()


# Launch one process per queue
def launch_worker_process(conn_url, queue_name, routing_key):
    def worker():
        worker = XMLWorker(conn_url, queue_name, routing_key)
        worker.run()

    return Process(target=worker)


if __name__ == "__main__":
    queues = [
        ("queue1", "rk1"),
        ("queue2", "rk2"),
        ("queue3", "rk3"),
    ]

    conn_url = "amqp://guest:guest@localhost:5672//"

    processes = []
    for qname, rkey in queues:
        p = launch_worker_process(conn_url, qname, rkey)
        p.start()
        processes.append(p)

    # Wait for all workers to finish (runs indefinitely)
    for p in processes:
        p.join()
