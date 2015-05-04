# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.core_api.tests import EbayTest
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.ebay.lib.ebay.data.events import EbayEventReadyForPickup
from inventorum.ebay.lib.ebay.events import EbayInboundEvents, EbayInboundEventsException
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from datetime import datetime

class TestEbayInboundEvents(EbayAuthenticatedAPITestCase):

    @EbayTest.use_cassette('ebay_event_ready_to_pickup_wrong_token.yaml')
    def test_ready_to_pickup(self):
        api = EbayInboundEvents(EbayToken('123', datetime.now()))

        event = EbayEventReadyForPickup(order_id='123')
        with self.assertRaises(EbayInboundEventsException) as exc:
            api.publish(event)
        self.assertEqual(exc.exception.message, "[ERROR] (code: 401001, domain: PINE) auth token is invalid.")

    @EbayTest.use_cassette('ebay_event_ready_to_pickup.yaml')
    def test_ready_to_pickup(self):
        api = EbayInboundEvents(self.ebay_token)

        event = EbayEventReadyForPickup(order_id='123')
        # It should not raise anything
        api.publish(event)