# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal as D
from inventorum.ebay.apps.core_api.tests import ApiTest

from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestSanityCheck(EbayAuthenticatedAPITestCase):

    def test_published_modified_and_deleted(self):
        # product a with updated quantity
        product_a = EbayProductFactory.create(account=self.account, inv_id=1001)
        item_a = PublishedEbayItemFactory.create(account=self.account,
                                                 product=product_a,
                                                 gross_price=D("3.99"),
                                                 quantity=79)



    def test_sanity_check(self):
        with ApiTest.use_cassette("inventory_sanity_check.yaml") as cassette:
            # product a with updated quantity
            product_a = EbayProductFactory.create(account=self.account, inv_id=StagingTestAccount.Products.SIMPLE_PRODUCT_ID)
            item_a = PublishedEbayItemFactory.create(account=self.account,
                                                     product=product_a,
                                                     gross_price=D("3.99"),
                                                     quantity=79)

            post_data = {
                "trackingUUID": "sadsadsadsadsad",
                "availabilities": [
                    {
                        "LocationID": "Sunnyvale CA",
                        "sku": "invdev_{0}".format(StagingTestAccount.Products.SIMPLE_PRODUCT_ID),
                        "available": "IN_STOCK",
                        "quantity": 10
                    }, {
                    }],
                "LocationID": "San Jose CA",
                "sku": "SKU3421",
                "available": "IN_STOCK",
                "quantity": 10
            }

            response = self.client.post('/inventory/check/', data=post_data)
            self.assertEqual(response.status_code, 200)

