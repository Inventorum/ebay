# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
import mock
from datetime import datetime, timedelta

from inventorum.ebay.lib.celery import get_anonymous_task_execution_context
from inventorum.ebay.tests.testcases import UnitTestCase
from ..tasks import periodic_ebay_timeouted_item_check_task
from .. import EbayItemPublishingStatus
from ..models import EbayItemModel
from .factories import EbayItemFactory


log = logging.getLogger(__name__)


class TestDelayedItemsPublishingGetsFinalized(UnitTestCase):

    def setUp(self):
        super(TestDelayedItemsPublishingGetsFinalized, self).setUp()
        self.timeout = 300

        self._make_items()
        self._make_items(timeout=self.timeout)

    def _make_items(self, count=5, timeout=0):
        items = []
        for counter in range(count):
            item = EbayItemFactory.create(publishing_status=EbayItemPublishingStatus.IN_PROGRESS)
            items.append(item.id)

        if timeout:
            delay = datetime.now() - timedelta(seconds=timeout)
            EbayItemModel.objects.filter(pk__in=items).update(time_added=delay)

    @mock.patch('inventorum.ebay.apps.products.tasks.synchronise_ebay_item_to_api.delay')
    def test_delayed_publishing_made_failed(self, synchronise_ebay_item_to_api):
        kwargs = dict(
            timeout=self.timeout,
            context=get_anonymous_task_execution_context())

        periodic_ebay_timeouted_item_check_task.apply(kwargs=kwargs)

        failed_items = EbayItemModel.objects.filter(
            publishing_status=EbayItemPublishingStatus.FAILED)

        self.assertEqual(failed_items.count(), 5)
        self.assertEqual(failed_items.first().publishing_status_details,
                         dict(message='Publishing timeout ({} seconds).'.format(self.timeout)))
        self.assertEqual(synchronise_ebay_item_to_api.call_count, 5)

        call_list = [args[0][0] for args in synchronise_ebay_item_to_api.call_args_list]

        self.assertEqual(set(call_list), set(failed_items.values_list('pk', flat=True)))
