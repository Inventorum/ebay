# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal as D
import logging
from random import randint

import factory
from inventorum.ebay.apps.core_api.models import CoreProductDelta

log = logging.getLogger(__name__)


class CoreProductDeltaFactory(factory.Factory):

    class Meta:
        model = CoreProductDelta

    id = factory.LazyAttribute(lambda m: randint(999, 99999))
    name = "Some product"
    state = "updated"
    gross_price = D("1.99")
    quantity = 100
