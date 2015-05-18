# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import sys

log = logging.getLogger(__name__)


def int_or_none(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def days_to_seconds(days):
    """
    :type days: int
    :rtype: int
    """
    return 60 * 60 * 24 * days


def preserve_and_reraise_exception():
    exc_class, exc_value, stacktrace = sys.exc_info()
    raise exc_class, exc_value, stacktrace