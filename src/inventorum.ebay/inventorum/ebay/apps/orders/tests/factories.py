# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal

import factory
from factory import fuzzy
from inventorum.ebay.apps.orders import CorePaymentMethod

from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel, OrderStatusModel
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, AddressFactory
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceConfigurationFactory
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType, BuyerPaymentMethodCodeType, PaymentStatusCodeType


log = logging.getLogger(__name__)


NUMBER_CHARS = [str(i) for i in range(10)]


class OrderStatusModelFactory(factory.DjangoModelFactory):
    
    class Meta:
        model = OrderStatusModel


class OrderModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderModel
        # django_get_or_create = ("ebay_id",)

    account = factory.SubFactory(EbayAccountFactory)
    ebay_status = factory.SubFactory(OrderStatusModelFactory)
    core_status = factory.SubFactory(OrderStatusModelFactory)

    inv_id = None
    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS, prefix="9912341245-")
    ebay_complete_status = CompleteStatusCodeType.Complete

    buyer_first_name = "John"
    buyer_last_name = "Wayne"
    buyer_email = "test@inventorum.com"
    billing_address = factory.SubFactory(AddressFactory)

    shipping_address = factory.SubFactory(AddressFactory)
    selected_shipping = factory.SubFactory(ShippingServiceConfigurationFactory)

    subtotal = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    total = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)

    payment_method = CorePaymentMethod.PAYPAL
    payment_amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    ebay_payment_method = BuyerPaymentMethodCodeType.PayPal
    ebay_payment_status = PaymentStatusCodeType.NoPaymentFailure


class OrderLineItemModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderLineItemModel
        # django_get_or_create = ("ebay_id",)

    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    inv_id = None

    name = factory.Sequence(lambda n: "Order line item {}".format(n))
    unit_price = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    tax_rate = fuzzy.FuzzyChoice([Decimal("0"), Decimal("7"), Decimal("19")])
    quantity = fuzzy.FuzzyInteger(low=1, high=100)

    order = factory.SubFactory(OrderModelFactory)
    orderable_item = factory.SubFactory(PublishedEbayItemFactory)
