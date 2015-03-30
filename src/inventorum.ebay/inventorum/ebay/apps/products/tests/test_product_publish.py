# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.products.models import EbayProductModel

from inventorum.ebay.tests.testcases import APITestCase


log = logging.getLogger(__name__)


class TestProductPublish(APITestCase):

    def test_first_time_publish(self):
        inv_product_id = 1
        assert not EbayProductModel.objects.by_inv_id(inv_product_id).exists()

        response = self.client.post("/products/%s/publish" % inv_product_id)
        self.assertEqual(response.status_code, 200)
