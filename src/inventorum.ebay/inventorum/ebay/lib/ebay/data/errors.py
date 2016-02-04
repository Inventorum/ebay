# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.translation import ugettext
from inventorum.ebay.lib.ebay.data import EbayNullableIntegerField, EbayNullableDecimalField, EbayListSerializer
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields
from rest_framework.fields import IntegerField
from rest_framework.serializers import Serializer


class EbayErrorCode(object):
    """
    Mapping of short message to error code, so we can see directly in code what is it about.
    """
    TheAuctionHasBeenClosed = 1047


class EbayError(object):
    def __init__(self, code, classification, long_message, severity_code, short_message, parameters=None):
        self.code = code
        self.classification = unicode(classification)
        self.long_message = unicode(long_message)
        self.severity_code = unicode(severity_code)
        self.short_message = unicode(short_message)
        self.parameters = parameters or []
        self.parameters = [p.get('Value', p) for p in self.parameters]

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

    def api_dict(self):
        return EbayCoreApiSerializer(instance=self).data


class EbayFatalError(EbayError):
    CODE = -1

    def __init__(self, error_id):
        super(EbayFatalError, self).__init__(
            code=self.CODE,
            classification="ApiError",
            long_message=ugettext("Something went wrong, please try again later."),
            severity_code="FatalError",
            short_message=ugettext("Fatal error (%(error_id)s)") %
                          {'error_id': error_id})


class EbayErrorDeserializer(POPOSerializer):
    ErrorCode = EbayNullableDecimalField(source='code', max_digits=10, decimal_places=2)
    ErrorClassification = fields.CharField(source='classification')
    LongMessage = fields.CharField(source='long_message')
    SeverityCode = fields.CharField(source='severity_code')
    ShortMessage = fields.CharField(source='short_message')
    ErrorParameters = EbayListSerializer(source='parameters', child=fields.DictField(), required=False)

    class Meta:
        model = EbayError


class EbayCoreApiSerializer(Serializer):
    code = fields.IntegerField()
    long_message = fields.CharField()
    short_message = fields.CharField()
    severity_code = fields.CharField()
    classification = fields.CharField()
    parameters = fields.ListField(child=fields.CharField())
