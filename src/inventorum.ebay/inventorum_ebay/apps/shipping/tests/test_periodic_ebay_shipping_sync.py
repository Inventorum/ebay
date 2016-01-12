# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.apps.shipping.tasks import periodic_ebay_shipping_sync_task
from inventorum_ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestPeriodicShippingSync(UnitTestCase):

    @celery_test_case()
    def test_invokes_correct_service_methods(self):
        self.shipping_syncer = self.patch('inventorum_ebay.apps.shipping.tasks.EbayShippingScraper.scrape')

        periodic_ebay_shipping_sync_task.delay(context=get_anonymous_task_execution_context())

        self.assertEqual(self.shipping_syncer.call_count, 1)
