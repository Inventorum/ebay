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


class TransactionStatusType(object):
    """
    Represents the ebay `TransactionStatusType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/TransactionStatusType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        CompleteStatus = serializers.CharField(source="complete_status")

    # / Deserialization ###############

    def __init__(self, complete_status):
        """
        :type complete_status: CompleteStatusCodeType
        """
        self.complete_status = complete_status

TransactionStatusType.Deserializer.Meta.model = TransactionStatusType


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
        QuantityPurchased = serializers.IntegerField(source="quantity_purchased")
        TransactionPrice = EbayAmountField(source="transaction_price")
        AmountPaid = EbayAmountField(source="amount_paid")
        Status = TransactionStatusType.Deserializer(source="status")
        ShippingServiceSelected = ShippingServiceOption.Deserializer(source="shipping_service_selected",
                                                                     required=False)

    # / Deserialization ###############

    def __init__(self, transaction_id, quantity_purchased, transaction_price, amount_paid, status,
                 shipping_service_selected=None):
        """
        :type transaction_id: unicode
        :type quantity_purchased: int
        :type transaction_price: decimal.Decimal
        :type amount_paid: decimal.Decimal
        :type status: TransactionStatusType
        :type shipping_service_selected: ShippingServiceOption
        """

        self.transaction_id = transaction_id
        self.amount_paid = amount_paid
        self.quantity_purchased = quantity_purchased
        self.transaction_price = transaction_price
        self.status = status
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
        :type item: ItemType
        :type transactions: list[TransactionType]
        """
        self.item = item
        self.transactions = transactions

GetItemTransactionsResponse.Deserializer.Meta.model = GetItemTransactionsResponse
