# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection

from django.conf import settings


class EbayException(Exception):
    pass


class Ebay(object):
    """
        Inventorum Ebay class with preconfiguration of Ebay Trading API.
    """
    # The newest version from Ebay Trading for 31 March 2015
    compatibility = 911
    version = 911
    timeout = 20
    api = None
    error_lang = None

    def __init__(self, token, site_id=77, error_lang="en_US"):
        self.api = Connection(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                              certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                              debug=settings.DEBUG, timeout=self.timeout, compatibility=self.compatibility,
                              version=self.version)

        self.token = token
        self.site_id = site_id
        self.error_lang = error_lang


    # EBAY PROPERTIES
    @property
    def token(self):
        return self.api.config.get('token')

    @token.setter
    def token(self, new_value):
        self.api.config.set('token', new_value)

    @property
    def site_id(self):
        return self.api.config.get('siteid')

    @site_id.setter
    def site_id(self, new_value):
        self.api.config.set('siteid', new_value)
