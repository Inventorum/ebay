# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel
from inventorum.ebay.lib.rest.fields import MoneyField

from rest_framework import serializers


log = logging.getLogger(__name__)


class OrderShipmentCoreAPIDataSerializer(serializers.ModelSerializer):
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


class OrderShippingAddressCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("first_name", "last_name", "address1", "address2", "zipcode", "city", "state", "country")

    first_name = serializers.CharField(source="shipping_first_name")
    last_name = serializers.CharField(source="shipping_last_name")
    address1 = serializers.CharField(source="shipping_address1")
    address2 = serializers.CharField(source="shipping_address2")
    zipcode = serializers.CharField(source="shipping_postal_code")
    city = serializers.CharField(source="shipping_city")
    state = serializers.CharField(source="shipping_state")
    country = serializers.CharField(source="shipping_country")


class OrderCustomerCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("first_name", "last_name", "email", "billing_address", "shipping_address")

    first_name = serializers.CharField(source="buyer_first_name")
    last_name = serializers.CharField(source="buyer_last_name")
    email = serializers.CharField(source="buyer_email")

    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    def get_billing_address(self, order):
        # we simply use the shipping address as billing address?!
        return OrderShippingAddressCoreAPIDataSerializer(order).data

    def get_shipping_address(self, order):
        # core api expects list?!
        return [OrderShippingAddressCoreAPIDataSerializer(order).data]


class OrderPaymentCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("payment_amount", "payment_method")

    payment_amount = MoneyField()
    payment_method = serializers.CharField()


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
        fields = ("items", "shipment", "customer", "payments")

    items = OrderLineItemModelCoreAPIDataSerializer(source="line_items", many=True)
    shipment = OrderShipmentCoreAPIDataSerializer(source="selected_shipping")
    customer = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    def get_customer(self, order):
        return OrderCustomerCoreAPIDataSerializer(order).data

    def get_payments(self, order):
        return [OrderPaymentCoreAPIDataSerializer(order).data]
