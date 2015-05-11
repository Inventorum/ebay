# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestInventoryManagementWeirdErrors(EbayAuthenticatedAPITestCase):
    def test_add_location_error(self):
        ebay = EbayInventoryManagement(self.ebay_token)
        self.add