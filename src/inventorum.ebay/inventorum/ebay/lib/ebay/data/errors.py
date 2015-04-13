# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields


class EbayError(object):
    def __init__(self, code, classification, long_message, severity_code, short_message):
        self.code = code
        self.classification = classification
        self.long_message = long_message
        self.severity_code = severity_code
        self.short_message = short_message

    def __unicode__(self):
        return self.long_message

    @classmethod
    def create_from_data(cls, data):
        """
        Creates EbayError from dict
        :rtype: EbayError
        :type data: dict
        """
        serializer = EbayErrorDeserializer(data=data)
        return serializer.build()


class EbayErrorDeserializer(POPOSerializer):
    ErrorCode = fields.IntegerField(source='code')
    ErrorClassification = fields.CharField(source='classification')
    LongMessage = fields.CharField(source='long_message')
    SeverityCode = fields.CharField(source='severity_code')
    ShortMessage = fields.CharField(source='short_message')

    class Meta:
        model = EbayError

