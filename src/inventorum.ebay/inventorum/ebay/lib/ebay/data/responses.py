# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay.data import EbayAmountField, EbayArrayField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


log = logging.getLogger(__name__)


class ItemType(object):
    """
    Represents the ebay `ItemType`
    http://developer.ebay.com/Devzone/XML/docs/Reference/ebay/types/ItemType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        ItemID = serializers.CharField(source="item_id")

    # / Deserialization ###############

    def __init__(self, item_id):
        """
        :type item_id: unicode
        """
        self.item_id = item_id

ItemType.Deserializer.Meta.model = ItemType


class GetItemResponse(object):
    """
    Represents the ebay `GetItem` response
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetItem.html#Output
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Item = ItemType.Deserializer(source="item")

    # / Deserialization ###############

    def __init__(self, item):
        """
        :type item: ItemType
        """
        self.item = item

GetItemResponse.Deserializer.Meta.model = GetItemResponse


class ShippingServiceOption(object):
    """
    Represents the ebay `ShippingServiceOptionsType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/ShippingServiceOptionsType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        ShippingService = serializers.CharField(source="shipping_service")
        ShippingServiceCost = EbayAmountField(source="shipping_cost")

    # / Deserialization ###############

    def __init__(self, shipping_service, shipping_cost):
        """
        :type shipping_service: unicode
        :type shipping_cost: decimal.Decimal
        """
        self.shipping_service = shipping_service
        self.shipping_cost = shipping_cost

ShippingServiceOption.Deserializer.Meta.model = ShippingServiceOption


class TransactionType(object):
    """
    Represents the ebay `TransactionType`
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/TransactionType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        TransactionID = serializers.CharField(source="transaction_id")
        QuantityPurchased = serializers.IntegerField(source="quantity")
        TransactionPrice = EbayAmountField(source="unit_price")
        AmountPaid = EbayAmountField(source="total_price")
        ShippingServiceSelected = ShippingServiceOption.Deserializer(source="shipping_service_selected",
                                                                     required=False)

    # / Deserialization ###############

    def __init__(self, transaction_id, quantity, unit_price, total_price, shipping_service_selected=None):
        """
        :type transaction_id: unicode
        :type quantity: int
        :type unit_price: decimal.Decimal
        :type total_price: decimal.Decimal
        :type shipping_service_selected: ShippingServiceOption
        """
        self.transaction_id = transaction_id
        self.total_price = total_price
        self.quantity = quantity
        self.unit_price = unit_price
        self.shipping_service_selected = shipping_service_selected

TransactionType.Deserializer.Meta.model = TransactionType


class GetItemTransactionsResponse(object):
    """
    Represents the ebay `GetItemTransactions` response
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetItemTransactions.html#Output
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Item = ItemType.Deserializer(source="item")
        TransactionArray = EbayArrayField(item_key="Transaction", item_deserializer=TransactionType.Deserializer,
                                          source="transactions")

    # / Deserialization ###############

    def __init__(self, item, transactions):
        """
        :type item: ResponseItem
        :type transactions: list[TransactionType]
        """
        self.item = item
        self.transactions = transactions

GetItemTransactionsResponse.Deserializer.Meta.model = GetItemTransactionsResponse
