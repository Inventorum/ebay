# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from __builtin__ import property

import os
import logging
import vcr
import unittest

from django.conf import settings
from django.test.testcases import TestCase
from rest_framework import test

from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.lib.ebay.authentication import EbayToken
from inventorum.ebay.lib.auth.backends import TrustedHeaderAuthentication
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory


log = logging.getLogger(__name__)


class APIClient(test.APIClient):
    pass


class APITestCase(test.APITestCase):
    maxDiff = None
    client_class = APIClient
    vcr = vcr.VCR(
        serializer='json',
        cassette_library_dir=settings.CASSETTES_DIR,
        record_mode='once',
        filter_headers=['X-EBAY-API-APP-NAME', 'X-EBAY-API-CERT-NAME', 'X-EBAY-API-DEV-NAME', 'Authorization']
    )

    def setUp(self):
        super(APITestCase, self).setUp()

        self._account = EbayAccountFactory(inv_id=StagingTestAccount.ACCOUNT_ID)
        self._user = EbayUserFactory(inv_id=StagingTestAccount.USER_ID, account=self.account)

        self.authenticate(self.user)

    @property
    def account(self):
        """ :rtype: inventorum.ebay.apps.accounts.models.EbayAccountModel """
        return self._account

    @property
    def user(self):
        """ :rtype: inventorum.ebay.apps.accounts.models.EbayUserModel """
        return self._user

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
    ebay_token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE,
                           site_id=settings.EBAY_SUPPORTED_SITES['DE'])

    def setUp(self):
        super(EbayAuthenticatedAPITestCase, self).setUp()
        self.account.token = EbayTokenModel.create_from_ebay_token(self.ebay_token)
        self.account.save()


class UnitTestCase(TestCase):
    pass


def long_running_test():
    """
    Skip a test if the condition is true.
    """
    return unittest.skipIf(os.environ.get('SKIP_LONG_TESTS', False), "Test takes too long...")
