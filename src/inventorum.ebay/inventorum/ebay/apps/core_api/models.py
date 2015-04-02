# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import serializers

from inventorum.ebay.lib.rest.serializers import POPOSerializer


log = logging.getLogger(__name__)


class CoreProduct(object):

    def __init__(self, id, name, description, gross_price, stock):
        self.id = id
        self.name = name
        self.description = description
        self.gross_price = gross_price
        self.stock = stock


class CoreProductSerializer(POPOSerializer):
    EBAY_META = "ebay"

    class CoreProductMetaSerializer(serializers.Serializer):
        name = serializers.CharField(allow_blank=True)
        description = serializers.CharField(allow_blank=True)
        gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = CoreProduct

    id = serializers.IntegerField(required=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    gross_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.DecimalField(max_digits=10, decimal_places=2)

    meta = serializers.DictField(child=CoreProductMetaSerializer())

    def create(self, validated_data):
        if "meta" in validated_data:
            if "ebay" in validated_data["meta"]:
                ebay_meta = validated_data["meta"]["ebay"]

                def overwrite_from_meta(attr):
                    if ebay_meta[attr] and ebay_meta[attr] != validated_data[attr]:
                        validated_data[attr] = ebay_meta[attr]

                overwrite_from_meta("name")
                overwrite_from_meta("description")
                overwrite_from_meta("gross_price")

            # we need meta only for attr overwrites => throw it away afterwards
            del validated_data["meta"]

        return super(CoreProductSerializer, self).create(validated_data)
