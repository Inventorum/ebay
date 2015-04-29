# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.apps.shipping.serializers import ShippingServiceSerializer
from inventorum.ebay.lib.rest.resources import APIListResource


log = logging.getLogger(__name__)


class ShippingServiceListResource(APIListResource):
    serializer_class = ShippingServiceSerializer
    page_size = None  # disables pagination

    def get_queryset(self):
        country = self.request.user.account.country
        return ShippingServiceModel.objects.by_country(country)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
