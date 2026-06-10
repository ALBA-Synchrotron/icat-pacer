from helpers.utils.strings import to_snake_case


def snakify_xml_dict_keys(d: dict) -> dict:
    result: dict = {}
    for key, value in d.items():
        snake_key: str = to_snake_case(key)
        if isinstance(value, list):
            snake_key += "s"

        result[snake_key] = value

    return result
