# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, PaymentMethodModel, \
    DurationModel
from inventorum.ebay.apps.categories.services import EbayCategoriesScraper, EbayFeaturesScraper
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestScrappingCategories(EbayAuthenticatedAPITestCase):
    def test_it(self):
        # Create first one to prove categories scrapper removes them
        CategoryModel.objects.create(
            name="Test",
            external_id="123",
            external_parent_id=None,
            country="DE"
        )
        with EbayAuthenticatedAPITestCase.vcr.use_cassette("ebay_get_level_limited_categories_with_features.json"):
            # First root node of ebay has 2012 children
            service = EbayCategoriesScraper(self.ebay_token, limit_root_nodes=1, limit_nodes_level=2)
            service.fetch_all()

        categories = CategoryModel.objects.all()
        # Doubled because AT & DE (31 + 1 [root node] * 2 = 64)
        self.assertEqual(categories.count(), 64)
        # 2 root nodes because AT & DE
        self.assertEqual(CategoryModel.tree_objects.root_nodes().count(), 2)

        # Make sure it was soft deleted
        self.assertEqual(CategoryModel.admin_objects.count(), 65)

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

        features_service = EbayFeaturesScraper(self.ebay_token)
        features_service.fetch_all()

        self.assertEqual(CategoryFeaturesModel.objects.count(), 64)

        for category in CategoryModel.objects.all():
            features = category.features
            self.assertGreater(features.payment_methods.count(), 0)
            self.assertGreater(features.durations.count(), 0)

        # Models should not be duplicated!
        self.assertEqual(PaymentMethodModel.objects.count(), 10)
        self.assertEqual(DurationModel.objects.count(), 5)