# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging
from inventorum.ebay.apps.notifications import EbayNotificationEventType
from inventorum.ebay.apps.notifications.fixtures import notification_templates
from inventorum.ebay.apps.notifications.tests import NotificationTestsMixin

from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory

from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from inventorum.util.celery import TaskExecutionContext


log = logging.getLogger(__name__)


class TestFixedPriceTransactionNotificationHandling(EbayAuthenticatedAPITestCase, NotificationTestsMixin):

    def setUp(self):
        super(TestFixedPriceTransactionNotificationHandling, self).setUp()

        self.schedule_ebay_orders_sync_mock = \
            self.patch("inventorum.ebay.apps.notifications.handlers.schedule_ebay_orders_sync")

    def test_item_sold_notification_handling(self):
        template = notification_templates.fixed_price_transaction_notification_template
        ebay_item_id = "12319491239"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id=ebay_item_id)
        self.assertPrecondition(published_item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.post_notification(EbayNotificationEventType.FixedPriceTransaction,
                               template=template,
                               item_id=ebay_item_id)

        self.assertEqual(self.schedule_ebay_orders_sync_mock.call_count, 1)
        self.schedule_ebay_orders_sync_mock\
            .assert_called_once_with(account_id=published_item.account.id,
                                     context=TaskExecutionContext(account_id=published_item.account.id,
                                                                  user_id=published_item.account.default_user.id,
                                                                  request_id=None))


class TestItemSoldNotificationHandling(EbayAuthenticatedAPITestCase, NotificationTestsMixin):

    def setUp(self):
        super(TestItemSoldNotificationHandling, self).setUp()

        self.schedule_ebay_orders_sync_mock = \
            self.patch("inventorum.ebay.apps.notifications.handlers.schedule_ebay_orders_sync")

    def test_item_sold_notification_handling(self):
        template = notification_templates.item_sold_notification_template
        ebay_item_id = "12319491239"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id=ebay_item_id)
        self.assertPrecondition(published_item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.post_notification(EbayNotificationEventType.ItemSold,
                               template=template,
                               item_id=ebay_item_id)

        self.assertEqual(self.schedule_ebay_orders_sync_mock.call_count, 1)
        self.schedule_ebay_orders_sync_mock\
            .assert_called_once_with(account_id=published_item.account.id,
                                     context=TaskExecutionContext(account_id=published_item.account.id,
                                                                  user_id=published_item.account.default_user.id,
                                                                  request_id=None))


class TestItemClosedNotificationHandling(EbayAuthenticatedAPITestCase, NotificationTestsMixin):

    def setUp(self):
        super(TestItemClosedNotificationHandling, self).setUp()

        self.schedule_core_api_publishing_status_update_mock = \
            self.patch("inventorum.ebay.apps.notifications.handlers.schedule_core_api_publishing_status_update")

    def test_item_closed_notification_handling(self):
        template = notification_templates.item_closed_notification_template
        ebay_item_id = "12319491239"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id=ebay_item_id)
        self.assertPrecondition(published_item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.post_notification(EbayNotificationEventType.ItemClosed,
                               template=template,
                               item_id=ebay_item_id)

        published_item = published_item.reload()
        self.assertEqual(published_item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)

        self.assertEqual(self.schedule_core_api_publishing_status_update_mock.call_count, 1)
        self.schedule_core_api_publishing_status_update_mock\
            .assert_called_once_with(ebay_item_id=published_item.id,
                                     context=TaskExecutionContext(account_id=self.account.id,
                                                                  user_id=self.account.default_user.id,
                                                                  request_id=None))


class TestItemSuspendedNotificationHandling(EbayAuthenticatedAPITestCase, NotificationTestsMixin):

    def setUp(self):
        super(TestItemSuspendedNotificationHandling, self).setUp()

        self.schedule_core_api_publishing_status_update_mock = \
            self.patch("inventorum.ebay.apps.notifications.handlers.schedule_core_api_publishing_status_update")

    def test_item_suspended_notification_handling(self):
        template = notification_templates.item_suspended_notification_template
        ebay_item_id = "12319491239"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id=ebay_item_id)
        self.assertPrecondition(published_item.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        self.post_notification(EbayNotificationEventType.ItemSuspended,
                               template=template,
                               item_id=ebay_item_id)

        published_item = published_item.reload()
        self.assertEqual(published_item.publishing_status, EbayItemPublishingStatus.FAILED)
        self.assertIn("suspended", json.dumps(published_item.publishing_status_details))

        self.assertEqual(self.schedule_core_api_publishing_status_update_mock.call_count, 1)
        self.schedule_core_api_publishing_status_update_mock\
            .assert_called_once_with(ebay_item_id=published_item.id,
                                     context=TaskExecutionContext(account_id=self.account.id,
                                                                  user_id=self.account.default_user.id,
                                                                  request_id=None))