# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import os
import logging
import vcr
import unittest

from django.utils.datetime_safe import datetime
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

    def setUp(self):
        super(APITestCase, self).setUp()

        self.account = EbayAccountFactory(inv_id=StagingTestAccount.ACCOUNT_ID)
        self.user = EbayUserFactory(inv_id=StagingTestAccount.USER_ID, account=self.account)

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
    def setUp(self):
        super(EbayAuthenticatedAPITestCase, self).setUp()
        # Token valid till 2016.09.21 13:18:38
        self.ebay_token = self.create_ebay_token()
        self.account.token = EbayTokenModel.create_from_ebay_token(self.ebay_token)
        self.account.save()

    @staticmethod
    def create_ebay_token():
        return EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE,
                         site_id=settings.EBAY_SUPPORTED_SITES['DE'])

class UnitTestCase(TestCase):
    pass


def long_running_test():
    """
    Skip a test if the condition is true.
    """
    return unittest.skipIf(os.environ.get('SKIP_LONG_TESTS', False), "Test takes too long...")
