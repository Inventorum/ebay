# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.apps.accounts.tests import AccountTestMixin
from inventorum_ebay.apps.products.models import EbayItemModel
from inventorum_ebay.lib.ebay.data.errors import EbayFatalError

import mock

from inventorum_ebay.apps.products.services import PublishingPreparationService
from inventorum_ebay.apps.products.tasks import schedule_ebay_item_publish
from inventorum_ebay.apps.products.tests import ProductTestMixin
from inventorum_ebay.lib.celery import celery_test_case
from inventorum_ebay.tests import ApiTest, StagingTestAccount
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestPublishingTaskExceptionHandling(EbayAuthenticatedAPITestCase, AccountTestMixin, ProductTestMixin):
    @ApiTest.use_cassette("test_publishing_task_exception_handling.yaml")
    @celery_test_case()
    @mock.patch('inventorum_ebay.apps.products.tasks.PublishingService.publish')
    def test_fatal_exception(self, publish_mock):
        self.prepare_account_for_publishing(self.account)

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
