import datetime
import logging
import queue
import sys
import threading
import traceback as tb
from logging import LogRecord
from logging.handlers import QueueListener
from typing import Union

import elasticsearch as es
import elasticsearch.helpers as es_helpers
import pytz
from python_elasticsearch_logging._queue_handler import ObjectQueueHandler


class CustomElasticSendingHandler(logging.Handler):
    service_name: str
    service_environment: str

    def __init__(self, level,
                 es_client: es.Elasticsearch, index: str, service_name: str, service_environment: str,
                 flush_period: float = 1,
                 batch_size: int = 1000,
                 timezone: str = None) -> None:
        super().__init__(level=level)

        self._es_client = es_client
        self._index = index

        self._flush_period = flush_period
        self._batch_size = batch_size
        self.service_name = service_name
        self.service_environment = service_environment

        self._timezone = timezone

        self.__message_buffer = []
        self.__buffer_lock = threading.Lock()

        self.__timer: threading.Timer = None
        self.__schedule_flush()

    def __schedule_flush(self):
        """Start timer that one-time flushes message buffer."""

        if self.__timer is None:
            self.__timer = threading.Timer(self._flush_period, self.flush)
            self.__timer.daemon = True
            self.__timer.start()

    def flush(self):
        """Send all messages from buffer to es.Elasticsearch."""

        if self.__timer is not None and self.__timer.is_alive():
            self.__timer.cancel()

        self.__timer = None

        if self.__message_buffer:
            try:
                with self.__buffer_lock:
                    actions, self.__message_buffer = self.__message_buffer, []

                es_helpers.bulk(self._es_client, actions, stats_only=True)
            except Exception:
                tb.print_exc(file=sys.stderr)

    def emit(self, record: LogRecord):
        """Add log message to the buffer. \n
        If the buffer is filled up, immedeately flush it."""

        action = self.__prepare_action(record)

        with self.__buffer_lock:
            self.__message_buffer.append(action)

        if len(self.__message_buffer) >= self._batch_size:
            self.flush()
        else:
            self.__schedule_flush()

    def __prepare_action(self, record: LogRecord):
        timestamp_dt: datetime = datetime.datetime.fromtimestamp(record.created)

        if self._timezone:
            tz_info = pytz.timezone(self._timezone)
            timestamp_dt: datetime = timestamp_dt.astimezone(tz_info)

        timestamp_iso = timestamp_dt.isoformat()

        message = record.message

        action = {
            '_index': self._index,
            '_op_type': 'index',
            '@timestamp': timestamp_iso,
            'level': record.levelname,
            'message': message,
            'event': {
                'dataset': f"pacer-{record.levelname.lower()}"
            },
            'service': {
                'name': self.service_name,
                'environment': self.service_environment,
            }
        }

        return action

    def close(self):
        self.flush()

        return super().close()


class CustomElasticHandler(logging.Handler):
    def __init__(self, host: str, index: str, service_name: str, service_environment: str, level=logging.NOTSET,
                 flush_period: float = 1, batch_size: int = 1000,
                 timezone: str = None) -> None:
        super().__init__(level)

        es_client = self._create_elastic_client(host)
        if es_client is None:
            # Disable emiting LogRecord to queue
            setattr(self, 'emit', lambda *a, **kw: None)

            return
        else:
            self._es_client = es_client

        _queue = queue.Queue(maxsize=100000)

        # Object for writing logs to the queue.
        self._queue_handler = ObjectQueueHandler(_queue)

        # Object for reading logs from the queue.
        _elastic_listener = CustomElasticSendingHandler(
            level, es_client, index, service_name, service_environment,
            flush_period=flush_period,
            batch_size=batch_size,
            timezone=timezone)
        self._queue_listener = QueueListener(_queue, _elastic_listener)
        self._queue_listener.start()

    def emit(self, record: LogRecord) -> None:
        """Write logs to the queue."""

        self._queue_handler.emit(record)

    def close(self) -> None:
        if hasattr(self, '_queue_listener'):
            self._queue_listener.stop()

        if hasattr(self, '_es_client'):
            self._es_client.close()

        return super().close()

    def _create_elastic_client(self, host) -> Union[es.Elasticsearch, None]:
        # Check all elastic configss are not None
        if host is None:
            return None

        try:
            es_client: es.Elasticsearch = es.Elasticsearch(
                hosts=[host])
            es_client.info()

            return es_client
        except es.exceptions.ConnectionError:
            pacer_logging.error("Can't connect to Elasticsearch host - {host}")

            return None
        except:
            tb.print_exc(file=sys.stderr)

            return None
