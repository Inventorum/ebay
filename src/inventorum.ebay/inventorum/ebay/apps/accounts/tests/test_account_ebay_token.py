# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.conf import settings
from inventorum.ebay.lib.ebay.info import EbayInfo
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestAccountEbayToken(EbayAuthenticatedAPITestCase):

    def test_if_send_correct_site_id(self):
        with EbayAuthenticatedAPITestCase.vcr.use_cassette('test_account_ebay_token.json') as cass:
            ebay_token_db = self.account.token
            ebay_token_db.site_id = settings.EBAY_SUPPORTED_SITES['AT']
            ebay_token_db.save()

            info = EbayInfo(ebay_token_db.ebay_object)
            response = info.get_user()

            requests = cass.requests
            self.assertEqual(requests[0].headers['X-EBAY-API-SITEID'], 16)