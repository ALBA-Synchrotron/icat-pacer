import re
from typing import Iterable

from icat import Client
from icat.entity import Entity
from icat.query import Query


class ICATTestClient:

    client: Client

    def __init__(self) -> None:
        self.client = Client(url)
