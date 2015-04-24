# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.shipping.models import ShippingServiceModel
from inventorum.ebay.apps.shipping.serializers import ShippingServiceSerializer
from inventorum.ebay.lib.rest.resources import APIResource
from rest_framework.response import Response


log = logging.getLogger(__name__)


class ShippingServiceListResource(APIResource):
    serializer_class = ShippingServiceSerializer

    def get_queryset(self):
        country = self.request.user.account.country
        return ShippingServiceModel.objects.by_country(country)

    def get(self, request):
        services = self.get_queryset()
        serializer = self.get_serializer(services, many=True)
        return Response(data=dict(data=serializer.data))
