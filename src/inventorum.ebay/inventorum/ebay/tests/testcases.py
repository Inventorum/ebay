# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from django.utils.datetime_safe import datetime
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.lib.ebay.authentication import EbayToken
import vcr

from django.conf import settings
from django.test.testcases import TestCase
from rest_framework import test

from inventorum.ebay.lib.auth.backends import TrustedHeaderAuthentication
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory


log = logging.getLogger(__name__)


class APIClient(test.APIClient):
    pass


class APITestCase(test.APITestCase):
    client_class = APIClient
    vcr = vcr.VCR(
        serializer='json',
        cassette_library_dir=settings.CASSETTES_DIR,
        record_mode='once',
        filter_headers=['X-EBAY-API-APP-NAME', 'X-EBAY-API-CERT-NAME', 'X-EBAY-API-DEV-NAME', 'Authorization']
    )

    def setUp(self):
        super(APITestCase, self).setUp()

        self.user = EbayUserFactory.create()
        self.account = self.user.account

        self.authenticate(self.user)

    def authenticate(self, user):
        """
        Authenticates the given user

        :param user: User to authenticate
        :type user: inventorum.ebay.apps.accounts.models.EbayUserModel
        """
        credentials = {
            TrustedHeaderAuthentication.AUTHENTICATED_ACCOUNT_HEADER: user.account.inv_id,
            TrustedHeaderAuthentication.AUTHENTICATED_USER_HEADER: user.inv_id
        }
        self.client.credentials(**credentials)


class EbayAuthenticatedAPITestCase(APITestCase):
    # Token valid till 2016.09.21 13:18:38
    ebay_token = EbayToken('AgAAAA**AQAAAA**aAAAAA**rp4aVQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AHlYunD5KLqA+dj6x'
                           '9nY+seQ**qeUBAA**AAMAAA**O2lrsU8I6yjrricneQO018oJ2GChsYf5PaV62oYlcDgguiGB/IPq89c'
                           'LIHfiHXjsz5ONAxNsjSzR+elJQkx6NlF+LTw0p3DdPItRFahsbY3O5+iVksmJr++E1+QF7PvkudovYA'
                           'b183wTZpnZ8np7bsOPAWvFeuRZHbVmwvROSGDQOsAzbWFyVF/6l9xJpHAKULDMzR/nnaCnE24tiTn0V2'
                           'KH+iBAMZzVbuoXM1kEtIll+N6S0JEvvhtTUW8qlmM0blGaXC7uVfd8CeLDudxEi7T2CSLzsqszuzf+fz'
                           'BsbSHmAWLWwndHmgnhqyrOXoDrrL9bd2w8jAgO5Lg58/2LoEPbo7TzFXlqv6RPjr0A/gp2/rpbbTl5XT'
                           'sApPyUN+YiYHuZe0MzxJxgDD6BsGKFK4FmeL+GoC8J9qox5Rk8ynGFOdpjTT29c9gA0NRW0x3iA9zzB5'
                           'O81Z20+euQJ1L58iVFOcDSHbN2pae0kgafUVJsq96yBz7EB56q9jt1KegCbGXVUrkfCzDUrEmZuJCm3'
                           'qw6edh6Xir6x+esSnG65toiF/TuiyyC76UYVXctEFxmJFpHbEOou8fzfEHq4FR8LFM5xEmqsx4tUKUFR'
                           'oxO6pCWHEjPEeOu5Hgl8/JxWDSp/JmTgGwofeIHrgHLJsnA6bhoo6heiAo2O8bGw/sReKccSGNV8JlFZ'
                           'JXCL7leA3APeVt3yi4itCaSCq0JsDpILTCAdC6vnUEQHcVvowhzN7ck1qmY0gUcOo6IOMuJlxn/',
                           expiration_time=datetime(2100, 1, 1))

    def setUp(self):
        super(EbayAuthenticatedAPITestCase, self).setUp()
        self.account.token = EbayTokenModel.create_from_ebay_token(self.ebay_token)


class UnitTestCase(TestCase):
    pass
