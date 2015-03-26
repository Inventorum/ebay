# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


def int_or_none(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None
