from __future__ import absolute_import, unicode_literals

import hashlib
import os
import re
import string


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def running_in_pytest() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


def camel_case_to_snake_case(string_str: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string_str).lower()


def to_base62(num: int) -> str:
    base_62: str = string.digits + string.ascii_uppercase + string.ascii_lowercase
    if num == 0:
        return base_62[0]

    result, base = [], len(base_62)

    while num > 0:
        num, rem = divmod(num, base)
        result.append(base_62[rem])

    return "".join(reversed(result))

def generate_doi_visit_suffix(s: str, length: int = 4) -> str:
    digest = hashlib.sha1(s.encode()).digest()
    num: int = int.from_bytes(digest[:4], byteorder="big")
    encoded: str = to_base62(num)
    return encoded[:length].rjust(length, '0')