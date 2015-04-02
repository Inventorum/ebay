# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.test.testcases import TestCase
from inventorum.ebay.tests import StagingTestAccount

from rest_framework import test

from inventorum.ebay.lib.auth.backends import TrustedHeaderAuthentication
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory


log = logging.getLogger(__name__)


class APIClient(test.APIClient):
    pass


class APITestCase(test.APITestCase):
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


class UnitTestCase(TestCase):
    pass
