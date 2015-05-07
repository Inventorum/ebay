# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.models import AddressModel
from inventorum.ebay.apps.core_api import CoreChannel, BinaryCoreOrderStates
from inventorum.ebay.apps.orders.models import OrderModel, OrderLineItemModel
from inventorum.ebay.apps.shipping.models import ShippingServiceConfigurationModel, ShippingServiceModel
from inventorum.ebay.lib.rest.fields import MoneyField, TaxRateField
from inventorum.ebay.lib.utils import days_to_seconds

from rest_framework import serializers


log = logging.getLogger(__name__)


class ShippingServiceCoreAPIDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingServiceModel
        fields = ("name", "time_min", "time_max")

    name = serializers.CharField(source="description")
    time_min = serializers.SerializerMethodField()
    time_max = serializers.SerializerMethodField()

    def get_time_min(self, service):
        """
        :type service: ShippingServiceModel
        :rtype: int | None
        """
        if service.shipping_time_min is not None:
            return days_to_seconds(service.shipping_time_min)

    def get_time_max(self, service):
        """
        :type service: ShippingServiceModel
        :rtype: int | None
        """
        if service.shipping_time_max is not None:
            return days_to_seconds(service.shipping_time_max)


class OrderShipmentCoreAPIDataSerializer(serializers.ModelSerializer):
    """
    Responsible for serializing a `ShippingServiceConfigurationModel` instance assigned as shipping to an order
    into the according data format to create/update its representation in the core api
    """
    class Meta:
        model = ShippingServiceConfigurationModel
        fields = ("service", "name", "cost", "external_key")

    service = ShippingServiceCoreAPIDataSerializer()

    name = serializers.CharField(source="service.description")
    cost = MoneyField()
    external_key = serializers.CharField(source="service.external_id")


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
        fields = ("product", "name", "quantity", "unit_gross_price", "tax_rate")

    product = serializers.IntegerField(source="orderable_item.inv_product_id")
    unit_gross_price = MoneyField(source="unit_price")
    tax_rate = TaxRateField()


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
        fields = ("channel", "basket", "shipment", "customer", "payments", "state")

    channel = serializers.SerializerMethodField()
    basket = serializers.SerializerMethodField()
    shipment = OrderShipmentCoreAPIDataSerializer(source="selected_shipping")
    customer = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_channel(self, order):
        return CoreChannel.EBAY

    def get_basket(self, order):
        return OrderBasketCoreAPIDataSerializer(order).data

    def get_customer(self, order):
        return OrderCustomerCoreAPIDataSerializer(order).data

    def get_payments(self, order):
        return [OrderPaymentCoreAPIDataSerializer(order).data]

    def get_state(self, order):
        return BinaryCoreOrderStates.PENDING
