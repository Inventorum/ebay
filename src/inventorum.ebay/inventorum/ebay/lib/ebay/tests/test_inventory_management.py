# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from inventorum.ebay.apps.core_api.tests import EbayTest
from inventorum.ebay.lib.ebay.clickcollect import EbayInventoryManagement
from inventorum.ebay.lib.ebay.data.inventorymanagement import EbayLocation, EbayDay, EbayInterval
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestEbayInventoryManagement(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("ebay_test_inventory_management_all.yaml")
    def test_all(self):
        # Add location first
        intervals = [
            EbayInterval(
                open='08:00:00',
                close='10:00:00'
            )
        ]

        days = [
            EbayDay(
                day_of_week=1,
                intervals=intervals
            )
        ]

        location = EbayLocation(
            location_id="test_inventorum_location",
            address1="Voltrastr 5",
            address2="Gebaude 2",
            city="Berlin",
            country="DE",
            days=days,
            latitude=Decimal("37.374488"),
            longitude=Decimal("-122.032876"),
            name="Test location Inventorum",
            phone="072 445 78 75",
            pickup_instruction="Pick it up as soon as possible",
            postal_code="13355",
            region="Berlin",
            url="http://inventorum.com",
            utc_offset="+02:00"
        )

        api = EbayInventoryManagement(token=self.ebay_token)
        response = api.add_location(location=location)
        self.assertEqual(response.location_id.lower(), "test_inventorum_location")