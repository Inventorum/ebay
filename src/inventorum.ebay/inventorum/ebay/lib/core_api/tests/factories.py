# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D, Decimal
import logging
from random import randint

import factory
from factory import fuzzy
from inventorum.ebay.lib.core_api import BinaryCoreOrderStates
from inventorum.ebay.lib.core_api.models import CoreProductDelta, CoreOrder, CoreDeltaReturn, CoreDeltaReturnItem, \
    CoreBasket, CoreProduct, CoreProductAttribute, CoreInfo, CoreTaxType


log = logging.getLogger(__name__)


NUMBER_CHARS = [str(i) for i in range(10)]


class CoreProductFactory(factory.Factory):

    class Meta:
        model = CoreProduct

    id = fuzzy.FuzzyInteger(low=1000, high=99999)
    name = factory.Sequence(lambda n: "Test Product {0}".format(n))
    gross_price = fuzzy.FuzzyDecimal(low=0, high=1000, precision=2)
    tax_type_id = fuzzy.FuzzyInteger(low=50000, high=999999)
    quantity = fuzzy.FuzzyInteger(low=0, high=10000)
    ean = fuzzy.FuzzyText(length=12, chars=NUMBER_CHARS)
    images = None


class CoreProductAttributeFactory(factory.Factory):

    class Meta:
        model = CoreProductAttribute

    key = "color"
    values = factory.LazyAttribute(lambda o: ["red"])


class CoreProductVariationFactory(CoreProductFactory):

    class Meta:
        model = CoreProduct

    name = factory.Sequence(lambda n: "Test Variation {0}".format(n))


class CoreProductDeltaFactory(factory.Factory):

    class Meta:
        model = CoreProductDelta

    id = fuzzy.FuzzyInteger(low=1000, high=99999)
    name = factory.Sequence(lambda n: "Test Delta Product {0}".format(n))
    gross_price = fuzzy.FuzzyDecimal(low=0, high=1000, precision=2)
    quantity = fuzzy.FuzzyInteger(low=0, high=10000)
    state = "updated"
    parent = None


class CoreBasketFactory(factory.Factory):

    class Meta:
        model = CoreBasket

    items = []


class CoreOrderFactory(factory.Factory):

    class Meta:
        model = CoreOrder

    id = fuzzy.FuzzyInteger(low=10000, high=99999)
    state = BinaryCoreOrderStates.DRAFT | BinaryCoreOrderStates.PENDING
    basket = factory.SubFactory(CoreBasketFactory)


class CoreDeltaReturnItemFactory(factory.Factory):
    
    class Meta:
        model = CoreDeltaReturnItem

    id = fuzzy.FuzzyInteger(low=1000, high=99999)
    basket_item_id = fuzzy.FuzzyInteger(low=10000, high=99999)
    name = factory.Sequence(lambda n: "Order line item {}".format(n))
    quantity = fuzzy.FuzzyInteger(low=1, high=100)
    amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)


class CoreDeltaReturnFactory(factory.Factory):

    class Meta:
        model = CoreDeltaReturn

    id = fuzzy.FuzzyInteger(low=100, high=99999)
    order_id = fuzzy.FuzzyInteger(low=10000, high=99999)
    total_amount = fuzzy.FuzzyDecimal(low=1, high=1000, precision=2)

    items = []


class CoreInfoFactory(factory.Factory):

    class Meta:
        model = CoreInfo

    account = None
    tax_types = CoreTaxType(1, Decimal("19.00"))
