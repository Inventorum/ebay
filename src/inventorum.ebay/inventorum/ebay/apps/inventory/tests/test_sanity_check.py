# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from decimal import Decimal as D

from inventorum.ebay.tests import ApiTest, StagingTestAccount

from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from django.conf import settings


log = logging.getLogger(__name__)


class TestSanityCheck(EbayAuthenticatedAPITestCase):

    def test_sanity_check(self):
        with ApiTest.use_cassette("inventory_sanity_check.yaml") as cassette:
            SIMPLE_INV_PRODUCT_ID = 463690
            IPAD_STAND_PRODUCT_ID = 665753

            # product a with updated quantity
            item_a = PublishedEbayItemFactory.create(account=self.account,
                                                     product__account=self.account,
                                                     inv_product_id=SIMPLE_INV_PRODUCT_ID,
                                                     gross_price=D("3.99"),
                                                     quantity=79)

            locationID = settings.EBAY_LOCATION_ID_FORMAT.format(StagingTestAccount.ACCOUNT_ID)
            post_data = {
                "trackingUUID": "sadsadsadsadsad",
                "availabilities": [
                    {
                        "LocationID": locationID,
                        "sku": settings.EBAY_SKU_FORMAT.format(SIMPLE_INV_PRODUCT_ID),
                        "available": "IN_STOCK",
                        "quantity": 2000
                    },
                    {
                        "LocationID": locationID,
                        "sku": settings.EBAY_SKU_FORMAT.format(IPAD_STAND_PRODUCT_ID),
                        "available": "IN_STOCK",
                        "quantity": 10
                    }
                ],
            }

            response = self.client.post('/inventory/check/', data=post_data)
            log.info(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(response.data, {
                "trackingUUID": "sadsadsadsadsad",
                "availabilities": [
                    {
                        "LocationID": locationID,
                        "sku": settings.EBAY_SKU_FORMAT.format(SIMPLE_INV_PRODUCT_ID),
                        "available": "IN_STOCK",
                        "quantity": 1000
                    },
                    {
                        "LocationID": locationID,
                        "sku": settings.EBAY_SKU_FORMAT.format(IPAD_STAND_PRODUCT_ID),
                        "available": "OUT_OF_STOCK",
                        "quantity": 0
                    }
                ],
            })
