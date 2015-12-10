# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from inventorum.ebay.apps.orders.services import CoreOrderService
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory, EbayAccountFactory
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory

from inventorum.ebay.tests import StagingTestAccount, MockedTest
from inventorum.ebay.tests.testcases import UnitTestCase


class TestCoreOrderService(UnitTestCase):

    @MockedTest.use_cassette("core_order_service_sync.yaml", record_mode="once")
    def test_core_order_serializer(self):
        account = EbayAccountFactory(
            inv_id=StagingTestAccount.ACCOUNT_ID,
        )
        EbayUserFactory.create(
            inv_id=StagingTestAccount.USER_ID,
            account=account,
        )
        order = OrderModelFactory.create(
            account=account,
        )

        OrderLineItemModelFactory.create(
            order=order,
            orderable_item__inv_product_id=StagingTestAccount.OrderableProducts.FAST_ROAD_COMAX,
            name="FastRoad CoMax",
            quantity=5
        )

        OrderLineItemModelFactory.create(
            order=order,
            orderable_item__inv_product_id=StagingTestAccount.OrderableProducts.XTC_ADVANCED_2_LTD,
            name="XtC Advanced 2 LTD",
            quantity=2
        )

        core_order_service = CoreOrderService(account)
        core_order_service.create_in_core_api(order)

        self.assertTrue(order.inv_id)
        self.assertTrue(order.line_items.count(), 2)
        self.assertTrue(all(order.line_items.values_list('inv_id', flat=True)))
