# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.lib.ebay.details import EbayShippingService
from inventorum.ebay.tests import Countries


log = logging.getLogger(__name__)


class ShippingServiceFactory(factory.DjangoModelFactory):

    class Meta:
        model = ShippingServiceModel

    country = Countries.DE
    external_id = factory.Sequence(lambda i: "EbayShippingService_%s" % i)
    description = "Some ebay description"

    shipping_time_min = 1
    shipping_time_max = 3

    is_international = False


class EbayShippingServiceFactory(factory.Factory):

    class Meta:
        model = EbayShippingService

    id = factory.Sequence(lambda i: "ShippingService_%s" % i)
    description = "Hello, I'm an ebay shipping service"
    valid_for_selling_flow = True

    shipping_time_min = 1
    shipping_time_max = 3

    international = False
    dimensions_required = False
