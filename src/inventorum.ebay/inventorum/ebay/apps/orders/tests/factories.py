# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy

from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory
from inventorum.ebay.apps.shipping.tests.factories import ShippingServiceConfigurationFactory
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType, BuyerPaymentMethodCodeType, PaymentStatusCodeType


log = logging.getLogger(__name__)


NUMBER_CHARS = [str(i) for i in range(10)]


class OrderModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderModel
        # django_get_or_create = ("ebay_id",)

    account = factory.SubFactory(EbayAccountFactory)

    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS, prefix="9912341245-")
    ebay_status = CompleteStatusCodeType.Complete

    buyer_first_name = "John"
    buyer_last_name = "Wayne"
    buyer_email = "test@inventorum.com"

    shipping_first_name = "Christoph"
    shipping_last_name = "Brem"
    shipping_address1 = "Voltastraße 5"
    shipping_address2 = "Inventorum, Gebäude 10"
    shipping_postal_code = "13355"
    shipping_city = "Berlin"
    shipping_state = "Wedding"
    shipping_country = "DE"

    selected_shipping = factory.SubFactory(ShippingServiceConfigurationFactory)

    subtotal = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    total = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)

    payment_method = BuyerPaymentMethodCodeType.PayPal
    payment_amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    payment_status = PaymentStatusCodeType.NoPaymentFailure


class OrderLineItemModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderLineItemModel
        # django_get_or_create = ("ebay_id",)

    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)

    name = factory.Sequence(lambda n: "Order line item {}".format(n))
    unit_price = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    quantity = fuzzy.FuzzyInteger(low=1, high=100)

    order = factory.SubFactory(OrderModelFactory)
    orderable_item = factory.SubFactory(PublishedEbayItemFactory)
