# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.apps.categories.services import EbayCategoriesScrapper
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestScrappingCategories(EbayAuthenticatedAPITestCase):
    @EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_get_all_categories.json", record_mode='new_episodes')
    def test_it(self):
        # Create first one to prove categories scrapper removes them
        CategoryModel.objects.create(
            name="Test",
            external_id="123",
            external_parent_id=None,
            country="DE"
        )

        # First root node of ebay has 2012 children
        service = EbayCategoriesScrapper(self.ebay_token, limit_root_nodes=1)
        service.fetch_all()

        categories = CategoryModel.objects.all()
        # Doubled because AT & DE (2012 + 1 [root node] = 4026)
        self.assertEqual(categories.count(), 4026)
        # 2 root nodes because AT & DE
        self.assertEqual(CategoryModel.objects.root_nodes().count(), 2)

        # Make sure it was soft deleted
        self.assertEqual(CategoryModel.admin_objects.count(), 4027)

        root_category = CategoryModel.tree_objects.root_nodes().first()
        self.assertEqual(root_category.name, "Antiquit\xe4ten & Kunst")
        self.assertEqual(root_category.external_id, "353")
        self.assertEqual(root_category.external_parent_id, None)
        self.assertEqual(root_category.b2b_vat_enabled, False)
        self.assertEqual(root_category.best_offer_enabled, True)
        self.assertEqual(root_category.auto_pay_enabled, True)
        self.assertEqual(root_category.item_lot_size_disabled, False)
        self.assertEqual(root_category.ebay_leaf, False)
        self.assertEqual(root_category.country, "DE")

        # AT root category
        root_category = CategoryModel.tree_objects.root_nodes().last()
        self.assertEqual(root_category.name, "Antiquit\xe4ten & Kunst")
        self.assertEqual(root_category.external_id, "353")
        self.assertEqual(root_category.external_parent_id, None)
        self.assertEqual(root_category.b2b_vat_enabled, False)
        self.assertEqual(root_category.best_offer_enabled, True)
        self.assertEqual(root_category.auto_pay_enabled, True)
        self.assertEqual(root_category.item_lot_size_disabled, False)
        self.assertEqual(root_category.ebay_leaf, False)
        self.assertEqual(root_category.country, "AT")