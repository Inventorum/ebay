# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta

import mock

from inventorum.ebay.lib.celery import get_anonymous_task_execution_context
from inventorum.ebay.tests.testcases import UnitTestCase
from .. import EbayItemPublishingStatus
from ..tasks import synchronise_ebay_item_to_api
from ..models import EbayItemModel
from ..models import DirtynessRegistry
from .factories import EbayItemFactory


class TestItemDirtyness(UnitTestCase):

    def setUp(self):
        super(TestItemDirtyness, self).setUp()
        self.timeout = 300
        for i in range(5):
            EbayItemFactory.create()

    def test_new_items_are_registered(self):
        self.assertEqual(
            EbayItemModel.objects.all().count(),
            DirtynessRegistry.objects.get_for_model(EbayItemModel).count())

    def test_unregister(self):
        DirtynessRegistry.objects.unregister(EbayItemModel.objects.first())

        self.assertEqual(
            EbayItemModel.objects.all().count(),
            DirtynessRegistry.objects.all().count() + 1)

    def test_item_registered_when_publishing_status_changes(self):
        DirtynessRegistry.objects.all().delete()
        first = EbayItemModel.objects.first()
        first.publishing_status = EbayItemPublishingStatus.IN_PROGRESS
        first.save()

        dirty_qs = DirtynessRegistry.objects.all()

        self.assertEqual(dirty_qs.count(), 1)
        self.assertEqual(dirty_qs.first().object_id,
                         EbayItemModel.objects.first().pk)

    @mock.patch('inventorum.ebay.apps.products.tasks._finalize_ebay_item_publish.delay')
    def test_finalize_item_publish_is_called(self, finalize_ebay_item_publish_delay_mock):
        delta = datetime.now() - timedelta(seconds=self.timeout)

        selected_items = DirtynessRegistry.objects.all()[2:]
        ids = [item.object_id for item in selected_items]

        DirtynessRegistry.objects.filter(
            id__in=selected_items).update(created_at=delta)

        kwargs = dict(
            timeout=self.timeout,
            context=get_anonymous_task_execution_context())

        synchronise_ebay_item_to_api.apply(kwargs=kwargs)

        call_list = [args[0][0] for args in finalize_ebay_item_publish_delay_mock.call_args_list]

        self.assertEqual(call_list, ids)
