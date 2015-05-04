# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.data import EbayBooleanField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


class EbayEventType(object):
    READY_FOR_PICKUP = 'EBAY.ORDER.READY_FOR_PICKUP'
    PICKED_UP = 'EBAY.ORDER.PICKEDUP'
    RETURNED = 'EBAY.ORDER.RETURNED'


class EbayEventBase(object):
    def __init__(self, order_id, seller_id=None, error=None):
        """
        :type order_id: unicode
        :type seller_id: unicode
        :type inventorum.ebay.lib.ebay.data.events.EbayEventError: error
        :return:
        """
        self.order_id = order_id
        self.seller_id = seller_id
        self.error = error

    @property
    def payload(self):
        data = {
            'ebayOrderId': self.order_id
        }
        if self.seller_id is not None:
            data['ebaySellerId'] = self.seller_id

        return data

    @property
    def type(self):
        raise NotImplementedError


class EbayEventReadyForPickup(EbayEventBase):
    type = EbayEventType.READY_FOR_PICKUP


class EbayEventError(object):
    class Deserializer(POPOSerializer):
        class Meta:
            model = None
        message = serializers.CharField()
        errorId = serializers.IntegerField(source='error_id')
        exceptionId = serializers.CharField(source='exception_id')
        domain = serializers.CharField()
        category = serializers.CharField()
        severity = serializers.CharField()

    def __init__(self, message, error_id, exception_id, domain, category, severity):
        self.message = message
        self.error_id = error_id
        self.exception_id = exception_id
        self.domain = domain
        self.category = category
        self.severity = severity

    def __unicode__(self):
        return "[{severity}] (code: {code}, domain: {domain}) {message}".\
            format(severity=self.severity, code=self.error_id, domain=self.domain, message=self.message)

EbayEventError.Deserializer.Meta.model = EbayEventError


class EbayEventResponse(object):
    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        ackValue = EbayBooleanField(source='ack')
        _errors = EbayEventError.Deserializer(source='errors', many=True, required=False, allow_null=True)


        def to_internal_value(self, data):
            data['_errors'] = data.get('errorMessage', {}).get('error')
            return super(EbayEventResponse.Deserializer, self).to_internal_value(data)

    def __init__(self, ack, errors=None):
        self.ack = ack
        self.errors = errors


EbayEventResponse.Deserializer.Meta.model = EbayEventResponse