# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal as D
from datetime import datetime, timedelta

from inventorum.ebay.lib.celery import celery_test_case, get_anonymous_task_execution_context
from inventorum.ebay.lib.core_api.tests import CoreApiTestHelpers
from inventorum.ebay.lib.ebay.data import EbayParser, OrderStatusCodeType, PaymentStatusCodeType, \
    BuyerPaymentMethodCodeType
from inventorum.ebay.lib.ebay.data.tests.factories import OrderTypeFactory, GetOrdersResponseTypeFactory, \
    TransactionTypeWithVariationFactory, TransactionTypeFactory
from inventorum.ebay.lib.ebay.tests.factories import EbayTokenFactory

from inventorum.ebay.tests import MockedTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase

from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.accounts.models import AddressModel

from inventorum.ebay.apps.auth.models import EbayTokenModel

from inventorum.ebay.apps.products.models import EbayItemVariationModel, EbayItemModel
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory, EbayItemVariationFactory

from inventorum.ebay.apps.shipping import INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin

from inventorum.ebay.apps.orders import CorePaymentMethod
from inventorum.ebay.apps.orders.ebay_orders_sync import EbayOrdersSync, IncomingEbayOrderSyncer, EbayOrderSyncException
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.orders.serializers import OrderCustomerCoreAPIDataSerializer
from inventorum.ebay.apps.orders.tasks import periodic_ebay_orders_sync_task
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory


log = logging.getLogger(__name__)


class IntegrationTestPeriodicEbayOrdersSync(EbayAuthenticatedAPITestCase, CoreApiTestHelpers, ShippingServiceTestMixin):

    def setUp(self):
        super(IntegrationTestPeriodicEbayOrdersSync, self).setUp()

        # In cassettes, we match on body, so we have to take the random part out of random :-)
        generate_random_mock = self.patch("inventorum.ebay.apps.orders.models.OrderModel.generate_unique_pickup_code")
        not_so_random = "123456"
        generate_random_mock.return_value = not_so_random

    @celery_test_case()
    @MockedTest.use_cassette("ebay_orders_sync.yaml", record_mode="once", match_on=['body'])
    def test_ebay_orders_sync(self):
        # ensure constant sync start since we're matching on body with vcr
        self.account.last_ebay_orders_sync = EbayParser.parse_date("2015-04-25T12:16:11.257939Z")
        self.account.save()

        # create published item with variations that are included in the response cassette
        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         product__account=self.account,
                                                         external_id="261869293885")
        EbayItemVariationFactory.create(inv_product_id=670339, item=published_item)

        # create shipping service that is selected in the response cassette
        self.get_shipping_service_dhl()

        periodic_ebay_orders_sync_task.delay(context=get_anonymous_task_execution_context())

        orders = OrderModel.objects.by_account(self.account)
        self.assertPostcondition(orders.count(), 5)

        for order in orders:
            self.assertIsNotNone(order.inv_id)
            self.assertIsNotNone(order.original_ebay_data)

            self.assertEqual(order.line_items.count(), 1)

            order_line_item = order.line_items.first()
            self.assertIsNotNone(order_line_item.inv_id)

    @celery_test_case()
    @MockedTest.use_cassette("ebay_orders_sync_click_and_collect.yaml", record_mode="once", match_on=['body'])
    def test_ebay_orders_click_and_collect_sync(self):
        # ensure constant sync start since we're matching on body with vcr
        self.account.last_ebay_orders_sync = EbayParser.parse_date("2015-04-25T12:16:11.257939Z")
        self.account.save()

        # create published item with variations that are included in the response cassette
        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         product__account=self.account,
                                                         external_id="261869293885")
        EbayItemVariationFactory.create(inv_product_id=670339, item=published_item)
        # create shipping service that is selected in the response cassette
        self.get_shipping_service_dhl()

        periodic_ebay_orders_sync_task.delay(context=get_anonymous_task_execution_context())

        orders = OrderModel.objects.by_account(self.account)
        self.assertPostcondition(orders.count(), 5)

        for order in orders:
            self.assertIsNotNone(order.inv_id)
            self.assertIsNotNone(order.original_ebay_data)

        first_order = OrderModel.objects.by_account(self.account).first()
        self.assertEqual(first_order.selected_shipping.service.external_id, INV_CLICK_AND_COLLECT_SERVICE_EXTERNAL_ID)
        self.assertTrue(first_order.is_click_and_collect)


class UnitTestEbayOrdersSync(UnitTestCase):

    def setUp(self):
        super(UnitTestEbayOrdersSync, self).setUp()

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

        subject = EbayOrdersSync(account=self.account)
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

        subject = EbayOrdersSync(account=self.account)
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

        subject = EbayOrdersSync(account=self.account)
        subject.run()

        self.assertEqual(self.incoming_ebay_order_sync_mock.call_count, 2)

        self.incoming_ebay_order_sync_mock.assert_any_call(order_1)
        self.incoming_ebay_order_sync_mock.assert_any_call(order_2)

    def test_sync_error_handling(self):
        self.assertPrecondition(self.account.last_ebay_orders_sync, None)
        self.assertPrecondition(OrderModel.objects.count(), 0)

        order_1 = OrderTypeFactory.create(order_id="1")
        order_2 = OrderTypeFactory.create(order_id="2")

        self.expect_ebay_orders([order_1, order_2])

        self.incoming_ebay_order_sync_mock.side_effect = EbayOrderSyncException("Oops, something went wrong")

        subject = EbayOrdersSync(account=self.account)
        subject.run()

        # should not update last sync time
        self.assertIsNone(self.account.last_ebay_orders_sync)


