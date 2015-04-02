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
            TrustedHeaderAuthentication.TRUSTED_ACCOUNT_HEADER: user.account.inv_id,
            TrustedHeaderAuthentication.TRUSTED_USER_HEADER: user.inv_id
        }
        self.client.credentials(**credentials)


class EbayAuthenticatedAPITestCase(APITestCase):
    # Token valid till 2016.09.21 13:18:38
    ebay_token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE)

    def setUp(self):
        super(EbayAuthenticatedAPITestCase, self).setUp()
        self.account.token = EbayTokenModel.create_from_ebay_token(self.ebay_token)


class UnitTestCase(TestCase):
    pass
