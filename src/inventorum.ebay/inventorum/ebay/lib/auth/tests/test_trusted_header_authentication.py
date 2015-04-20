# encoding: utf-8
from __future__ import unicode_literals, absolute_import
import logging

from django.test.client import RequestFactory
from inventorum.ebay.apps.accounts.models import EbayUserModel
from rest_framework.exceptions import AuthenticationFailed

from inventorum.ebay.tests.testcases import UnitTestCase
from inventorum.ebay.lib.auth.backends import TrustedHeaderAuthentication

from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory


log = logging.getLogger(__name__)


class TestTrustedHeaderAuthentication(UnitTestCase):
    X_ACCOUNT_HEADER = "HTTP_X_INV_ACCOUNT"
    X_USER_HEADER = "HTTP_X_INV_USER"

    request_factory = RequestFactory()

    def setUp(self):
        super(TestTrustedHeaderAuthentication, self).setUp()

        self.account = EbayAccountFactory.create()
        self.subject = TrustedHeaderAuthentication()

    def test_succeeds_with_valid_credentials(self):
        user = EbayUserFactory.create(account=self.account)

        request = self.get_request({
            self.X_ACCOUNT_HEADER: self.account.inv_id,
            self.X_USER_HEADER: user.inv_id
        })

        self.assert_authentication_succeeds(request, expected_auth_model_inv_id=user.inv_id)

    def test_lazily_creates_users(self):
        request = self.get_request({
            self.X_ACCOUNT_HEADER: self.account.inv_id,
            self.X_USER_HEADER: 1234
        })

        self.assert_authentication_succeeds(request, expected_auth_model_inv_id=1234)
        self.assertTrue(EbayUserModel.objects.by_inv_id(1234).exists())

    def test_skipped_without_account_or_user_header(self):
        user = EbayUserFactory.create(account=self.account)

        for headers in [{self.X_ACCOUNT_HEADER: self.account.inv_id},
                        {self.X_USER_HEADER: user.inv_id}]:
            request = self.get_request(headers)
            self.assert_authentication_skipped(request)

    def get_request(self, headers):
        return self.request_factory.get('/', **headers)

    def assert_authentication_succeeds(self, request, expected_auth_model_inv_id):
        result = self.subject.authenticate(request)
        self.assertIsInstance(result, tuple)

        auth_model, auth = result
        self.assertIsInstance(auth_model, EbayUserModel)
        self.assertEqual(auth_model.inv_id, expected_auth_model_inv_id)

    def assert_authentication_skipped(self, request):
        self.assertEqual(self.subject.authenticate(request), None)

    def assert_authentication_fails(self, request):
        with self.assertRaises(AuthenticationFailed):
            self.subject.authenticate(request)
