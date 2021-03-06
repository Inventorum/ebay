# encoding: utf-8
from __future__ import absolute_import, unicode_literals


class EbayCompleteSaleShipment(object):
    def __init__(self, carrier_used, tracking_number):
        self.carrier_used = carrier_used
        self.tracking_number = tracking_number

    def dict(self):
        return {
            'ShipmentTrackingDetails': {
                'ShipmentTrackingNumber': self.tracking_number,
                'ShippingCarrierUsed': self.carrier_used,
            }
        }


class CheckoutStatusType(object):
    COMPLETE = 'Complete'
    INCOMPLETE = 'Incomplete'
    PENDING = 'Pending'


class PaymentMethodType(object):
    BANK_TRANSFER = 'MoneyXferAccepted'
    BANK_TRANSFER_IN_CHECKOUt = 'MoneyXferAcceptedInCheckout'