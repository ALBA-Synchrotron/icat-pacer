from datetime import datetime


def elastic_date_check(value) -> bool:
    formats: list = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            _: datetime.datetime = datetime.strptime(value, fmt)
            return True
        except (ValueError, TypeError):
            return False

    return False