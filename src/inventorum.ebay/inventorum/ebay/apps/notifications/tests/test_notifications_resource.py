# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from datetime import timedelta
from inventorum.ebay.apps.notifications.fixtures import notification_templates
from inventorum.ebay.apps.notifications.fixtures.notification_templates import compile_notification_template
from inventorum.ebay.apps.notifications.models import EbayNotificationModel

from inventorum.ebay.apps.notifications import EbayNotificationEventType, EbayNotificationStatus
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory, EbayItemVariationFactory
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType
from inventorum.ebay.tests.testcases import APITestCase

from rest_framework import status


log = logging.getLogger(__name__)


class TestNotificationsResource(APITestCase):

    TEMPLATES = {
        EbayNotificationEventType.FixedPriceTransaction: notification_templates.fixed_price_transaction_notification_template,
        EbayNotificationEventType.ItemSold: notification_templates.item_sold_notification_template,
        EbayNotificationEventType.ItemClosed: notification_templates.item_closed_notification_template,
        EbayNotificationEventType.ItemSuspended: notification_templates.item_suspended_notification_template
    }

    def post_notification(self, event_type, data=None, timestamp=None, signature=None, **kwargs):
        if data is None:
            template = self.TEMPLATES[event_type]
            data = compile_notification_template(template, timestamp=timestamp, signature=signature, **kwargs)
        return self.client.post("/notifications/", content_type='text/xml; charset="utf-8"',
                                SOAPACTION=event_type, data=data)

    def test_valid_signature_and_payload(self):
        for event_type in self.TEMPLATES.keys():
            response = self.post_notification(event_type=event_type)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # notification should have been persisted and handled
            self.assertPostcondition(EbayNotificationModel
                                     .objects.filter(event_type=event_type,
                                                     status=EbayNotificationStatus.HANDLED).count(), 1)

    def test_invalid_signature(self):
        expired_timestamp = datetime.datetime.utcnow() - timedelta(minutes=15)
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          timestamp=expired_timestamp)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        invalid_signature = "INVALID"
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          signature=invalid_signature)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_payload(self):
        response = self.client.post("/notifications/", content_type='text/xml; charset="utf-8"',
                                    SOAPACTION=EbayNotificationEventType.FixedPriceTransaction,
                                    data="""<? echo "Invalid xml"; ?>""")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fixed_price_transaction(self):
        published_item = PublishedEbayItemFactory(external_id="1234")
        assert isinstance(published_item, EbayItemModel)

        self.assertPrecondition(published_item.order_line_items.count(), 0)

        event_type = EbayNotificationEventType.FixedPriceTransaction
        template = notification_templates.fixed_price_transaction_notification_template

        data = compile_notification_template(template, item_id="1234", item_title="Inventorum T-Shirt",
                                             transaction_id="5678", transaction_price="5.99", quantity_purchased=5,
                                             amount_paid="29.95", complete_status=CompleteStatusCodeType.Complete)

        response = self.post_notification(event_type=event_type, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertPostcondition(published_item.order_line_items.count(), 1)

        order_line_item = published_item.order_line_items.first()
        assert isinstance(order_line_item, OrderLineItemModel)

        self.assertEqual(order_line_item.quantity, 5)
        self.assertDecimal(order_line_item.unit_price, "5.99")

        order = order_line_item.order
        assert isinstance(order, OrderModel)

        self.assertEqual(order.ebay_id, "1234-5678")
        self.assertDecimal(order.final_price, "29.95")
        self.assertEqual(order.ebay_status, CompleteStatusCodeType.Complete)
        self.assertEqual(type(order.created_from), EbayNotificationModel)

    def test_fixed_price_transaction_for_variation(self):
        published_item = PublishedEbayItemFactory(external_id="1337")
        variation = EbayItemVariationFactory.create(item=published_item)

        event_type = EbayNotificationEventType.FixedPriceTransaction
        template = notification_templates.fixed_price_transaction_notification_template_for_variation

        data = compile_notification_template(template, item_id="1337", item_title="Inventorum T-Shirt",
                                             variation_sku="9999", variation_title="Inventorum T-Shirt [Blau, M]",
                                             transaction_id="1111", transaction_price="5.99", quantity_purchased=1,
                                             amount_paid="5.99", complete_status=CompleteStatusCodeType.Incomplete)

        response = self.post_notification(event_type=event_type, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
