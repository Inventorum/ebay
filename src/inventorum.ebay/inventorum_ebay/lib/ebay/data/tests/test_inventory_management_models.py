# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.lib.ebay.tests.factories import EbayLocationFactory
from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestEbayItems(UnitTestCase):

    def test_ebay_location_defaults_and_optionals(self):
        self.assertPrecondition(hasattr(EbayLocationFactory, "location_type"), False)

        location = EbayLocationFactory.create(address2=None, pickup_instruction=None, url=None)
        data = location.dict()

        # defaults
        self.assertTrue("LocationType" in data)
        self.assertEqual(data["LocationType"], "STORE")

        # optionals should not be included
        self.assertFalse("Address2" in data)
        self.assertFalse("PickupInstructions" in data)
        self.assertFalse("URL" in data)

        # set optionals
        location.address2 = "Test"
        location.pickup_instruction = "Better hurry, the pizza is getting cold"
        location.url = "http://example.com"

        data = location.dict()

        # optionals should be included now
        self.assertTrue("Address2" in data)
        self.assertEqual(data["Address2"], location.address2)

        self.assertTrue("PickupInstructions" in data)
        self.assertEqual(data["PickupInstructions"], location.pickup_instruction)

        self.assertTrue("URL" in data)
        self.assertEqual(data["URL"], location.url)
