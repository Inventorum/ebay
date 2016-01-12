# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging

from inventorum_ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, PaymentMethodModel, \
    DurationModel, CategorySpecificModel
from inventorum_ebay.apps.categories.services import EbayCategoriesScraper, EbayFeaturesScraper, EbaySpecificsScraper
from inventorum_ebay.tests import EbayTest
from inventorum_ebay.apps.categories.tests.factories import CategoryFactory
from inventorum_ebay.apps.products.models import EbayProductModel
from inventorum_ebay.apps.products.tests.factories import EbayProductFactory
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestEbayCategoryScrapers(EbayAuthenticatedAPITestCase):

    def test_it(self):
        # Create first one to prove categories scrapper removes them
        category_to_be_deleted = CategoryModel.objects.create(
            name="Test",
            external_id="123",
            external_parent_id=None,
            country="DE"
        )

        product = EbayProductFactory.create(category=category_to_be_deleted)

        with EbayTest.use_cassette("ebay_get_level_limited_categories_with_features.yaml"):
            # First root node of ebay has 2012 children
            service = EbayCategoriesScraper(self.ebay_token, limit_root_nodes=1, limit_nodes_level=2)
            service.fetch_all()

        categories = CategoryModel.objects.all()
        # Doubled because AT & DE (31 + 1 [root node] * 2 = 64)
        self.assertEqual(categories.count(), 64)
        # 2 root nodes because AT & DE
        self.assertEqual(CategoryModel.objects.root_nodes().count(), 2)

        root_nodes = CategoryModel.objects.root_nodes().order_by('country')
        root_category = root_nodes.first()
        self.assertEqual(root_category.name, "Antiquit\xe4ten & Kunst")
        self.assertEqual(root_category.external_id, "353")
        self.assertEqual(root_category.external_parent_id, None)
        self.assertEqual(root_category.b2b_vat_enabled, False)
        self.assertEqual(root_category.best_offer_enabled, True)
        self.assertEqual(root_category.auto_pay_enabled, True)
        self.assertEqual(root_category.item_lot_size_disabled, False)
        self.assertEqual(root_category.ebay_leaf, False)
        self.assertEqual(root_category.country, "AT")

        # AT root category
        root_category = root_nodes.last()
        self.assertEqual(root_category.name, "Antiquit\xe4ten & Kunst")
        self.assertEqual(root_category.external_id, "353")
        self.assertEqual(root_category.external_parent_id, None)
        self.assertEqual(root_category.b2b_vat_enabled, False)
        self.assertEqual(root_category.best_offer_enabled, True)
        self.assertEqual(root_category.auto_pay_enabled, True)
        self.assertEqual(root_category.item_lot_size_disabled, False)
        self.assertEqual(root_category.ebay_leaf, False)
        self.assertEqual(root_category.country, "DE")

        categories = CategoryModel.objects.all()
        for category in categories:
            descendants = category.get_descendants(include_self=True)
            for descendant in descendants:
                self.assertEqual(descendant.country, category.country)

        with self.assertRaises(CategoryModel.DoesNotExist):
            CategoryModel.objects.get(pk=category_to_be_deleted.pk)

        product = EbayProductModel.objects.get(pk=product.pk)
        self.assertIsNone(product.category)

    @EbayTest.use_cassette("ebay_test_scraper_features.yaml")
    def test_features(self):
        with EbayTest.use_cassette("ebay_get_leaf_categories.yaml"):
            # First root node of ebay has 2012 children
            service = EbayCategoriesScraper(self.ebay_token, only_leaf=True, limit=20)
            service.fetch_all()

        leaf_categories = CategoryModel.objects.filter(ebay_leaf=True)
        self.assertGreater(leaf_categories.count(), 0)
        log.debug('Leaf categories external ids: %s', [l.external_id for l in leaf_categories])

        features_service = EbayFeaturesScraper(self.ebay_token)
        features_service.fetch_all()

        self.assertEqual(CategoryFeaturesModel.objects.count(), 40)  # limit * countries = 20 * 2 = 40

        for category in CategoryModel.objects.all():
            features = category.features
            self.assertGreater(features.payment_methods.count(), 0)
            self.assertGreater(features.durations.count(), 0)

        last_feature = leaf_categories.last().features
        self.assertEqual(last_feature.item_specifics_enabled, True)
        self.assertEqual(last_feature.variations_enabled, False)
        self.assertEqual(last_feature.ean_enabled, False)
        self.assertEqual(last_feature.ean_required, False)

        # Models should not be duplicated!
        self.assertEqual(PaymentMethodModel.objects.count(), 10)
        self.assertEqual(DurationModel.objects.count(), 5)

    @EbayTest.use_cassette("ebay_test_scraper_features_ean.yaml")
    def test_features_ean(self):
        common_category_attrs = dict(ebay_leaf=True, features=None)

        category_ean_disabled = CategoryFactory.create(external_id=17145, name="EAN disabled", **common_category_attrs)
        category_ean_enabled = CategoryFactory.create(external_id=147915, name="EAN enabled", **common_category_attrs)
        category_ean_required = CategoryFactory.create(external_id=163769, name="EAN required", **common_category_attrs)

        features_service = EbayFeaturesScraper(self.ebay_token)
        features_service.fetch_all()

        self.assertFalse(category_ean_disabled.features.ean_enabled)
        self.assertFalse(category_ean_disabled.features.ean_required)

        self.assertTrue(category_ean_enabled.features.ean_enabled)
        self.assertFalse(category_ean_enabled.features.ean_required)

        self.assertTrue(category_ean_required.features.ean_enabled)
        self.assertTrue(category_ean_required.features.ean_required)

    @EbayTest.use_cassette("ebay_test_scraper_specifics.yaml")
    def test_specifics(self):
        with EbayTest.use_cassette("ebay_get_leaf_categories.yaml"):
            # First root node of ebay has 2012 children
            service = EbayCategoriesScraper(self.ebay_token, only_leaf=True, limit=20)
            service.fetch_all()

        leaf_categories = CategoryModel.objects.filter(ebay_leaf=True)
        self.assertGreater(leaf_categories.count(), 0)
        log.debug('Leaf categories external ids: %s', [l.external_id for l in leaf_categories])

        features_service = EbayFeaturesScraper(self.ebay_token)
        features_service.fetch_all()

        specifics_service = EbaySpecificsScraper(self.ebay_token)
        specifics_service.fetch_all()

        self.assertEqual(CategorySpecificModel.objects.count(), 80)

        some_category = CategoryModel.objects.get(external_id='167050', country='DE')
        specifics = some_category.specifics.all()

        self.assertEqual(specifics.count(), 2)

        first_specific = specifics[0]
        self.assertEqual(first_specific.name, 'Anzahl der Einheiten')
        self.assertIsNone(first_specific.help_text)
        self.assertIsNone(first_specific.help_url)
        self.assertFalse(first_specific.is_required)
        self.assertEqual(first_specific.selection_mode, 'FreeText')
        self.assertEqual(first_specific.value_type, 'Text')
        self.assertFalse(first_specific.can_use_in_variations)
        self.assertTrue(first_specific.can_use_own_values)

        self.assertEqual(first_specific.values.all().count(), 0)

        second_specific = specifics[1]
        self.assertEqual(second_specific.name, 'Maßeinheit')
        self.assertEqual(second_specific.help_text, None)
        self.assertEqual(second_specific.help_url, None)
        self.assertFalse(second_specific.is_required)
        self.assertEqual(second_specific.selection_mode, 'SelectionOnly')
        self.assertEqual(second_specific.value_type, 'Text')
        self.assertFalse(second_specific.can_use_in_variations)
        self.assertFalse(second_specific.can_use_own_values)

        values = second_specific.values.all()
        self.assertEqual(values.count(), 10)

        values_values = [v.value for v in values]
        self.assertEqual(values_values, ['kg', '100 g', '10 g', 'L', '100 ml', '10 ml', 'm³', 'm', 'm²', 'Einheit'])
