import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
import dateutil.tz
import pytz
from django.utils import timezone


def from_utc_to_local_datetime(utc_date):
    time_zone = pytz.timezone('Europe/Madrid')
    return utc_date.astimezone(time_zone)


def get_local_datetime():
    now = timezone.now()
    local_now = from_utc_to_local_datetime(now)
    return local_now.replace(microsecond=0)


def deserialize_date(date, date_format=settings.DATE_FORMAT):
    unaware_date = datetime.datetime.strptime(date, date_format)
    aware_date = settings.PYTZ_TIME_ZONE.localize(unaware_date)
    return aware_date


def serialize_date(date, date_format=settings.DATE_FORMAT):
    if date is not None:
        if date.tzinfo == pytz.UTC:
            date = from_utc_to_local_datetime(date)
        serialized_date = date.strftime(date_format)
        return serialized_date
    else:
        return ''


def get_timezone_offset(dt):
    offset_seconds = settings.PYTZ_TIME_ZONE.utcoffset(dt).seconds
    offset_hours = offset_seconds / 3600.0
    return offset_hours


def correct_tzinfo(date):
    date = date.replace(tzinfo=None)
    offset = get_timezone_offset(date)
    date = date.replace(tzinfo=dateutil.tz.tzoffset(None, offset * 60 * 60))
    return date


def add_datedelta(date, **kwargs):
    result = date + relativedelta(**kwargs)
    return correct_tzinfo(result)
