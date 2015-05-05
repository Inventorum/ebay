# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.models import AddressModel
from inventorum.ebay.apps.accounts.serializers import AddressSerializer
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


class OrderCustomerAddressCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = AddressModel
        fields = ("first_name", "last_name", "address1", "address2", "zipcode", "city", "state", "country")

    address1 = serializers.CharField(source="street")
    address2 = serializers.CharField(source="street1")
    zipcode = serializers.CharField(source="postal_code")
    state = serializers.CharField(source="region")


class OrderCustomerCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("first_name", "last_name", "email", "billing_address", "shipping_address")

    first_name = serializers.CharField(source="buyer_first_name")
    last_name = serializers.CharField(source="buyer_last_name")
    email = serializers.CharField(source="buyer_email")

    billing_address = OrderCustomerAddressCoreAPIDataSerializer()
    shipping_address = serializers.SerializerMethodField()

    def get_shipping_address(self, order):
        # Note: core api wants to have a list of shipping addresses :-(
        return [OrderCustomerAddressCoreAPIDataSerializer(order.shipping_address).data]


class OrderPaymentCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("payment_amount", "payment_method")

    payment_amount = MoneyField()


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


class OrderBasketCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderModel
        fields = ("items",)

    items = OrderLineItemModelCoreAPIDataSerializer(source="line_items", many=True)


class OrderModelCoreAPIDataSerializer(serializers.ModelSerializer):
    """
    Responsible for serializing a `OrderModel` instance into the according data format
    to create/update its representation in the core api
    """
    
    class Meta:
        model = OrderModel
        fields = ("basket", "shipment", "customer", "payments")

    basket = serializers.SerializerMethodField()
    shipment = OrderShipmentCoreAPIDataSerializer(source="selected_shipping")
    customer = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    def get_basket(self, order):
        return OrderBasketCoreAPIDataSerializer(order).data

    def get_customer(self, order):
        return OrderCustomerCoreAPIDataSerializer(order).data

    def get_payments(self, order):
        return [OrderPaymentCoreAPIDataSerializer(order).data]
