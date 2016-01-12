# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields


log = logging.getLogger(__name__)


class EbayShippingService(object):

    def __init__(self, id, description, valid_for_selling_flow, shipping_time_min, shipping_time_max,
                 international, dimensions_required):
        """
        :param id: unicode
        :param description: unicode
        :param valid_for_selling_flow: bool
        :param shipping_time_min: int
        :param shipping_time_max: int
        :param international: bool
        :param dimensions_required: bool
        """
        self.id = id
        self.description = description
        self.valid_for_selling_flow = valid_for_selling_flow

        self.shipping_time_min = shipping_time_min
        self.shipping_time_max = shipping_time_max

        self.international = international
        self.dimensions_required = dimensions_required

    @classmethod
    def create_from_data(cls, data):
        """
        :type data: dict | list[dict]
        :rtype: EbayShippingService | list[EbayShippingService]
        """
        serializer = EbayShippingServiceDeserializer(data=data, many=isinstance(data, list))
        # TODO jm: Add custom list deserializer with build
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class EbayShippingServiceDeserializer(POPOSerializer):

    class Meta:
        model = EbayShippingService

    ShippingService = fields.CharField(source="id")
    Description = fields.CharField(source="description")
    ValidForSellingFlow = fields.BooleanField(source="valid_for_selling_flow")

    ShippingTimeMin = fields.IntegerField(source="shipping_time_min", required=False, default=None)
    ShippingTimeMax = fields.IntegerField(source="shipping_time_max", required=False, default=None)

    InternationalService = fields.BooleanField(source="international", required=False, default=False)
    DimensionsRequired = fields.BooleanField(source="dimensions_required", required=False, default=False)
