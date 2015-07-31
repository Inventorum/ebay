# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from django.conf import settings

from inventorum.ebay.tests import EbayTest, Countries
from inventorum.ebay.lib.ebay.categories import EbayCategories
from inventorum.ebay.lib.ebay.data import ProductIdentiferEnabledCodeType
from inventorum.ebay.lib.ebay.data.categories import EbayCategory
from inventorum.ebay.lib.ebay.data.categories.features import EbayFeature, EbayFeatureDefinition, \
    EbayListingDurationDefinition
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class EbayApiCategoriesTest(EbayAuthenticatedAPITestCase):

    @EbayTest.use_cassette("ebay_get_all_categories.yaml")
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

    @EbayTest.use_cassette('ebay_check_features_downloading.yaml')
    def test_ebay_categories_features(self):
        ebay = EbayCategories(self.ebay_token)
        features = {cat_id: ebay.get_features_for_category(cat_id) for cat_id in ['353', '64540', '163769']}
        self.assertEqual(len(features), 3)
        feature = features['353']

        self.assertIsInstance(feature, EbayFeature)
        self.assertEqual(feature.details.category_id, '353')

        log.debug('Durations: %s', feature.details.durations)
        self.assertEqual(len(feature.details.durations), 9)
        self.assertEqual(len(feature.details.durations_dict), 9)

        payment_methods = [
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
        ]

        self.assertEqual(feature.details.durations_dict['FixedPriceItem'], 8)
        self.assertEqual(feature.details.payment_methods, payment_methods)
        self.assertTrue(feature.details.item_specifics_enabled)
        self.assertFalse(feature.details.variations_enabled)
        self.assertEqual(feature.payment_methods, payment_methods)
        self.assertEqual(feature.details.ean_enabled, ProductIdentiferEnabledCodeType.Disabled)

        second_feature = features['64540']

        self.assertIsInstance(second_feature, EbayFeature)
        self.assertEqual(second_feature.details.category_id, '64540')

        self.assertEqual(len(second_feature.details.durations), 9)
        self.assertEqual(len(second_feature.details.durations_dict), 9)

        self.assertEqual(second_feature.details.durations_dict['FixedPriceItem'], 8)
        self.assertEqual(second_feature.details.payment_methods, payment_methods)
        self.assertTrue(second_feature.details.item_specifics_enabled)
        self.assertFalse(second_feature.details.variations_enabled)
        self.assertEqual(second_feature.payment_methods, payment_methods)
        self.assertEqual(feature.details.ean_enabled, ProductIdentiferEnabledCodeType.Disabled)

        feature_definition = feature.definition
        self.assertIsInstance(feature_definition, EbayFeatureDefinition)
        self.assertEqual(len(feature_definition.durations), 6)

        for duration in feature_definition.durations:
            self.assertIsInstance(duration, EbayListingDurationDefinition)

        # So in Category 353 we got SetId: 8 for FixedPriceItem, lets check if this is in definitions
        self.assertIsInstance(feature_definition.durations_dict[8], EbayListingDurationDefinition)
        log.debug('Original data: %s', POPOSerializer.extract_original_data(feature_definition.durations_dict[8]))
        self.assertEqual(feature_definition.durations_dict[8].durations, ['Days_3', 'Days_5', 'Days_7', 'Days_10',
                                                                          'Days_30'])

        self.assertEqual(feature.get_duration_list_by_type('FixedPriceItem'), ['Days_3', 'Days_5', 'Days_7', 'Days_10',
                                                                               'Days_30'])

        third_feature = features['163769']
        self.assertEqual(third_feature.details.ean_enabled, ProductIdentiferEnabledCodeType.Required)

    @EbayTest.use_cassette("ebay_get_categories_specifics.yaml")
    def test_ebay_category_specifics(self):
        leaf_categories = ['167050', '19351', '167049', '167046', '81915', '167044', '167045', '167048', '64541',
                           '86146', '157120', '157121', '168696', '168694', '168695', '92921', '68180', '68181',
                           '78366', '157119']

        ebay = EbayCategories(self.ebay_token)
        specifics = ebay.get_specifics_for_categories(leaf_categories)
        self.assertEqual(len(leaf_categories), len(specifics))

        for category_id in leaf_categories:
            self.assertIn(category_id, category_id)

        some_specifics = specifics['167050']
        self.assertEqual(some_specifics.category_id, '167050')
        self.assertEqual(len(some_specifics.name_recommendations), 2)

        first_name_rn = some_specifics.name_recommendations[0]
        self.assertEqual(first_name_rn.name, 'Anzahl der Einheiten')
        self.assertEqual(first_name_rn.help_text, None)
        self.assertEqual(first_name_rn.help_url, None)
        self.assertFalse(first_name_rn.is_required)
        self.assertEqual(first_name_rn.validation_rules.selection_mode, 'FreeText')
        self.assertEqual(first_name_rn.validation_rules.value_type, 'Text')
        self.assertFalse(first_name_rn.validation_rules.can_use_in_variations)

        first_value_recommendations = first_name_rn.value_recommendations
        self.assertEqual(len(first_value_recommendations), 0)

        second_name_rn = some_specifics.name_recommendations[1]
        self.assertEqual(second_name_rn.name, 'Maßeinheit')
        self.assertEqual(second_name_rn.help_text, None)
        self.assertEqual(second_name_rn.help_url, None)
        self.assertFalse(second_name_rn.is_required)
        self.assertEqual(second_name_rn.validation_rules.selection_mode, 'SelectionOnly')
        self.assertEqual(second_name_rn.validation_rules.value_type, 'Text')
        self.assertFalse(second_name_rn.validation_rules.can_use_in_variations)

        second_value_recommendations = second_name_rn.value_recommendations
        self.assertEqual(len(second_value_recommendations), 10)
        values = [r.value for r in second_value_recommendations]
        self.assertEqual(values, ['kg', '100 g', '10 g', 'L', '100 ml', '10 ml', 'm³', 'm', 'm²', 'Einheit'])

    @EbayTest.use_cassette("ebay_get_category_suggestions.yaml")
    def test_get_suggested_categories(self):
        ebay = EbayCategories(self.ebay_token)
        response = ebay.get_suggested_categories("iPhone")

        self.assertEqual(response.category_count, 10)
        self.assertEqual(len(response.suggested_categories), 10)

        self.assertEqual(sum([suggested_category.percent_item_found
                              for suggested_category in response.suggested_categories]), 100)


    @EbayTest.use_cassette("ebay_get_specfic_for_category_162499_AT.yaml")
    def test_specifics_for_one_category(self):
        token = self.ebay_token
        token.site_id = settings.EBAY_SUPPORTED_SITES[Countries.AT]
        ebay = EbayCategories(token)
        specifics = ebay.get_specifics_for_categories([162499])
        self.assertEqual(len(specifics), 1)