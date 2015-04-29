# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.lib.rest.fields import MoneyField

from rest_framework import serializers


log = logging.getLogger(__name__)


class OrderShippingConfigurationCoreAPIDataSerializer(serializers.ModelSerializer):
    """
    Responsible for serializing a `ShippingServiceConfigurationModel` instance assigned as shipping to an order
    into the according data format to create/update its representation in the core api
    """

    class Meta:
        model = ShippingServiceConfigurationModel
        fields = ("name", "cost", "external_id")

    name = serializers.CharField(source="service.description")
    cost = MoneyField()
    external_id = serializers.CharField(source="service.external_id")


class OrderLineItemModelCoreAPIDataSerializer(serializers.ModelSerializer):
    """
    Responsible for serializing a `OrderLineItemModel` instance into the according data format
    to create/update its representation in the core api
    """

    class Meta:
        model = OrderLineItemModel
        fields = ("product", "name", "quantity", "gross_price")

    product = serializers.IntegerField(source="orderable_item.inv_product_id")
    gross_price = MoneyField(source="unit_price")


class OrderModelCoreAPIDataSerializer(serializers.ModelSerializer):
    """
    Responsible for serializing a `OrderModel` instance into the according data format
    to create/update its representation in the core api
    """
    
    class Meta:
        model = OrderModel
        fields = ("items", "shipment")

    items = OrderLineItemModelCoreAPIDataSerializer(source="line_items", many=True)
    shipment = OrderShippingConfigurationCoreAPIDataSerializer(source="shipping")
