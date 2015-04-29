# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

import re

from django.utils.datetime_safe import datetime
from rest_framework.fields import BooleanField
from rest_framework import serializers


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


class EbayBooleanField(BooleanField):
    TRUE_VALUES = frozenset(BooleanField.TRUE_VALUES | {'Enabled'})
    FALSE_VALUES = frozenset(BooleanField.FALSE_VALUES | {'Disabled'})


class EbayListSerializer(serializers.ListSerializer):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = [data]
        return super(EbayListSerializer, self).to_internal_value(data)


class EbayNullableIntegerField(serializers.IntegerField):
    def to_internal_value(self, data):
        if data == 'null':
            return None
        return super(EbayNullableIntegerField, self).to_internal_value(data)