class UnitTestEbayOrderSyncer(UnitTestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(UnitTestEbayOrderSyncer, self).setUp()

        self.account = EbayAccountFactory.create()
        self.default_user = EbayUserFactory.create(account=self.account)

        self.schedule_core_order_creation_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_core_order_creation")

        self.assertPrecondition(OrderModel.objects.count(), 0)

    def test_new_icoming_order_with_invalid_request_in_buyer_email(self):
        incoming_order = OrderModelFactory.create(
            buyer_email='Invalid Request'
        )
        serialized_data = OrderCustomerCoreAPIDataSerializer(instance=incoming_order).data
        self.assertIsNone(serialized_data['email'])

    def test_new_incoming_order_for_non_variation_listing(self):
        published_ebay_item_id = "123456789"
        transaction_id = "987654321"
        order_id = "123456789-987654321"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         tax_rate=D("7.000"),
                                                         external_id=published_ebay_item_id)

        shipping_service_dhl = self.get_shipping_service_dhl()

        incoming_order = OrderTypeFactory.create(
            order_id=order_id,
            order_status=OrderStatusCodeType.Completed,
            subtotal=D("7.98"),
            total=D("12.88"),
            amount_paid=D("12.88"),
            checkout_status__payment_method="PayPal",
            checkout_status__payment_status=PaymentStatusCodeType.NoPaymentFailure,

            transactions=[
                TransactionTypeFactory.create(
                    transaction_id=transaction_id,
                    item__item_id=published_ebay_item_id,
                    item__title="Inventorum iPad Stand",
                    quantity_purchased=2,
                    transaction_price=D("3.99"),
                    buyer__email="test@inventorum.com",
                    buyer__user_first_name="John",
                    buyer__user_last_name="Newman"
                )
            ],

            shipping_address__name="Max Mustermann",
            shipping_address__street_1="Voltastraße 5",
            shipping_address__postal_code="13355",
            shipping_address__city_name="Berlin",
            shipping_address__state_or_province="Wedding",
            shipping_address__country="DE",

            shipping_service_selected__shipping_service=shipping_service_dhl.external_id,
            shipping_service_selected__shipping_cost=D("4.90")
        )

        sync = IncomingEbayOrderSyncer(account=self.account)
        sync(incoming_order)

        # syncer should have created a new order model
        self.assertPostcondition(OrderModel.objects.count(), 1)

        order_model = OrderModel.objects.first()
        assert isinstance(order_model, OrderModel)

        self.assertEqual(order_model.account, self.account)
        self.assertEqual(order_model.ebay_id, order_id)
        self.assertEqual(order_model.ebay_complete_status, OrderStatusCodeType.Completed)
        self.assertEqual(order_model.created_in_core_api, False)

        self.assertEqual(order_model.buyer_first_name, "John")
        self.assertEqual(order_model.buyer_last_name, "Newman")
        self.assertEqual(order_model.buyer_email, "test@inventorum.com")

        self.assertIsNotNone(order_model.shipping_address)
        shipping_address = order_model.shipping_address
        assert isinstance(shipping_address, AddressModel)
        # shipping name should have been correctly split into first and last name
        self.assertEqual(shipping_address.first_name, "Max")
        self.assertEqual(shipping_address.last_name, "Mustermann")
        self.assertEqual(shipping_address.street, "Voltastraße 5")
        self.assertEqual(shipping_address.street1, None)
        self.assertEqual(shipping_address.postal_code, "13355")
        self.assertEqual(shipping_address.city, "Berlin")
        self.assertEqual(shipping_address.region, "Wedding")
        self.assertEqual(shipping_address.country, "DE")

        # billing address should equal shipping address with buyer name
        self.assertIsNotNone(order_model.billing_address)
        billing_address = order_model.billing_address
        assert isinstance(billing_address, AddressModel)
        self.assertEqual(billing_address.first_name, "John")
        self.assertEqual(billing_address.last_name, "Newman")
        self.assertEqual(billing_address.street, "Voltastraße 5")
        self.assertEqual(billing_address.street1, None)
        self.assertEqual(billing_address.postal_code, "13355")
        self.assertEqual(billing_address.city, "Berlin")
        self.assertEqual(billing_address.region, "Wedding")
        self.assertEqual(billing_address.country, "DE")

        self.assertIsNotNone(order_model.selected_shipping)
        selected_shipping = order_model.selected_shipping
        assert isinstance(selected_shipping, ShippingServiceConfigurationModel)
        self.assertEqual(selected_shipping.service_id, shipping_service_dhl.id)
        self.assertEqual(selected_shipping.cost, D("4.90"))
        self.assertEqual(selected_shipping.additional_cost, D("0.00"))

        self.assertEqual(order_model.subtotal, D("7.98"))
        self.assertEqual(order_model.total, D("12.88"))

        self.assertEqual(order_model.payment_amount, D("12.88"))
        self.assertEqual(order_model.payment_method, CorePaymentMethod.PAYPAL)
        self.assertEqual(order_model.ebay_payment_method, BuyerPaymentMethodCodeType.PayPal)
        self.assertEqual(order_model.ebay_payment_status, PaymentStatusCodeType.NoPaymentFailure)

        self.assertEqual(order_model.line_items.count(), 1)

        line_item = order_model.line_items.first()
        assert isinstance(line_item, OrderLineItemModel)

        self.assertEqual(line_item.ebay_id, transaction_id)
        self.assertEqual(line_item.orderable_item_id, published_item.id)
        self.assertIsInstance(line_item.orderable_item, EbayItemModel)
        self.assertEqual(line_item.name, "Inventorum iPad Stand")
        self.assertEqual(line_item.quantity, 2)
        self.assertEqual(line_item.unit_price, D("3.99"))
        # tax rate should have been taken from the ebay item model
        self.assertEqual(line_item.tax_rate, D("7.000"))

        # task to create order in core api should have been scheduled
        self.schedule_core_order_creation_mock\
            .assert_called_once_with(order_model.id, context=sync.get_task_execution_context())

    def test_new_incoming_order_for_variation_listing(self):
        published_ebay_item_id = "000000000"
        transaction_id = "111111111"
        order_id = "000000000-111111111"

        # we set a different tax rate here to proof that the variation tax rate is taken over the item model
        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         tax_rate=D("19.000"),
                                                         external_id=published_ebay_item_id)
        published_variation = EbayItemVariationFactory(item=published_item,
                                                       tax_rate=D("7.000"),
                                                       inv_product_id=23)
        assert published_variation.sku.endswith("23")
        assert published_item.id != published_variation.id

        shipping_service_dhl = self.get_shipping_service_dhl()

        incoming_order = OrderTypeFactory.create(
            order_id=order_id,
            order_status=OrderStatusCodeType.Completed,
            transactions=[
                TransactionTypeWithVariationFactory.create(
                    transaction_id=transaction_id,
                    item__item_id=published_ebay_item_id,
                    item__title="Inventorum T-Shirt",
                    variation__variation_title="Inventorum T-Shirt [Black, M]",
                    variation__sku=published_variation.sku,
                )
            ],
            shipping_service_selected__shipping_service=shipping_service_dhl.external_id,
            shipping_service_selected__shipping_cost=D("4.90")
        )

        sync = IncomingEbayOrderSyncer(self.account)
        sync(incoming_order)

        # syncer should have created a new order model
        self.assertPostcondition(OrderModel.objects.count(), 1)

        order_model = OrderModel.objects.first()
        assert isinstance(order_model, OrderModel)
        self.assertEqual(order_model.ebay_id, order_id)

        line_item = order_model.line_items.first()
        assert isinstance(line_item, OrderLineItemModel)

        self.assertEqual(line_item.ebay_id, transaction_id)
        self.assertEqual(line_item.orderable_item_id, published_variation.id)
        self.assertIsInstance(line_item.orderable_item, EbayItemVariationModel)
        self.assertEqual(line_item.name, "Inventorum T-Shirt [Black, M]")
        self.assertEqual(line_item.orderable_item.tax_rate, D("7.000"))

        # task to create order in core api should have been scheduled
        self.schedule_core_order_creation_mock\
            .assert_called_once_with(order_model.id, context=sync.get_task_execution_context())

    def test_initial_order_state(self):
        published_ebay_item_id = "123456789"
        PublishedEbayItemFactory.create(account=self.account,
                                        external_id=published_ebay_item_id)

        incoming_order = OrderTypeFactory.create(
            shipping_service_selected__shipping_service=self.get_shipping_service_dhl().external_id,
            checkout_status__payment_method=BuyerPaymentMethodCodeType.MoneyXferAccepted,
            transactions=[TransactionTypeFactory.create(item__item_id=published_ebay_item_id)]
        )

        sync = IncomingEbayOrderSyncer(account=self.account)
        sync(incoming_order)

        order_model = OrderModel.objects.last()
        assert isinstance(order_model, OrderModel)
        self.assertFalse(order_model.core_status.is_paid)

        incoming_order = OrderTypeFactory.create(
            shipping_service_selected__shipping_service=self.get_shipping_service_dhl().external_id,
            checkout_status__payment_method=BuyerPaymentMethodCodeType.PayPal,
            transactions=[TransactionTypeFactory.create(item__item_id=published_ebay_item_id)]
        )

        sync = IncomingEbayOrderSyncer(account=self.account)
        sync(incoming_order)

        order_model = OrderModel.objects.last()
        assert isinstance(order_model, OrderModel)

        self.assertTrue(order_model.ebay_status.is_paid)
        self.assertTrue(order_model.core_status.is_paid)
