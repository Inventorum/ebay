# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.tests import IntegrationTest
from inventorum.ebay.tests.testcases import APITestCase, EbayAuthenticatedAPITestCase
from inventorum.util.django.timezone import datetime


class TestDjangoEbayAuthenticator(APITestCase):

    @IntegrationTest.use_cassette('auth/test_endpoint_without_ebay_auth.yaml')
    def test_endpoint_without_ebay_auth(self):
        response = self.client.get('/auth/authorize/')
        self.assertEqual(response.status_code, 200)

    @IntegrationTest.use_cassette('auth/test_endpoint_with_ebay_auth.yaml')
    def test_endpoint_with_ebay_auth(self):
        response = self.client.get('/products/1')
        self.assertEqual(response.status_code, 404)

        token = EbayTokenModel.create_from_ebay_token(EbayAuthenticatedAPITestCase.create_ebay_token())
        token.expiration_date = datetime(2000, 1, 1)
        token.save()
        self.account.token = token
        self.account.save()

        response = self.client.get('/products/1')
        # Token is expired
        self.assertEqual(response.status_code, 403)

        token.expiration_date = datetime(2100, 1, 1)
        token.save()

        response = self.client.get('/products/1')
        # 404 because product does not exists but no more 403!
        self.assertEqual(response.status_code, 404)
