# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.core_api.tests import EbayTest
from inventorum.ebay.lib.ebay import EbayConnectionException
from inventorum.ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from inventorum.ebay.lib.ebay.tests.factories import EbayLocationFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestInventoryManagementWeirdErrors(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("ebay_test_inventory_adding_location_weird_errors.yaml")
    def test_add_location_error(self):
        api = EbayInventoryManagement(self.ebay_token)
        location = EbayLocationFactory.build()
        with self.assertRaises(EbayConnectionException) as exc:
            response = api.add_location(location=location)

        self.assertEqual(exc.exception.message, "AddInventoryLocation: Bad Gateway, Class: RequestError, Severity: "
                                                "Error, Code: 99.99, Gateway Error Failover endpoint : "
                                                "Selling_Inventory_REST_SVC_V1 - no ready child endpoints")