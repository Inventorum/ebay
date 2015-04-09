# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import unittest
from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.tests import StagingTestAccount

from inventorum.ebay.tests.testcases import APITestCase


log = logging.getLogger(__name__)


class TestProductPublish(APITestCase):

    @CoreApiTest.vcr.use_cassette("publish_product_resource_no_category.json")
    def test_publish_no_category(self):
        inv_product_id = StagingTestAccount.Products.SIMPLE_PRODUCT_ID
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertEqual(data, ['You need to select category'])
        
