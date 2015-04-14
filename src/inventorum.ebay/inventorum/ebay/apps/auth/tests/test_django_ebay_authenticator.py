# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.tests.testcases import APITestCase, EbayAuthenticatedAPITestCase
from inventorum.util.django.timezone import datetime


class TestDjangoEbayAuthenticator(APITestCase):

    @APITestCase.vcr.use_cassette('auth_test_endpoint_without_ebay_auth.json')
    def test_endpoint_without_ebay_auth(self):
        response = self.client.get('/auth/authorize/')
        self.assertEqual(response.status_code, 200)

    @APITestCase.vcr.use_cassette('auth_test_endpoint_with_ebay_auth.json')
    def test_endpoint_with_ebay_auth(self):
        response = self.client.post('/products/1/publish')
        self.assertEqual(response.status_code, 403)

        token = EbayTokenModel.create_from_ebay_token(EbayAuthenticatedAPITestCase.ebay_token)
        token.expiration_date = datetime(2000, 1, 1)
        token.save()
        self.account.token = token
        self.account.save()

        response = self.client.post('/products/1/publish')
        # Token is expired
        self.assertEqual(response.status_code, 403)

        token.expiration_date = datetime(2100, 1, 1)
        token.save()

        response = self.client.post('/products/1/publish')
        # 404 because product does not exists but no more 403!
        self.assertEqual(response.status_code, 404)