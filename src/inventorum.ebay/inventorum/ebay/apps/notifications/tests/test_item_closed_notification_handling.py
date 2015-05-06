# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.notifications import EbayNotificationEventType
from inventorum.ebay.apps.notifications.fixtures import notification_templates
from inventorum.ebay.apps.notifications.fixtures.notification_templates import compile_notification_template

from inventorum.ebay.apps.notifications.tests import NotificationTestsMixin
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class IntegrationTestItemClosedNotificationHandling(EbayAuthenticatedAPITestCase):

    def post_notification(self, event_type, template, timestamp=None, signature=None, **kwargs):
        data = compile_notification_template(template, timestamp=timestamp, signature=signature, **kwargs)
        return self.client.post("/notifications/", content_type='text/xml; charset="utf-8"',
                                SOAPACTION=event_type, data=data)

    def test_item_closed_notification_handling(self):
        ebay_item_id = "12319491239"

        published_item = PublishedEbayItemFactory.create(external_id=ebay_item_id)
        self.assertPrecondition(published_item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.post_notification(EbayNotificationEventType.ItemClosed,
                               template=notification_templates.item_closed_notification_template,
                               item_id=ebay_item_id)

        published_item = published_item.reload()
        self.assertEqual(published_item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)
