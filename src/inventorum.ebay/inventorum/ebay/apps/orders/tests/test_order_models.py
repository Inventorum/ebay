# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum.ebay.apps.orders.models import OrderFactory, OrderStatusModel
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType
from inventorum.ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestOrderFactory(UnitTestCase):

    def test_creates_related_status_models(self):
        # create order with required attributes
        order = OrderFactory.create(account=EbayAccountFactory.create(),
                                    ebay_id="SOME_EBAY_ID",
                                    ebay_complete_status=CompleteStatusCodeType.Complete)

        # factory should automatically create related status models
        self.assertIsInstance(order.core_status, OrderStatusModel)
        self.assertIsInstance(order.ebay_status, OrderStatusModel)

        core_status = OrderStatusModel.objects.create()
        ebay_status = OrderStatusModel.objects.create()
        another_order = OrderFactory.create(account=order.account,
                                            ebay_id="ANOTHER_EBAY_ID",
                                            ebay_complete_status=CompleteStatusCodeType.Pending,
                                            core_status=core_status,
                                            ebay_status=ebay_status)

        # factory should not have overwritten the given related status models
        self.assertEqual(another_order.core_status, core_status)
        self.assertEqual(another_order.ebay_status, ebay_status)


class TestOrderStatusModel(UnitTestCase):

    def test_regular_states(self):
        order = OrderModelFactory.create()
        self.assertPrecondition(order.is_click_and_collect, False)

        self.assertFalse(order.core_status.is_paid)
        self.assertFalse(order.core_status.is_shipped)
        self.assertFalse(order.core_status.is_closed)
        self.assertFalse(order.core_status.is_canceled)

        self.assertFalse(order.ebay_status.is_paid)
        self.assertFalse(order.ebay_status.is_shipped)
        self.assertFalse(order.ebay_status.is_closed)
        self.assertFalse(order.ebay_status.is_canceled)

    def test_click_and_collect_states(self):
        account = EbayAccountFactory.create()
        click_and_collect_order = OrderModelFactory.create(
            account=account,
            selected_shipping__service=ShippingServiceModel.get_click_and_collect_service(country=account.country))
        self.assertPrecondition(click_and_collect_order.is_click_and_collect, True)

        self.assertFalse(click_and_collect_order.core_status.is_ready_for_pickup)
        self.assertFalse(click_and_collect_order.core_status.is_picked_up)
        self.assertFalse(click_and_collect_order.ebay_status.is_ready_for_pickup)
        self.assertFalse(click_and_collect_order.ebay_status.is_picked_up)

        click_and_collect_order.core_status.is_shipped = True
        self.assertTrue(click_and_collect_order.core_status.is_ready_for_pickup)

        click_and_collect_order.ebay_status.is_closed = True
        click_and_collect_order.ebay_status.is_delivered = True
        self.assertTrue(click_and_collect_order.ebay_status.is_picked_up)
