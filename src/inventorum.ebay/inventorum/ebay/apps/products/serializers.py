# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.models import EbayProductModel
from rest_framework.serializers import ModelSerializer


class EbayProductSerializer(ModelSerializer):
    class Meta:
        model = EbayProductModel
        fields = ('id', 'external_item_id')
