# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy

from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum.ebay.apps.products.tests.factories import PublishedEbayItemFactory
from inventorum.ebay.lib.ebay.data import CompleteStatusCodeType


log = logging.getLogger(__name__)


NUMBER_CHARS = [str(i) for i in range(10)]


class OrderModelFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderModel
        # django_get_or_create = ("ebay_id",)

    account = factory.SubFactory(EbayAccountFactory)

    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS, prefix="9912341245-")
    final_price = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)

    ebay_status = fuzzy.FuzzyChoice(choices=[CompleteStatusCodeType.Complete, CompleteStatusCodeType.Incomplete,
                                             CompleteStatusCodeType.Pending])


class OrderLineItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = OrderLineItemModel
        # django_get_or_create = ("ebay_id",)

    ebay_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    unit_price = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)
    quantity = fuzzy.FuzzyInteger(low=1, high=100)

    order = factory.SubFactory(OrderModelFactory)
    orderable_item = factory.SubFactory(PublishedEbayItemFactory)
