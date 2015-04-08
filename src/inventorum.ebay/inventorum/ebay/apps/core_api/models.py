# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import serializers

from inventorum.ebay.lib.rest.serializers import POPOSerializer


log = logging.getLogger(__name__)


class CoreProduct(object):
    """ Represents a core product from the inventorum api """
    def __init__(self, id, name, description, gross_price, quantity, images, variation_count, shipping_services):
        """
        :type id: int
        :type name: unicode
        :type description: unicode
        :type gross_price: decimal.Decimal
        :type quantity: decimal.Decimal
        :type images: list of CoreProductImage
        :type variation_count: int
        :type shipping_services: list of CoreShippingService
        """
        self.id = id
        self.name = name
        self.description = description
        self.gross_price = gross_price
        self.quantity = quantity
        self.images = images
        self.variation_count = variation_count
        self.shipping_services = shipping_services

    @property
    def is_parent(self):
        return self.variation_count > 0


class CoreProductImage(object):
    """ Represents a product image embedded in a core product"""
    def __init__(self, id, url):
        """
        :type id: int
        :type url: unicode
        """
        self.id = id
        self.url = url


class CoreProductImageDeserializer(POPOSerializer):

        class Meta:
            model = CoreProductImage

        id = serializers.IntegerField()
        ipad_retina = serializers.CharField(source="url")


class CoreShippingService(object):
    """ Represents a shipping service model """
    def __init__(self, id, description, time_min, time_max, additional_cost, cost):
        """
        :type id: unicode
        :type description: unicode
        :type time_min: int
        :type time_max: int
        :type additional_cost: decimal.Decimal
        :type cost: decimal.Decimal
        """
        self.id = id
        self.description = description
        self.time_min = time_min
        self.time_max = time_max
        self.additional_cost = additional_cost
        self.cost = cost

class CoreShippingServiceDeserializer(POPOSerializer):

        class Meta:
            model = CoreShippingService

        id = serializers.CharField()
        description = serializers.CharField()
        time_min = serializers.IntegerField()
        time_max = serializers.IntegerField()
        additional_cost = serializers.DecimalField(max_digits=20, decimal_places=10)
        cost = serializers.DecimalField(max_digits=20, decimal_places=10)


class CoreProductDeserializer(POPOSerializer):

    class Meta:
        model = CoreProduct

    class MetaDeserializer(serializers.Serializer):
        """ Helper deserializer for nested meta information (won't be assigned to POPOs) """
        name = serializers.CharField(allow_null=True, allow_blank=True)
        description = serializers.CharField(allow_null=True, allow_blank=True)
        gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)

        images = CoreProductImageDeserializer(many=True)

    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    variation_count = serializers.IntegerField()

    images = CoreProductImageDeserializer(many=True)
    shipping_services = CoreShippingServiceDeserializer(many=True)

    meta = serializers.DictField(child=MetaDeserializer())

    def create(self, validated_data):
        if "meta" in validated_data:
            if "ebay" in validated_data["meta"]:
                ebay_meta = validated_data["meta"]["ebay"]

                def overwrite_from_meta(attr):
                    if attr in ebay_meta and ebay_meta[attr] not in (None, []):
                        validated_data[attr] = ebay_meta[attr]

                overwrite_from_meta("name")
                overwrite_from_meta("description")
                overwrite_from_meta("gross_price")

                overwrite_from_meta("images")

            # we need meta only for attr overwrites => throw it away afterwards
            del validated_data["meta"]

        return super(CoreProductDeserializer, self).create(validated_data)
