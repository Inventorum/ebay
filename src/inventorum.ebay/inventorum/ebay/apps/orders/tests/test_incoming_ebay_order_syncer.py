# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.accounts.models import AddressModel
from inventorum.ebay.apps.orders import CorePaymentMethod
from inventorum.ebay.apps.products.models import EbayItemVariationModel, EbayItemModel
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.tests.testcases import UnitTestCase
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.orders.ebay_orders_sync import IncomingEbayOrderSyncer
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory, EbayItemVariationFactory
from inventorum.ebay.lib.ebay.data import OrderStatusCodeType, PaymentStatusCodeType, BuyerPaymentMethodCodeType
from inventorum.ebay.lib.ebay.data.tests.factories import OrderTypeFactory, TransactionTypeFactory, \
    TransactionTypeWithVariationFactory


log = logging.getLogger(__name__)


class UnitTestEbayOrderSyncer(UnitTestCase, ShippingServiceTestMixin):

    def setUp(self):
        super(UnitTestEbayOrderSyncer, self).setUp()

        self.account = EbayAccountFactory.create()
        self.default_user = EbayUserFactory.create(account=self.account)

        self.schedule_core_order_creation_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_core_order_creation")

    def test_new_incoming_order_for_non_variation_listing(self):
        self.assertPrecondition(OrderModel.objects.count(), 0)

        published_ebay_item_id = "123456789"
        transaction_id = "987654321"
        order_id = "123456789-987654321"

        published_item = PublishedEbayItemFactory.create(account=self.account,
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

        # task to create order in core api should have been scheduled
        self.schedule_core_order_creation_mock\
            .assert_called_once_with(order_model.id, context=sync.get_task_execution_context())

    def test_new_incoming_order_for_variation_listing(self):
        self.assertPrecondition(OrderModel.objects.count(), 0)

        published_ebay_item_id = "000000000"
        transaction_id = "111111111"
        order_id = "000000000-111111111"

        published_item = PublishedEbayItemFactory.create(account=self.account,
                                                         external_id=published_ebay_item_id)
        published_variation = EbayItemVariationFactory(item=published_item,
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

        # task to create order in core api should have been scheduled
        self.schedule_core_order_creation_mock\
            .assert_called_once_with(order_model.id, context=sync.get_task_execution_context())
