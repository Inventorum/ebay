# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D
import logging
from random import randint

import factory
from factory import fuzzy
from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.core_api.models import CoreProductDelta, CoreOrder, CoreDeltaReturn, CoreDeltaReturnItem


log = logging.getLogger(__name__)


class CoreProductDeltaFactory(factory.Factory):

    class Meta:
        model = CoreProductDelta

    id = factory.LazyAttribute(lambda m: randint(999, 99999))
    name = "Some product"
    state = "updated"
    gross_price = D("1.99")
    quantity = 100
    parent = None


class CoreOrderFactory(factory.Factory):

    class Meta:
        model = CoreOrder

    id = fuzzy.FuzzyInteger(low=10000, high=99999)
    state = BinaryCoreOrderStates.DRAFT | BinaryCoreOrderStates.PENDING


class CoreDeltaReturnItemFactory(factory.Factory):
    
    class Meta:
        model = CoreDeltaReturnItem

    id = fuzzy.FuzzyInteger(low=1000, high=99999)
    basket_item_id = fuzzy.FuzzyInteger(low=10000, high=99999)
    name = factory.Sequence(lambda n: "Order line item {}".format(n))
    quantity = fuzzy.FuzzyInteger(low=1, high=100)


class CoreDeltaReturnFactory(factory.Factory):

    class Meta:
        model = CoreDeltaReturn

    id = fuzzy.FuzzyInteger(low=100, high=99999)
    order_id = fuzzy.FuzzyInteger(low=10000, high=99999)
    items = []
