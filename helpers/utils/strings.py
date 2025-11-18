from urllib.parse import ParseResult, urlparse, urlunparse


def to_camel_case(string: str) -> str:
    if not string:
        return string
    return string[0].lower() + string[1:]


def string_to_classname(class_name: str, separator: str = '_') -> str:
    class_name_bits = class_name.split(separator)
    res = ''
    for word in class_name_bits:
        res += word.capitalize()
    return res


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
