# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.categories.tasks import initialize_periodic_ebay_categories_sync_task
from inventorum.ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestPeriodicEbayCategoriesSync(UnitTestCase):

    @celery_test_case()
    def test_invokes_correct_service_methods(self):
        categories_syncer_mock = self.patch("inventorum.ebay.apps.categories.tasks.EbayCategoriesScraper.fetch_all")
        features_syncer_mock = self.patch("inventorum.ebay.apps.categories.tasks.EbayFeaturesScraper.fetch_all")
        specifics_syncer_mock = self.patch("inventorum.ebay.apps.categories.tasks.EbaySpecificsScraper.fetch_all")

        initialize_periodic_ebay_categories_sync_task.delay(context=get_anonymous_task_execution_context())

        self.assertEqual(categories_syncer_mock.call_count, 1)
        self.assertEqual(features_syncer_mock.call_count, 1)
        self.assertEqual(specifics_syncer_mock.call_count, 0)
