# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.apps.orders.ebay_orders_sync import EbayOrdersSync
from inventorum_ebay.apps.orders.tasks import schedule_ebay_orders_sync
from inventorum_ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context

from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase
from mock import Mock


log = logging.getLogger(__name__)


class UnitTestEbayOrdersSyncTask(EbayAuthenticatedAPITestCase):

    @celery_test_case()
    def test_basic_logic(self):
        self.ebay_orders_sync_ctor_mock = \
            self.patch("inventorum_ebay.apps.orders.ebay_orders_sync.EbayOrdersSync")

        self.ebay_orders_sync_mock = Mock(spec_set=EbayOrdersSync)
        self.ebay_orders_sync_ctor_mock.return_value = self.ebay_orders_sync_mock

        self.ebay_orders_sync_run_mock = \
            self.patch("inventorum_ebay.apps.orders.ebay_orders_sync.EbayOrdersSync.run", spec_set=EbayOrdersSync)

        schedule_ebay_orders_sync(account_id=self.account.id, context=get_anonymous_task_execution_context())

        self.assertEqual(self.ebay_orders_sync_ctor_mock.call_count, 1)
        self.ebay_orders_sync_ctor_mock.assert_called_once_with(self.account)

        self.assertEqual(self.ebay_orders_sync_mock.run.call_count, 1)
