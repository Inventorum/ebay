# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging
import mock

from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.tests import StagingTestAccount, ApiTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestBatchPublish(EbayAuthenticatedAPITestCase, ProductTestMixin):

    def setUp(self):
        super(TestBatchPublish, self).setUp()

        self.product_1 = self.get_valid_ebay_product_for_publishing(self.account,
                                                                    inv_id=StagingTestAccount.Products.IPAD_STAND)

    def test_validate(self):
        # remove category from product to trigger validation error
        self.product_1.category = None
        self.product_1.save()

        with ApiTest.use_cassette("batch_publishing_test_validate.yaml"):
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
    def test_publish(self, schedule_ebay_item_publish_mock, initialize_publish_attempt_mock):
        product_2 = self.get_valid_ebay_product_for_publishing(account=self.account,
                                                               inv_id=StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING)

        with ApiTest.use_cassette("batch_publishing_test_publish.yaml"):
            response = self.client.post('/products/publish', data=[
                {'product': str(self.product_1.inv_id)},
                {'product': str(product_2.inv_id)},
            ])

        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(initialize_publish_attempt_mock.call_count, 2)
        self.assertEqual(schedule_ebay_item_publish_mock.call_count, 2)
