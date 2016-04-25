# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.tests import Countries

import mock

from inventorum.ebay.apps.categories.tasks import ebay_category_specifics_sync_task
from inventorum.ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum.ebay.tests.testcases import APITestCase


class TestFetchSpecificsInBatches(APITestCase):

    @mock.patch('inventorum.ebay.apps.categories.services.EbaySpecificsScraper.fetch')
    @celery_test_case()
    def test_task_that_initialize_batches(self, fetch_mock):
        batches = []

        def fetch(qs, country):
            batches.append((country, qs.values_list('id', flat=True)))
        fetch_mock.side_effect = fetch

        for i in range(0, 45):
            CategoryFactory.create(country=Countries.DE, ebay_leaf=True)
            CategoryFactory.create(country=Countries.AT, ebay_leaf=True)

        # batches: 20, 20, 5 per each country so totally 6 batches
        ebay_category_specifics_sync_task.delay(context=get_anonymous_task_execution_context())

        self.assertEqual(len(batches), 6)

        # First 3 batches are for DE
        self.assertEqual(batches[0][0], 'DE')
        self.assertEqual(len(batches[0][1]), 20)

        self.assertEqual(batches[1][0], 'DE')
        self.assertEqual(len(batches[1][1]), 20)

        self.assertEqual(batches[2][0], 'DE')
        self.assertEqual(len(batches[2][1]), 5)

        # First 3 batches are for AT
        self.assertEqual(batches[3][0], 'AT')
        self.assertEqual(len(batches[3][1]), 20)

        self.assertEqual(batches[4][0], 'AT')
        self.assertEqual(len(batches[4][1]), 20)

        self.assertEqual(batches[5][0], 'AT')
        self.assertEqual(len(batches[5][1]), 5)
