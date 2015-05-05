# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from datetime import datetime, timedelta
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.apps.core_api.tests import MockedTest
from inventorum.ebay.apps.orders.ebay_orders_sync import PeriodicEbayOrdersSync
from inventorum.ebay.apps.orders.models import OrderModel
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory, EbayItemVariationFactory
from inventorum.ebay.apps.shipping import INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.ebay.data.tests.factories import OrderTypeFactory, GetOrdersResponseTypeFactory
from inventorum.ebay.lib.ebay.tests.factories import EbayTokenFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase


log = logging.getLogger(__name__)


class IntegrationTestPeriodicEbayOrdersSync(EbayAuthenticatedAPITestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(IntegrationTestPeriodicEbayOrdersSync, self).setUp()

        # TODO jm: unmock and record when api is ready
        self.schedule_core_order_creation_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_core_order_creation")

    @MockedTest.use_cassette("ebay_orders_sync.yaml")
    def test_ebay_orders_sync(self):
        # create published item with variations that are included in the response cassette
        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id="261869293885")
        EbayItemVariationFactory.create(inv_id=1, item=published_item)
        EbayItemVariationFactory.create(inv_id=2, item=published_item)
        EbayItemVariationFactory.create(inv_id=3, item=published_item)
        EbayItemVariationFactory.create(inv_id=4, item=published_item)
        EbayItemVariationFactory.create(inv_id=5, item=published_item)
        # create shipping service that is selected in the response cassette
        dhl_shipping = self.get_shipping_service_dhl()

        sync = PeriodicEbayOrdersSync(account=self.account)
        sync.run()

        orders = OrderModel.objects.by_account(self.account)
        self.assertPostcondition(orders.count(), 5)

        for order in orders:
            self.assertIsNotNone(order.original_ebay_data)

    @MockedTest.use_cassette("ebay_orders_sync_click_and_collect.yaml")
    def test_ebay_orders_sync(self):
        # create published item with variations that are included in the response cassette
        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id="261869293885")
        EbayItemVariationFactory.create(inv_product_id=1, item=published_item)
        EbayItemVariationFactory.create(inv_product_id=2, item=published_item)
        EbayItemVariationFactory.create(inv_product_id=3, item=published_item)
        EbayItemVariationFactory.create(inv_product_id=4, item=published_item)
        EbayItemVariationFactory.create(inv_product_id=5, item=published_item)
        # create shipping service that is selected in the response cassette
        dhl_shipping = self.get_shipping_service_dhl()

        sync = PeriodicEbayOrdersSync(account=self.account)
        sync.run()

        orders = OrderModel.objects.by_account(self.account)
        self.assertPostcondition(orders.count(), 5)

        for order in orders:
            self.assertIsNotNone(order.original_ebay_data)

        first_order = OrderModel.objects.by_account(self.account).first()
        self.assertEqual(first_order.selected_shipping.service.external_id, INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID)
        self.assertTrue(first_order.is_click_and_collect)


class UnitTestPeriodicEbayOrdersSync(UnitTestCase):

    def setUp(self):
        super(UnitTestPeriodicEbayOrdersSync, self).setUp()

        # ebay-authenticated account with default user
        ebay_token = EbayTokenFactory.create()
        self.account = EbayAccountFactory.create(token=EbayTokenModel.create_from_ebay_token(ebay_token))
        self.default_user = EbayUserFactory.create(account=self.account)

        self.incoming_ebay_order_sync_mock = \
            self.patch("inventorum.ebay.apps.orders.ebay_orders_sync.IncomingEbayOrderSyncer.__call__")

        self.ebay_api_get_orders_mock = \
            self.patch("inventorum.ebay.lib.ebay.orders.EbayOrders.get_orders")

    def expect_ebay_orders(self, orders):
        """
        :type orders: list[inventorum.ebay.lib.ebay.data.responses.OrderType]
        """
        get_orders_response = GetOrdersResponseTypeFactory.create(
            pagination_result__total_number_of_entries=len(orders),
            orders=orders
        )
        self.ebay_api_get_orders_mock.return_value = get_orders_response

    def test_basic_logic_with_empty_orders(self):
        assert self.account.last_ebay_orders_sync is None

        self.expect_ebay_orders([])

        subject = PeriodicEbayOrdersSync(account=self.account)
        subject.run()

        self.assertFalse(self.incoming_ebay_order_sync_mock.called)
        self.assertTrue(self.ebay_api_get_orders_mock.called)

        self.ebay_api_get_orders_mock.assert_called_once_with({
            "OrderStatus": "Completed",
            "OrderRole": "Seller",
            "ModTimeFrom": EbayParser.format_date(self.account.time_added),
            "Pagination": {
                "EntriesPerPage": 100
            }
        })

        # next sync for the account should start from last_ebay_orders_sync
        self.ebay_api_get_orders_mock.reset_mock()
        self.expect_ebay_orders([])

        self.assertIsNotNone(self.account.last_ebay_orders_sync)
        self.assertTrue(datetime.utcnow() - self.account.last_ebay_orders_sync < timedelta(seconds=1))

        # reload changes from database
        self.account = self.account.reload()

        last_ebay_orders_sync = self.account.last_ebay_orders_sync

        subject = PeriodicEbayOrdersSync(account=self.account)
        subject.run()

        self.ebay_api_get_orders_mock.assert_called_once_with({
            "OrderStatus": "Completed",
            "OrderRole": "Seller",
            "ModTimeFrom": EbayParser.format_date(last_ebay_orders_sync),
            "Pagination": {
                "EntriesPerPage": 100
            }
        })

    def test_syncs_incoming_ebay_orders(self):
        order_1 = OrderTypeFactory.create(order_id="1")
        order_2 = OrderTypeFactory.create(order_id="2")

        self.expect_ebay_orders([order_1, order_2])

        subject = PeriodicEbayOrdersSync(account=self.account)
        subject.run()

        self.assertEqual(self.incoming_ebay_order_sync_mock.call_count, 2)

        self.incoming_ebay_order_sync_mock.assert_any_call(order_1)
        self.incoming_ebay_order_sync_mock.assert_any_call(order_2)
