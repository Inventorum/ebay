# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
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


class UnitTestCase(TestCase):
    pass
