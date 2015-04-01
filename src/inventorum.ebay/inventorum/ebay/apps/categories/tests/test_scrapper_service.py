# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.apps.categories.services import EbayCategoriesScrapper
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestScrappingCategories(EbayAuthenticatedAPITestCase):
    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_get_all_categories.json")
    def test_it(self):
        service = EbayCategoriesScrapper(self.ebay_token, limit_root_nodes=1)
        service.fetch_all()

        categories = CategoryModel.objects.all()
        self.assertEqual(categories.count(), 2013)
        self.assertEqual(CategoryModel.objects.root_nodes().count(), 1)