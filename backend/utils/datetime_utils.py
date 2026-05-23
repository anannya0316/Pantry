from datetime import (
    datetime,
    timedelta,
    timezone,
)

from zoneinfo import ZoneInfo


IST = ZoneInfo(
    "Asia/Kolkata"
)


def now_utc():

    return datetime.now(
        timezone.utc
    )


def now_ist():

    return datetime.now(
        IST
    )


def parse_log_date(log: dict):
    """Parse a log's created_at field and return its date in IST, or None."""
    created = log.get("created_at")
    if created is None:
        return None
    try:
        if isinstance(created, str):
            created = datetime.fromisoformat(created)
        return to_ist(created).date()
    except Exception:
        return None


_RELATIVE_DAYS = {
    "today":     0,
    "yesterday": -1,
    "tomorrow":  1,
}


def normalize_day(value: str) -> str:
    """
    Convert a raw day value to the canonical Title-case day name used by DAY_NAMES.

    Handles relative references (resolved in IST):
      "today"     → e.g. "Monday"
      "yesterday" → e.g. "Sunday"
      "tomorrow"  → e.g. "Tuesday"

    Already-canonical names are returned Title-cased:
      "monday" → "Monday"

    Unrecognised values are returned Title-cased as-is so downstream
    validation can surface the error clearly.
    """
    if not value:
        return value

    key = value.strip().lower()

    if key in _RELATIVE_DAYS:
        return (now_ist() + timedelta(days=_RELATIVE_DAYS[key])).strftime("%A")

    return value.strip().title()


def to_ist(dt):

    if dt is None:
        return None

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt.astimezone(IST)