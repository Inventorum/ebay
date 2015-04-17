# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.core_api.tests import CoreApiTestHelpers
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
from mock import PropertyMock
from rest_framework import status


log = logging.getLogger(__name__)


class IntegrationTestCoreAPISync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers):

    def xtest_integration(self):
        # Create some core products to play with
        product_1_inv_id = self.create_core_api_product(name="Test product 1", gross_price="1.99", quantity=12)
        product_2_inv_id = self.create_core_api_product(name="Test product 2", gross_price="3.45", quantity=5)
        product_3_inv_id = self.create_core_api_product(name="Test product 3", gross_price="9.99", quantity=100)

        # Map core products into ebay service
        ebay_product_1 = EbayProductModel.objects.create(inv_id=product_1_inv_id)
        ebay_product_2 = EbayProductModel.objects.create(inv_id=product_2_inv_id)
        ebay_product_3 = EbayProductModel.objects.create(inv_id=product_3_inv_id)

        # Publish some core products to ebay
        response = self.client.post("/products/%s/publish" % product_1_inv_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post("/products/%s/publish" % product_2_inv_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make some changes
        self.update_core_api_product(product_1_inv_id, {
            "gross_price": "1.99"
        })

        self.delete_core_api_product(product_2_inv_id)

        self.update_core_api_product(product_3_inv_id, {
            "gross_price"
        })


class UnitTestCoreAPISyncService(UnitTestCase):

    def setUp(self):
        self.account = EbayAccountFactory.create()
        type(self.account).core_api = PropertyMock(return_value=None)

    def test_empty_delta(self):
        self.account.core_api.get_paginated_product_delta_modified()
