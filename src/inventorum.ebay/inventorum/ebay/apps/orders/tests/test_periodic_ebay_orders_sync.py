# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.tests import CoreApiTest, EbayTest, MockedTest
from inventorum.ebay.apps.orders.ebay_orders_sync import PeriodicEbayOrdersSync
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory, EbayItemVariationFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class IntegrationTestPeriodicEbayOrdersSync(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(IntegrationTestPeriodicEbayOrdersSync, self).setUp()

        self.schedule_core_order_creation_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_core_order_creation")

    @MockedTest.use_cassette("ebay_orders_sync.yaml")
    def test_ebay_orders_sync(self):
        published_item = PublishedEbayItemFactory.create(external_id="261869293885")
        EbayItemVariationFactory.create(inv_id=1, item=published_item)
        EbayItemVariationFactory.create(inv_id=2, item=published_item)
        EbayItemVariationFactory.create(inv_id=3, item=published_item)
        EbayItemVariationFactory.create(inv_id=4, item=published_item)
        EbayItemVariationFactory.create(inv_id=5, item=published_item)

        sync = PeriodicEbayOrdersSync(account=self.account)
        sync.run()

        orders = OrderModel.objects.by_account(self.account)
        self.assertPostcondition(orders.count(), 5)

        for order in orders:
            self.assertIsNotNone(order.original_ebay_data)
