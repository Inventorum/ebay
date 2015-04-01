# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.ebay.info import EbayInfo
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestEbayInfo(EbayAuthenticatedAPITestCase):

    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_get_user.json")
    def test_it(self):
        auth = EbayInfo(self.ebay_token)
        # Get current authenticated user
        user = auth.get_user()
        log.debug('Got user: %s', user)
        self.assertEqual(user.email, 'tech+ebay@inventorum.com')
        self.assertEqual(user.id_verified, False)
        self.assertEqual(user.status, 'Confirmed')
        self.assertEqual(user.user_id, 'newmade')
        self.assertEqual(user.qualifies_for_b2b_vat, False)
        self.assertEqual(user.store_owner, False)
        self.assertEqual(user.registration_date, datetime(2015, 3, 31, 8, 57, 26))

        address = user.registration_address
        self.assertEqual(address.name, 'John Newman')
        self.assertEqual(address.street, None)
        self.assertEqual(address.street1, None)
        self.assertEqual(address.city, 'default')
        self.assertEqual(address.country, 'DE')
        self.assertEqual(address.postal_code, 'default')