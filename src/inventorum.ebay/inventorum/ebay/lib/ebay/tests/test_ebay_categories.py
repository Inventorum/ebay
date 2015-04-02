# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay.categories import EbayCategories
from inventorum.ebay.lib.ebay.data import EbayCategory
from inventorum.ebay.lib.ebay.tests import EbayClassTestCase
from django.conf import settings
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class EbayCategoriesTest(EbayClassTestCase):
    def test_init(self):
        ebay = EbayCategories(None)


        self.connection_mock.assert_any_call(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                                             certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                                             debug=settings.DEBUG, timeout=20, config_file=None,
                                             compatibility=911, version=911, parallel=None)
        # Make sure parallel object was created
        self.connection_mock.assert_any_call(appid=settings.EBAY_APPID, devid=settings.EBAY_DEVID,
                                             certid=settings.EBAY_CERTID, domain=settings.EBAY_DOMAIN,
                                             debug=settings.DEBUG, timeout=20, config_file=None,
                                             compatibility=911, version=911, parallel=self.parallel_mock)

        ebay.get_attributes_for_categories([1, 2, 3])
        self.parallel_mock.wait.assert_called_with(ebay.timeout)


class EbayApiCategoriesTest(EbayAuthenticatedAPITestCase):
    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_get_all_categories.json")
    def test_getting_categories(self):
        ebay = EbayCategories(self.ebay_token)
        categories = ebay.get_categories()

        first_category = None
        for category in categories:
            if first_category is None:
                first_category = category
            self.assertIsInstance(category, EbayCategory)

        self.assertEqual(first_category.category_id, '353')
        self.assertEqual(first_category.name, 'Antiquit\xe4ten & Kunst')
        self.assertEqual(first_category.parent_id, None)
        self.assertEqual(first_category.virtual, False)
        self.assertEqual(first_category.expired, False)
        self.assertEqual(first_category.b2b_vat_enabled, False)
        self.assertEqual(first_category.leaf, False)
        self.assertEqual(first_category.best_offer_enabled, True)
        self.assertEqual(first_category.auto_pay_enabled, True)
        self.assertEqual(first_category.item_lot_size_disabled, False)
