# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy
from inventorum.ebay.apps.orders.tests.factories import OrderModelFactory, OrderLineItemModelFactory
from inventorum.ebay.apps.returns import EbayRefundType
from inventorum.ebay.apps.returns.models import ReturnModel, ReturnItemModel


log = logging.getLogger(__name__)


class ReturnModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = ReturnModel

    order = factory.SubFactory(OrderModelFactory)
    inv_id = fuzzy.FuzzyInteger(low=1, high=10000)
    refund_type = EbayRefundType.EBAY
    refund_amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)


class ReturnItemModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = ReturnItemModel

    order_line_item = factory.SubFactory(OrderLineItemModelFactory)
    inv_id = fuzzy.FuzzyInteger(low=1, high=10000)
    refund_quantity = fuzzy.FuzzyInteger(low=1, high=5)
    refund_amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)