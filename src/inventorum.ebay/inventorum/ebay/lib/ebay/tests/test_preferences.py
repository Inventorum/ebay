# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data import SellerProfileCodeType

from inventorum.ebay.lib.ebay.preferences import EbayPreferences
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


log = logging.getLogger(__name__)


class TestEbayPreferences(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette('ebay_get_user_preferences.yaml')
    def test_get_user_preferences(self):
        ebay_preferences = EbayPreferences(self.ebay_token)
        user_preferences = ebay_preferences.get_user_preferences()

        supported_seller_profiles = user_preferences.seller_profile_preferences.supported_seller_profiles
        self.assertTrue(len(supported_seller_profiles) > 0, 'There should be at least one configured seller profile')

        return_profiles = [p for p in supported_seller_profiles if p.profile_type == SellerProfileCodeType.RETURN_POLICY
                           and p.category_group.is_default]
        self.assertTrue(len(return_profiles) > 0, 'There should be at least one default return policy profile')

        self.assertEqual(return_profiles[0].profile_id, '70043489023', 'Hardcoded id from eBay account, may change :)')
