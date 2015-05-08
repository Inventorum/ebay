# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging


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
