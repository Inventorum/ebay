# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import logging

from inventorum.ebay.tests import StagingTestAccount

from celery.exceptions import MaxRetriesExceededError
from inventorum.ebay.lib.core_api.tests import ApiTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.tasks import schedule_core_api_publishing_status_update
from inventorum.ebay.apps.products.tests.factories import EbayItemFactory
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.tests.testcases import APITestCase
from requests.exceptions import HTTPError


log = logging.getLogger(__name__)


class IntegrationTestCoreAPIPublishingStatusUpdate(APITestCase):

    @celery_test_case()
    def test_core_api_publishing_status_update(self):
        source_item = EbayItemFactory(product__inv_id=StagingTestAccount.Products.IPAD_STAND)

        with ApiTest.use_cassette("test_core_api_publishing_status_update.yaml", match_on=['body']) as cassette:
            source_item.set_publishing_status(publishing_status=EbayItemPublishingStatus.IN_PROGRESS)
            schedule_core_api_publishing_status_update(source_item.id, context=self.get_task_execution_context())

            source_item.set_publishing_status(publishing_status=EbayItemPublishingStatus.FAILED,
                                                 details={"message": "Oops, something went wrong!"})
            schedule_core_api_publishing_status_update(source_item.id, context=self.get_task_execution_context())

            source_item.set_publishing_status(publishing_status=EbayItemPublishingStatus.PUBLISHED)
            schedule_core_api_publishing_status_update(source_item.id, context=self.get_task_execution_context())

        requests = cassette.requests
        self.assertEqual(len(requests), 3)

        first_request = requests[0]
        self.assertTrue(first_request.uri.endswith("/api/products/{}/state/"
                                                   .format(StagingTestAccount.Products.IPAD_STAND)))
        self.assertEqual(json.loads(first_request.body), {"state": "in_progress", "details": {}, "channel": "ebay"})

        second_request = requests[1]
        self.assertTrue(second_request.uri.endswith("/api/products/{}/state/"
                                                    .format(StagingTestAccount.Products.IPAD_STAND)))
        self.assertEqual(json.loads(second_request.body), {"state": "failed",
                                                           "details": {"message": "Oops, something went wrong!"},
                                                           "channel": "ebay"})

        third_request = requests[2]
        self.assertTrue(third_request.uri.endswith("/api/products/{}/state/"
                                                   .format(StagingTestAccount.Products.IPAD_STAND)))
        self.assertEqual(json.loads(third_request.body), {"state": "published", "details": {}, "channel": "ebay"})

    @celery_test_case()
    def test_retrying(self):
        service_method = \
            "inventorum.ebay.apps.products.services.CorePublishingStatusUpdateService.update_publishing_status"
        service_method_mock = self.patch(service_method)
        service_method_mock.side_effect = HTTPError("Failed, should retry")

        source_item = EbayItemFactory(product__inv_id=StagingTestAccount.Products.IPAD_STAND)

        with self.assertRaises(MaxRetriesExceededError):
            schedule_core_api_publishing_status_update(source_item.id, context=self.get_task_execution_context())
