from datetime import datetime

# Datetime formats
DATETIME_ISO = "%Y-%m-%dT%H:%M:%S"
DATETIME_ISO_8601_UTC = '%Y-%m-%dT%H:%M:%SZ'
DATETIME_ISO_UTC_MS = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_ISO_SPACE = "%Y-%m-%d %H:%M:%S"
DATETIME_ISO_SPACE_MS = "%Y-%m-%d %H:%M:%S.%f"
DATETIME_US = "%m/%d/%Y %H:%M:%S"
DATETIME_EU = "%d/%m/%Y %H:%M:%S"

# Date-only formats
DATE_ISO = "%Y-%m-%d"
DATE_US = "%m/%d/%Y"
DATE_EU = "%d/%m/%Y"


def try_parse_datetime(date_str: str) -> datetime:
    datetime_formats = [
        DATETIME_ISO_UTC_MS,
        DATETIME_ISO,
        DATETIME_ISO_SPACE,
        DATETIME_ISO_SPACE_MS,
        DATETIME_US,
        DATETIME_EU,
        DATE_ISO,
        DATE_US,
        DATE_EU,
    ]

    for fmt in datetime_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse datetime string: '{date_str}'")
