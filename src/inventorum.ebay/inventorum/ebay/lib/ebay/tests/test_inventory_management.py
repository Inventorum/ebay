# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.lib.ebay.inventorymanagement import EbayInventoryManagement
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayLocationAvailability, EbayAvailability
from inventorum.ebay.lib.ebay.tests.factories import EbayLocationFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestEbayInventoryManagement(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("ebay_test_inventory_management_all.yaml")
    def test_all(self):
        # Add location first
        location = EbayLocationFactory.build()

        api = EbayInventoryManagement(token=self.ebay_token)
        response = api.add_location(location=location)
        self.assertEqual(response.location_id.lower(), "test_inventorum_location")

        locations_availability = [
            EbayLocationAvailability(
                availability=EbayAvailability.IN_STOCK,
                location_id=location.location_id,
                quantity=10
            )
        ]
        response = api.add_inventory('test_sky', locations_availability=locations_availability)
        self.assertEqual(response.sku.lower(), 'test_sky')

        response = api.delete_inventory('test_sky', delete_all=True)
        self.assertEqual(response.sku.lower(), 'test_sky')

        response = api.delete_location(location.location_id)
        self.assertEqual(response.location_id.lower(), location.location_id)

    @EbayTest.use_cassette("ebay_test_add_inventory_to_non_existing_location.yaml")
    def test_add_inventory_to_non_existing_location(self):
        api = EbayInventoryManagement(token=self.ebay_token)

        locations_availability = [
            EbayLocationAvailability(
                availability=EbayAvailability.IN_STOCK,
                location_id="SOME_WIERD_NON_EXISTING_ID",
                quantity=10
            )
        ]
        # I dont know what I expected here, maybe ERROR because this location DOES NOT EXIST ... BUT NO!
        # Ebay has his own reasons and they accept this request....

        response = api.add_inventory('test_sky', locations_availability=locations_availability)
        self.assertEqual(response.sku.lower(), 'test_sky')