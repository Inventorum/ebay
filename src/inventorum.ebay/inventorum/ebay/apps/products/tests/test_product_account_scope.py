# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.tests import ApiTest
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestProductAccountScope(EbayAuthenticatedAPITestCase):
    @ApiTest.use_cassette('test_product_from_different_account.yaml')
    def test_access_from_different_account(self):
        id_of_product_from_different_account = 1

        response = self.client.get('/products/{id}'.format(id=id_of_product_from_different_account))
        self.assertEqual(response.status_code, 404)

        self.assertEqual(EbayProductModel.objects.by_account(self.account).count(), 0)