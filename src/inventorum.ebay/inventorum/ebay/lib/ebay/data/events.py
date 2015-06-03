# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.data import EbayBooleanField
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


class EbayEventType(object):
    READY_FOR_PICKUP = 'EBAY.ORDER.READY_FOR_PICKUP'
    PICKED_UP = 'EBAY.ORDER.PICKEDUP'
    RETURNED = 'EBAY.ORDER.RETURNED'
    CANCELED = 'EBAY.ORDER.PICKUP_CANCELED'


class EbayEventBase(object):
    def __init__(self, order_id, seller_id=None):
        """
        :type order_id: unicode
        :type seller_id: unicode
        :type inventorum.ebay.lib.ebay.data.events.EbayEventError: error
        :return:
        """
        self.order_id = order_id
        self.seller_id = seller_id

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

    def __init__(self, order_id, pickup_note=None, pickup_id=None, seller_id=None):
        self.pickup_note = pickup_note
        self.pickup_id = pickup_id
        super(EbayEventReadyForPickup, self).__init__(order_id=order_id, seller_id=seller_id)

    @property
    def payload(self):
        payload = super(EbayEventReadyForPickup, self).payload

        if self.pickup_id is not None:
            payload['notifierPickupId'] = self.pickup_id

        if self.pickup_note is not None:
            payload['notifierPickupNote'] = self.pickup_note

        return payload


class EbayEventPickedUp(EbayEventBase):
    type = EbayEventType.PICKED_UP


class EbayEventCanceled(EbayEventBase):
    class CancellationType(object):
        OUT_OF_STOCK = 'OUT_OF_STOCK'
        BUYER_NO_SHOW = 'BUYER_NO_SHOW'
        BUYER_REFUSED = 'BUYER_REFUSED'

    class RefundType(object):
        EBAY = 'EBAY'

    type = EbayEventType.CANCELED

    def __init__(self, order_id, cancellation_type, refund_type=RefundType.EBAY, pickup_note=None, pickup_id=None,
                 seller_id=None):
        self.cancellation_type = cancellation_type
        self.refund_type = refund_type
        self.pickup_note = pickup_note
        self.pickup_id = pickup_id
        super(EbayEventCanceled, self).__init__(order_id=order_id, seller_id=seller_id)

    @property
    def payload(self):
        payload = super(EbayEventCanceled, self).payload
        payload['notifierCancelType'] = self.cancellation_type
        payload['notifierRefundType'] = self.refund_type

        if self.pickup_id is not None:
            payload['notifierPickupId'] = self.pickup_id

        if self.pickup_note is not None:
            payload['notifierPickupNote'] = self.pickup_note

        return payload


class EbayEventReturnedItem(object):
    def __init__(self, item_id, transaction_id, refund_quantity, refund_amount, currency='EUR'):
        self.item_id = item_id
        self.transaction_id = transaction_id
        self.refund_quantity = refund_quantity
        self.refund_amount = refund_amount
        self.currency = currency

    @property
    def payload(self):
        return {
            'eBayItemId': self.item_id,
            'eBayTransactionId': self.transaction_id,
            'notifierRefundQuantity': self.refund_quantity,
            'notifierRefundAmount': self.refund_amount,
            'notifierRefundCurrency': self.currency,
        }


class EbayEventReturned(EbayEventBase):

    class RefundType(object):
        EBAY = 'EBAY'
        STORE_CREDIT = 'STORE_CREDIT'

    type = EbayEventType.RETURNED

    def __init__(self, order_id, refund_amount, refund_type, items, refund_id=None, refund_note=None, currency='EUR',
                 seller_id=None):
        self.refund_amount = refund_amount
        self.currency = currency
        self.refund_type = refund_type
        self.refund_note = refund_note
        self.refund_id = refund_id
        self.items = items
        super(EbayEventReturned, self).__init__(order_id=order_id, seller_id=seller_id)

    @property
    def payload(self):
        payload = super(EbayEventReturned, self).payload
        payload['notifierTotalRefundAmount'] = self.refund_amount
        payload['notifierTotalRefundCurrency'] = self.currency
        payload['notifierRefundType'] = self.refund_type
        payload['refundLineItems'] = [i.payload for i in self.items]

        if self.refund_note is not None:
            payload['notifierRefundNote'] = self.refund_note

        if self.refund_id is not None:
            payload['notifierRefundId'] = self.refund_id

        return payload


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
            # Tricky part to be able to easy fetch list of errors (errorMessage.error[]) and we want to access it
            # directly
            data['_errors'] = data.get('errorMessage', {}).get('error')
            return super(EbayEventResponse.Deserializer, self).to_internal_value(data)

    def __init__(self, ack, errors=None):
        self.ack = ack
        self.errors = errors


EbayEventResponse.Deserializer.Meta.model = EbayEventResponse