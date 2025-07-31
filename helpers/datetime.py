from datetime import datetime

# ISO 8601 with milliseconds and 'Z' for UTC
DATETIME_ISO_UTC_MS = "%Y-%m-%dT%H:%M:%S.%fZ"

# ISO 8601 without milliseconds
DATETIME_ISO = "%Y-%m-%dT%H:%M:%S"

# ISO 8601 with space separator instead of 'T'
DATETIME_ISO_SPACE = "%Y-%m-%d %H:%M:%S"

# ISO 8601 with milliseconds and space separator
DATETIME_ISO_SPACE_MS = "%Y-%m-%d %H:%M:%S.%f"

# Common US format (month/day/year)
DATETIME_US = "%m/%d/%Y %H:%M:%S"

# Common EU format (day/month/year)
DATETIME_EU = "%d/%m/%Y %H:%M:%S"

# Date-only formats
DATE_ISO = "%Y-%m-%d"
DATE_US = "%m/%d/%Y"
DATE_EU = "%d/%m/%Y"


def try_parse_datetime(date_str: str) -> datetime:
    """
    Attempts to parse a date string using multiple known datetime formats.
    Returns a datetime object if parsing succeeds, otherwise raises ValueError.
    """
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
