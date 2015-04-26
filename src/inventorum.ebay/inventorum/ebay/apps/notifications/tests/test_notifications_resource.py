# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from datetime import timedelta
from inventorum.ebay.apps.notifications.tests import templates
from inventorum.ebay.apps.notifications.tests.templates import compile_notification_template
from inventorum.ebay.lib.ebay.notifications import EbayNotificationEventType, EbayNotification

from rest_framework import status
from rest_framework.test import APITestCase


log = logging.getLogger(__name__)


class TestNotificationsResource(APITestCase):

    TEMPLATES = {
        EbayNotificationEventType.FixedPriceTransaction: templates.FIXED_PRICE_TRANSACTION_NOTIFICATION
    }

    def post_notification(self, event_type, timestamp=None, signature=None, **kwargs):
        template = self.TEMPLATES[event_type]
        data = compile_notification_template(template, timestamp=timestamp, signature=signature, **kwargs)

        return self.client.post("/notifications/", content_type='text/xml; charset="utf-8"',
                                SOAPACTION=event_type, data=data)

    def test_valid_signature(self):
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_signature(self):
        expired_timestamp = datetime.datetime.utcnow() - timedelta(minutes=15)
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          timestamp=expired_timestamp)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        invalid_signature = "INVALID"
        response = self.post_notification(event_type=EbayNotificationEventType.FixedPriceTransaction,
                                          signature=invalid_signature)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
