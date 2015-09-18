# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.lib.ebay.data.errors import EbayFatalError

import mock

from inventorum.ebay.apps.products.services import PublishingPreparationService
from inventorum.ebay.apps.products.tasks import schedule_ebay_item_publish
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.lib.celery import celery_test_case
from inventorum.ebay.tests import ApiTest, StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestPublishingTaskExceptionHandling(EbayAuthenticatedAPITestCase, ProductTestMixin):
    @ApiTest.use_cassette("test_publishing_task_exception_handling.yaml")
    @celery_test_case()
    @mock.patch('inventorum.ebay.apps.products.tasks.PublishingService.publish')
    def test_fatal_exception(self, publish_mock):
        publish_mock.side_effect = KeyError()

        product = self.get_valid_ebay_product_for_publishing(self.account)
        product.is_click_and_collect = True
        product.save()

        # Try to publish
        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()
        item = preparation_service.create_ebay_item()

        with self.assertRaises(KeyError):
            schedule_ebay_item_publish(ebay_item_id=item.id, context=self.get_task_execution_context())

        item = EbayItemModel.objects.get(id=item.id)
        self.assertEqual(item.publishing_status, "failed")

        error = item.publishing_status_details[0]
        self.assertEqual(error["long_message"], "Something went wrong, please try again later.")
        self.assertEqual(error["code"], EbayFatalError.CODE)
        self.assertEqual(error["severity_code"], "FatalError")
        self.assertEqual(error["classification"], "ApiError")
        self.assertTrue(error["short_message"].startswith('Fatal error ('))
