# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf import settings


class EbayToken(object):
    """
    Data object to keeps expiration time and value
    """
    expiration_time = None
    value = None

    def __init__(self, value, expiration_time, site_id=None):
        self.expiration_time = expiration_time
        self.value = value
        self.site_id = site_id

    @property
    def error_language(self):
        return settings.EBAY_ERROR_LANGUAGE_BY_SITE_ID.get(self.site_id, 'en_US')