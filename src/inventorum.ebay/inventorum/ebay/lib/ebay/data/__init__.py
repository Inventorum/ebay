# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

import re
from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.rest.fields import MoneyField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CompleteStatusCodeType(object):
    """
    Provides consts for the ebay `CompleteStatusCodeType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/CompleteStatusCodeType.html
    """

    # Generally speaking, an order is complete when payment from the buyer has been initiated and processed.
    Complete = "Complete"

    # Generally speaking, an order is incomplete when payment from the buyer has yet to be initiated.
    Incomplete = "Incomplete"

    # Generally speaking, an order is pending when payment from the buyer has been initiated but not yet fully processed
    Pending = "Pending"

    CHOICES = (
        (Complete, "Complete"),
        (Incomplete, "Incomplete"),
        (Pending, "Pending")
    )


class OrderStatusCodeType(object):
    """
    Provides consts for the ebay `OrderStatusCodeType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/OrderStatusCodeType.html
    """

    Completed = "Completed"


class BuyerPaymentMethodCodeType(object):
    """
    Provides consts for the ebay `BuyerPaymentMethodCodeType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/BuyerPaymentMethodCodeType.html
    """

    PayPal = "PayPal"


class PaymentStatusCodeType(object):
    """
    Provides consts for the ebay `PaymentStatusCodeType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/PaymentStatusCodeType.html
    """

    NoPaymentFailure = "NoPaymentFailure"


class TradingRoleCodeType(object):
    """
    Provides consts for the ebay `TradingRoleCodeType`
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/types/TradingRoleCodeType.html
    """

    Seller = "Seller"


# TODO jm: Move to data/utils.py #######################################################################################

class EbayParser(object):
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    RE_SECURE_BODY = re.compile("<RequesterCredentials>(.+?)</RequesterCredentials>")

    @classmethod
    def parse_date(cls, str_date):
        """
        Parse given ebay date as string to datetime
        :param str_date: Comming from ebay
        :return: Parsed date

        :type str_date: str | unicode
        :rtype: datetime
        """
        return datetime.strptime(str_date, cls.DATE_FORMAT)

    @classmethod
    def format_date(cls, date):
        """
        Formats the given datetime to the ebay datetime format
        :type date: datetime
        :rtype: unicode
        """
        return date.strftime(cls.DATE_FORMAT)

    @classmethod
    def encode_price(cls, price):
        """
        Force it to be Decimal, then quantize to 2 and make it unicode
        :rtype: unicode
        """
        return unicode(Decimal(price).quantize(Decimal('0.01')))

    @classmethod
    def make_body_secure(cls, body):
        """
        Clears all credentials from body.
        :param body: unicode
        :return: unicode
        """
        return cls.RE_SECURE_BODY.sub("<RequesterCredentials>***</RequesterCredentials>", body)


class EbayBooleanField(serializers.BooleanField):
    TRUE_VALUES = frozenset(serializers.BooleanField.TRUE_VALUES | {'Enabled'})
    FALSE_VALUES = frozenset(serializers.BooleanField.FALSE_VALUES | {'Disabled'})


class EbayListSerializer(serializers.ListSerializer):

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = [data]
        return super(EbayListSerializer, self).to_internal_value(data)


class EbayArrayField(serializers.Field):

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


class EbayAmountField(MoneyField):

    def __init__(self, **kwargs):
        super(EbayAmountField, self).__init__(decimal_places=2, max_digits=10, **kwargs)

    def to_internal_value(self, data):
        return super(EbayAmountField, self).to_internal_value(data["value"])


class EbayNullableIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data == 'null':
            return None
        return super(EbayNullableIntegerField, self).to_internal_value(data)


# TODO jm: Move to data/utils.py #######################################################################################
