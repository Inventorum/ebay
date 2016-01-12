# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from inventorum_ebay.apps.orders import CorePaymentMethod
from inventorum_ebay.lib.ebay.data import BuyerPaymentMethodCodeType

from inventorum_ebay.tests.testcases import UnitTestCase


log = logging.getLogger(__name__)


class TestCorePaymentMethodMapping(UnitTestCase):

    def test_mapping(self):

        self.assertEqual(CorePaymentMethod.from_ebay_payment_method(BuyerPaymentMethodCodeType.PayPal),
                         CorePaymentMethod.PAYPAL)

        self.assertEqual(CorePaymentMethod.from_ebay_payment_method(BuyerPaymentMethodCodeType.MoneyXferAccepted),
                         CorePaymentMethod.BANK_TRANSFER)

        self.assertEqual(CorePaymentMethod.from_ebay_payment_method(BuyerPaymentMethodCodeType.MoneyXferAcceptedInCheckout),
                         CorePaymentMethod.BANK_TRANSFER)

        # unmapped/unknown should yield None
        self.assertIsNone(CorePaymentMethod.from_ebay_payment_method("SomeUnknownEbayPaymentMethod"))
