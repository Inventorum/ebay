# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime

from inventorum.ebay.apps.core_api.tests import EbayTest
from inventorum.ebay.lib.ebay.data.authorization import EbayToken
from inventorum.ebay.lib.ebay.data.events import EbayEventReadyForPickup, EbayEventPickedUp, EbayEventCanceled
from inventorum.ebay.lib.ebay.events import EbayInboundEvents, EbayInboundEventsException
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestEbayInboundEvents(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette('ebay_event_ready_to_pickup_wrong_token.yaml')
    def test_ready_to_pickup_failing(self):
        api = EbayInboundEvents(EbayToken('123', datetime.now()))

        event = EbayEventReadyForPickup(order_id='123')
        with self.assertRaises(EbayInboundEventsException) as exc:
            api.publish(event)
        self.assertEqual(exc.exception.message, "[ERROR] (code: 401001, domain: PINE) auth token is invalid.")

    def test_ready_to_pickup(self):
        api = EbayInboundEvents(self.ebay_token)

        # Btw, my opinion is that this should return 404 or something cause this order does not exist, but
        # who am I to argue with ebay ?
        event = EbayEventReadyForPickup(order_id='123')

        # Return 200, so accepted by ebay.
        with EbayTest.use_cassette('ebay_event_ready_to_pickup.yaml') as cass:
            api.publish(event)

        first_request = cass.requests[0]
        data = json.loads(first_request.body)
        self.assertDictEqual(data, {
            'event': {
                'notifierReferenceId': 'test',
                'payload': {
                    'ebayOrderId': '123'
                },
                'type': 'EBAY.ORDER.READY_FOR_PICKUP',
                'version': '1.0'
            }})

    def test_picked_up(self):
        api = EbayInboundEvents(self.ebay_token)

        # Btw, my opinion is that this should return 404 or something cause this order does not exist, but
        # who am I to argue with ebay ?
        event = EbayEventPickedUp(order_id='123')

        # Return 200, so accepted by ebay.
        with EbayTest.use_cassette('ebay_event_pickedup.yaml') as cass:
            api.publish(event)

        first_request = cass.requests[0]
        data = json.loads(first_request.body)
        self.assertDictEqual(data, {
            'event': {
                'notifierReferenceId': 'test',
                'payload': {
                    'ebayOrderId': '123'
                },
                'type': 'EBAY.ORDER.PICKEDUP',
                'version': '1.0'
            }})

    def test_canceled(self):
        api = EbayInboundEvents(self.ebay_token)

        # Btw, my opinion is that this should return 404 or something cause this order does not exist, but
        # who am I to argue with ebay ?
        event = EbayEventCanceled(order_id='123',
                                  cancellation_type=EbayEventCanceled.CancellationType.OUT_OF_STOCK)

        # Return 200, so accepted by ebay.
        with EbayTest.use_cassette('ebay_event_canceled.yaml') as cass:
            api.publish(event)

        first_request = cass.requests[0]
        data = json.loads(first_request.body)
        self.assertDictEqual(data, {
            'event': {
                'notifierReferenceId': 'test',
                'payload': {
                    'ebayOrderId': '123',
                    'notifierCancelType': 'OUT_OF_STOCK',
                    'notifierRefundType': 'EBAY'
                },
                'type': 'EBAY.ORDER.PICKUP_CANCELED',
                'version': '1.0'
            }})