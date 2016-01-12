# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from inventorum_ebay.apps.inventory.models import CoreQuantity, EbayItemForQuantityCheck, EbaySanityCheck
from inventorum_ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, IntegerField, DecimalField

log = logging.getLogger(__name__)


class AvailabilityEbaySerializer(POPOSerializer):
    sku = CharField()
    available = CharField(read_only=True)
    LocationID = CharField()
    quantity = IntegerField()

    class Meta(POPOSerializer.Meta):
        model = EbayItemForQuantityCheck


class SanityCheckEbaySerializer(POPOSerializer):
    trackingUUID = CharField()
    availabilities = AvailabilityEbaySerializer(many=True)

    class Meta(POPOSerializer.Meta):
        model = EbaySanityCheck


class QuantityCoreApiResponseDeserializer(POPOSerializer):
    id = CharField()
    quantity = DecimalField(max_digits=20, decimal_places=10)

    class Meta(POPOSerializer.Meta):
        model = CoreQuantity
