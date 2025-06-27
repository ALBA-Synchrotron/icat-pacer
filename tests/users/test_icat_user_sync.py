import multiprocessing

import pytest

from consumers.users import UsersConsumer

MODULE: str = "consumers.users"
WORKERS: int = 1
ENABLED: bool = True
CONSUMER_QUEUES: list = []
LOG_QUEUE: multiprocessing.Queue = None
CONFIG: dict = {}
ICAT_SESSION_ID: str = ""


@pytest.fixture
def consumer():
    return UsersConsumer(MODULE, WORKERS, ENABLED, CONSUMER_QUEUES, LOG_QUEUE, CONFIG, ICAT_SESSION_ID)

def test_consumer_init(consumer):
