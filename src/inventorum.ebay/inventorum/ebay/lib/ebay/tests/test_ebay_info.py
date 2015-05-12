# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from pytz import UTC

from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.ebay.data.categories.features import EbayFeature, EbayFeatureDefinition
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.lib.ebay.info import EbayInfo
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestEbayInfo(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("ebay_get_user.yaml")
    def test_it(self):
        auth = EbayInfo(self.ebay_token)
        # Get current authenticated user
        user = auth.get_user()
        log.debug('Got user: %s', user)
        self.assertEqual(user.email, 'tech+ebay@inventorum.com')
        self.assertEqual(user.id_verified, False)
        self.assertEqual(user.status, 'Confirmed')
        self.assertEqual(user.user_id, 'newmade')
        self.assertEqual(user.seller_info.qualifies_for_b2b_vat, False)
        self.assertEqual(user.seller_info.store_owner, False)
        self.assertEqual(user.registration_date, datetime(2015, 3, 31, 8, 57, 26, tzinfo=UTC))

        address = user.registration_address
        self.assertEqual(address.name, 'John Newman')
        self.assertEqual(address.street, None)
        self.assertEqual(address.street1, None)
        self.assertEqual(address.city, 'default')
        self.assertEqual(address.country, 'DE')
        self.assertEqual(address.postal_code, 'default')

    @EbayTest.use_cassette("ebay_get_site_defaults.yaml")
    def test_it(self):
        auth = EbayInfo(self.ebay_token)
        site_defaults = auth.get_site_defaults()
        self.assertIsInstance(site_defaults, EbayFeature)
        self.assertIsInstance(site_defaults.definition, EbayFeatureDefinition)

        durations = site_defaults.definition.durations
        self.assertIsNone(durations)

        durations = site_defaults.details.durations
        self.assertIsNone(durations)
        self.assertIsNone(site_defaults.details.category_id)

        self.assertEqual(site_defaults.details.payment_methods, [
            'PayPal',
            'Moneybookers',
            'CashOnPickup',
            'MoneyXferAcceptedInCheckout',
            'MoneyXferAccepted',
            'COD',
            'PaymentSeeDescription',
            'CCAccepted',
            'Escrow',
            'StandardPayment'
        ])