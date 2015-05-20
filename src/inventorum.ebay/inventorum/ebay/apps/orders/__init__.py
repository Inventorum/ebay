# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import math
import random

from inventorum.ebay.lib.ebay.data import BuyerPaymentMethodCodeType


log = logging.getLogger(__name__)


class CorePaymentMethod(object):
    """
    Provides consts and mapping to ebay payment methods for *supported* core payment methods
    """
    PAYPAL = "4"
    BANK_TRANSFER = "6"

    CHOICES = (
        (PAYPAL, "PayPal"),
        (BANK_TRANSFER, "Bank Transfer")
    )

    EBAY_PAYMENT_CODE_TYPE_MAPPING = {
        BuyerPaymentMethodCodeType.PayPal: PAYPAL,
        BuyerPaymentMethodCodeType.MoneyXferAccepted: BANK_TRANSFER,
        BuyerPaymentMethodCodeType.MoneyXferAcceptedInCheckout: BANK_TRANSFER
    }

    @classmethod
    def from_ebay_payment_method(cls, ebay_payment_method):
        """
        Maps the given `ebay_payment_method` to an inventorum core payment method

        :param ebay_payment_method: An ebay payment method, see `BuyerPaymentMethodCodeType`
        :type ebay_payment_method: unicode

        :return: ebay_payment_method: The mapped core payment method or None if not supported/not yet mapped
        :rtype: unicode
        """
        return cls.EBAY_PAYMENT_CODE_TYPE_MAPPING.get(ebay_payment_method)


class PickupCode(object):
    LENGTH = 12  # length of redeem code
    # for `randint` we need a max value for this length, e.g for length of 6: 10 ^ 6 - 1 == 999999
    MAX_INT = int(math.pow(10, LENGTH) - 1)
    # no leading zeros, we want to start with: 10 ^ (6 - 1) = 100000
    MIN_INT = int(math.pow(10, LENGTH-1))

    @classmethod
    def generate_random(cls):
        """
        :rtype: unicode
        """
        return unicode(random.randint(PickupCode.MIN_INT, PickupCode.MAX_INT))
