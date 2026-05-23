"""Tests for utils/datetime_utils.py."""
import pytest
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from unittest.mock import patch

from utils.datetime_utils import to_ist, normalize_day, parse_log_date

_IST = ZoneInfo("Asia/Kolkata")
_IST_OFFSET_HOURS = 5.5  # UTC+5:30


class TestToIst:
    def test_utc_datetime_converted_to_ist(self):
        utc_dt = datetime(2024, 1, 15, 6, 0, 0, tzinfo=timezone.utc)
        ist_dt = to_ist(utc_dt)
        # 06:00 UTC == 11:30 IST
        assert ist_dt.hour == 11
        assert ist_dt.minute == 30

    def test_naive_datetime_assumed_utc(self):
        naive_dt = datetime(2024, 1, 15, 0, 0, 0)
        ist_dt = to_ist(naive_dt)
        # 00:00 UTC == 05:30 IST
        assert ist_dt.hour == 5
        assert ist_dt.minute == 30

    def test_none_returns_none(self):
        assert to_ist(None) is None

    def test_result_has_ist_timezone(self):
        utc_dt = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
        ist_dt = to_ist(utc_dt)
        assert ist_dt.tzinfo is not None
        assert ist_dt.tzinfo.key == "Asia/Kolkata"

    def test_already_ist_stays_consistent(self):
        ist_dt = datetime(2024, 1, 15, 12, 0, tzinfo=_IST)
        result = to_ist(ist_dt)
        assert result.hour == 12


class TestNormalizeDay:
    def test_lowercase_day_name_title_cased(self):
        assert normalize_day("monday") == "Monday"

    def test_uppercase_day_name_title_cased(self):
        assert normalize_day("TUESDAY") == "Tuesday"

    def test_mixed_case_title_cased(self):
        assert normalize_day("wEdNeSdAy") == "Wednesday"

    def test_none_returns_none(self):
        assert normalize_day(None) is None

    def test_empty_string_returns_empty(self):
        assert normalize_day("") == ""

    def test_today_returns_current_ist_day_name(self):
        fixed = datetime(2024, 1, 15, 12, 0, tzinfo=_IST)  # Monday
        with patch("utils.datetime_utils.now_ist", return_value=fixed):
            result = normalize_day("today")
        assert result == "Monday"

    def test_yesterday_returns_previous_day(self):
        fixed = datetime(2024, 1, 16, 12, 0, tzinfo=_IST)  # Tuesday
        with patch("utils.datetime_utils.now_ist", return_value=fixed):
            result = normalize_day("yesterday")
        assert result == "Monday"

    def test_tomorrow_returns_next_day(self):
        fixed = datetime(2024, 1, 15, 12, 0, tzinfo=_IST)  # Monday
        with patch("utils.datetime_utils.now_ist", return_value=fixed):
            result = normalize_day("tomorrow")
        assert result == "Tuesday"

    def test_unknown_value_title_cased_as_is(self):
        assert normalize_day("funday") == "Funday"

    def test_whitespace_trimmed(self):
        assert normalize_day("  friday  ") == "Friday"


class TestParseLogDate:
    def test_iso_string_returns_ist_date(self):
        log = {"created_at": "2024-01-15T06:00:00+00:00"}
        result = parse_log_date(log)
        # 06:00 UTC == 11:30 IST on same calendar day
        assert result == date(2024, 1, 15)

    def test_naive_iso_string_assumed_utc(self):
        log = {"created_at": "2024-01-15T00:00:00"}
        result = parse_log_date(log)
        # 00:00 UTC → 05:30 IST, still Jan 15
        assert result == date(2024, 1, 15)

    def test_missing_created_at_returns_none(self):
        assert parse_log_date({}) is None

    def test_none_created_at_returns_none(self):
        assert parse_log_date({"created_at": None}) is None

    def test_invalid_string_returns_none(self):
        assert parse_log_date({"created_at": "not-a-date"}) is None

    def test_datetime_object_accepted(self):
        dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        result = parse_log_date({"created_at": dt})
        assert result == date(2024, 1, 15)

    def test_utc_midnight_may_shift_date_to_previous_ist(self):
        # 2024-01-15 00:00 UTC → 2024-01-15 05:30 IST (still 15th)
        log = {"created_at": "2024-01-15T00:00:00+00:00"}
        result = parse_log_date(log)
        assert result == date(2024, 1, 15)
