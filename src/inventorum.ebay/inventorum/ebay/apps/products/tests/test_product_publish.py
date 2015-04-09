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

    @unittest.skip("To be done")
    @CoreApiTest.vcr.use_cassette("get_product_simple.json")
    def test_first_time_publish(self):
        inv_product_id = StagingTestAccount.Products.SIMPLE_PRODUCT_ID
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        response = self.client.post("/products/%s/publish" % inv_product_id)
        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)
        # core api product name, just to prove that the connection is working
        self.assertEqual(response.data, "XtC Advanced 2 LTD")
