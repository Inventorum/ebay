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
        self.product_1 = self.get_product(StagingTestAccount.Products.IPAD_STAND, self.account)
        self.assign_valid_shipping_services(self.product_1)

    def test_validate(self):
        with ApiTest.use_cassette("batch_publishing_test_validate.yaml"):
            response = self.client.post('/products/publish', data=[
                {'product': self.product_1.inv_id},
                {'product': StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING},
            ])

        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['key'], 'multiple.errors')
        self.assertEqual(response.data['error']['detail'][self.product_1.inv_id], ['You need to select category'])
        self.assertEqual(response.data['error']['detail'][StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING], ['Neither product or account have configured shipping '
                                                               'services'])

    @mock.patch('inventorum.ebay.apps.products.resources.schedule_ebay_item_publish')
    def test_publish(self, mock):
        product_2 = self.get_product(StagingTestAccount.Products.PRODUCT_VALID_FOR_PUBLISHING, self.account)
        self.assign_valid_shipping_services(self.product_1)
        self.assign_valid_shipping_services(product_2)

        self.assign_product_to_valid_category(self.product_1)
        self.assign_product_to_valid_category(product_2)

        with ApiTest.use_cassette("batch_publishing_test_publish.yaml"):
            response = self.client.post('/products/publish', data=[
                {'product': self.product_1.inv_id},
                {'product': product_2.inv_id},
            ])

        log.debug('Got response: %s', response)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(mock.call_count, 2)