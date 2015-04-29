# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, ChoiceField, IntegerField, DecimalField, SerializerMethodField
from rest_framework.serializers import Serializer

log = logging.getLogger(__name__)


class AvailabilityEbaySerializer(Serializer):
    sku = CharField()
    available = SerializerMethodField(read_only=True)
    LocationID = CharField()
    quantity = IntegerField()

    def get_available(self, obj):
        return 'IN_STOCK' if obj['quantity'] > 0 else 'OUT_OF_STOCK'


class SanityCheckEbaySerializer(Serializer):
    trackingUUID = CharField()
    availabilities = AvailabilityEbaySerializer(many=True)


class CoreQuantity(object):
    def __init__(self, id, quantity):
        self.id = id
        self.quantity = quantity


class QuantityCoreApiResponse(POPOSerializer):
    id = CharField()
    quantity = DecimalField(max_digits=20, decimal_places=10)

    class Meta(POPOSerializer.Meta):
        model = CoreQuantity