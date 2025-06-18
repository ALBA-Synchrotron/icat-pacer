from __future__ import absolute_import, unicode_literals


def string_to_classname(class_name: str, separator: str = '_') -> str:
    class_name_bits = class_name.split(separator)
    res = ''
    for word in class_name_bits:
        res += word.capitalize()
    return res


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
