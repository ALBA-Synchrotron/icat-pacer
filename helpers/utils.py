from __future__ import absolute_import, unicode_literals

from urllib.parse import urlparse, urlunparse, ParseResult


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


def mask_amqp_password(url: str) -> str:
    parsed: ParseResult = urlparse(url)
    if parsed.username and parsed.password:
        masked_netloc: str = f"{parsed.username}:*****@{parsed.hostname}"
        if parsed.port:
            masked_netloc += f":{parsed.port}"
        masked_url: str = urlunparse((
            parsed.scheme,
            masked_netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        return masked_url
    return url