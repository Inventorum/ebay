# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, IntegerField, BooleanField, DateTimeField, ListField


class EbayParser(object):
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

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

