# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


log = logging.getLogger(__name__)


# TODO jm: Can we re-use these for publishing etc. ?
class EbayResponseItem(object):

    def __init__(self, item_id):
        """
        :type item_id: unicode
        """
        self.item_id = item_id


class EbayArrayField(serializers.Serializer):

    def __init__(self, item_key, item_deserializer, *args, **kwargs):
        self.item_key = item_key
        self.item_deserializer = item_deserializer
        super(EbayArrayField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if self.item_key not in data:
            raise ValidationError("item_key `%s` not found" % self.item_key)

        item_data = data[self.item_key]
        if isinstance(item_data, dict):
            item_data = [item_data]

        return [self.item_deserializer(data=data).build() for data in item_data]


class EbayAmountField(serializers.DecimalField):

    def __init__(self, **kwargs):
        super(EbayAmountField, self).__init__(decimal_places=2, max_digits=10, **kwargs)

    def to_internal_value(self, data):
        return super(EbayAmountField, self).to_internal_value(data["value"])


class EbayResponseItemDeserializer(POPOSerializer):

    class Meta:
        model = EbayResponseItem

    ItemID = serializers.CharField(source="item_id")


class EbayGetItemResponse(object):

    def __init__(self, item):
        """
        :type item: EbayResponseItem
        """
        self.item = item


class EbayGetItemResponseDeserializer(POPOSerializer):

    class Meta:
        model = EbayGetItemResponse

    Item = EbayResponseItemDeserializer(source="item")


class ItemTransaction(object):

    def __init__(self, transaction_id, quantity, unit_price, total_price):
        """
        :type transaction_id: unicode
        :type quantity: int
        :type unit_price: decimal.Decimal
        :type total_price: decimal.Decimal
        """
        self.transaction_id = transaction_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price


class ItemTransactionDeserializer(POPOSerializer):

    class Meta:
        model = ItemTransaction

    TransactionID = serializers.CharField(source="transaction_id")
    QuantityPurchased = serializers.IntegerField(source="quantity")
    TransactionPrice = EbayAmountField(source="unit_price")
    AmountPaid = EbayAmountField(source="total_price")

class EbayGetItemTransactionsResponse(object):

    def __init__(self, item, transactions):
        """
        :type item: EbayResponseItem
        :type transactions: list[ItemTransaction]
        """
        self.item = item
        self.transactions = transactions


class EbayGetItemTransactionsResponseDeserializer(POPOSerializer):

    class Meta:
        model = EbayGetItemTransactionsResponse

    Item = EbayResponseItemDeserializer(source="item")
    TransactionArray = EbayArrayField(item_key="Transaction", item_deserializer=ItemTransactionDeserializer,
                                      source="transactions")
