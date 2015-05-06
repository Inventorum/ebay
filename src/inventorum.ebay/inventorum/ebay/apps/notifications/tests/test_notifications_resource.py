# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from datetime import timedelta
from inventorum.ebay.apps.notifications.fixtures import notification_templates
from inventorum.ebay.apps.notifications.models import EbayNotificationModel

from inventorum.ebay.apps.notifications import EbayNotificationEventType, EbayNotificationStatus
from inventorum.ebay.apps.notifications.tests import NotificationTestsMixin
from inventorum.ebay.tests.testcases import APITestCase

from rest_framework import status


log = logging.getLogger(__name__)


class TestNotificationsResource(APITestCase, NotificationTestsMixin):

    NOTIFICATIONS = {
        EbayNotificationEventType.FixedPriceTransaction: notification_templates.fixed_price_transaction_notification_template,
        EbayNotificationEventType.ItemSold: notification_templates.item_sold_notification_template,
        EbayNotificationEventType.ItemClosed: notification_templates.item_closed_notification_template,
        EbayNotificationEventType.ItemSuspended: notification_templates.item_suspended_notification_template
    }

    def test_unhandled(self):
        for event_type, template in self.NOTIFICATIONS.iteritems():
            self.assertPrecondition(EbayNotificationModel
                                    .objects.filter(event_type=event_type,
                                                    status=EbayNotificationStatus.UNHANDLED).count(), 0)

            response = self.post_notification(event_type=event_type, template=template)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # notification should have been persisted and handled
            self.assertPostcondition(EbayNotificationModel
                                     .objects.filter(event_type=event_type,
                                                     status=EbayNotificationStatus.UNHANDLED).count(), 1)

    def test_invalid_signature(self):
        expired_timestamp = datetime.datetime.utcnow() - timedelta(minutes=15)
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          template=notification_templates.fixed_price_transaction_notification_template,
                                          timestamp=expired_timestamp)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        invalid_signature = "INVALID"
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          template=notification_templates.fixed_price_transaction_notification_template,
                                          signature=invalid_signature)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_payload(self):
        response = self.client.post("/notifications/", content_type='text/xml; charset="utf-8"',
                                    SOAPACTION=EbayNotificationEventType.FixedPriceTransaction,
                                    data="""<? echo "Invalid xml"; ?>""")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
