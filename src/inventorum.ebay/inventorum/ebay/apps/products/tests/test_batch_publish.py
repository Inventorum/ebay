# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
from inventorum.ebay.apps.accounts.tests import AccountTestMixin
import mock

from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.tests import StagingTestAccount, IntegrationTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestBatchPublish(EbayAuthenticatedAPITestCase, AccountTestMixin, ProductTestMixin):

    def setUp(self):
        super(TestBatchPublish, self).setUp()

        self.prepare_account_for_publishing(self.account)
        self.product_1 = self.get_valid_ebay_product_for_publishing(self.account,
                                                                    inv_id=StagingTestAccount.Products.IPAD_STAND)

    @IntegrationTest.use_cassette("publishing/test_batch_publishing_attempt_with_validation_errors.yaml")
    def test_batch_publishing_attempt_with_validation_errors(self):
        # remove category from product to trigger validation error
        self.product_1.category = None
        self.product_1.save()

        response = self.client.post('/products/publish', data=[
            {'product': str(self.product_1.inv_id)},
            {'product': str(StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING)},
        ])

        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['key'], 'multiple.errors')
        self.assertEqual(response.data['error']['detail'][self.product_1.inv_id], ['You need to select category'])
        self.assertEqual(response.data['error']['detail'][StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING],
                         ['Neither product or account have configured shipping services'])

    @mock.patch('inventorum.ebay.apps.products.resources.schedule_ebay_item_publish')
    @mock.patch('inventorum.ebay.apps.products.services.PublishingService.initialize_publish_attempt')
    @IntegrationTest.use_cassette("publishing/test_batch_publishing.yaml")
    def test_batch_publishing(self, schedule_ebay_item_publish_mock, initialize_publish_attempt_mock):
        product_2 = self.get_valid_ebay_product_for_publishing(account=self.account,
                                                               inv_id=StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING)
        response = self.client.post('/products/publish', data=[
            {'product': str(self.product_1.inv_id)},
            {'product': str(product_2.inv_id)},
        ])

        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(initialize_publish_attempt_mock.call_count, 2)
        self.assertEqual(schedule_ebay_item_publish_mock.call_count, 2)
