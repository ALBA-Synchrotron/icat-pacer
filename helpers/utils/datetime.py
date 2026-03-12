import datetime
from dateutil import parser

def try_parse_datetime(date_str: str):
    """
    Try to parse a datetime string using ISO 8601 parsing first,
    then fallback to custom formats if needed.
    """
    # First, try robust ISO 8601 parsing
    try:
        return parser.isoparse(date_str)
    except (ValueError, TypeError):
        pass

    # Fallback formats
    datetime_formats = [
        "%Y-%m-%dT%H:%M:%S",        # DATETIME_ISO
        "%Y-%m-%d %H:%M:%S",        # DATETIME_ISO_SPACE
        "%m/%d/%Y %H:%M:%S",        # DATETIME_US
        "%d/%m/%Y %H:%M:%S",        # DATETIME_EU
        "%Y-%m-%d",                 # DATE_ISO
        "%m/%d/%Y",                 # DATE_US
        "%d/%m/%Y",                 # DATE_EU
    ]

    for fmt in datetime_formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse datetime string: '{date_str}'")
