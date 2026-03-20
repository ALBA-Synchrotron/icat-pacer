from __future__ import absolute_import, unicode_literals

import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



def running_in_pytest() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ
