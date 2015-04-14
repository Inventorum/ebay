# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import unittest
import os

from inventorum.ebay.lib.ebay.categories import EbayCategories
from inventorum.ebay.lib.ebay.data.categories import EbayCategory
from inventorum.ebay.lib.ebay.data.features import EbayFeature, EbayFeatureDefinition, \
    EbayListingDurationDefinition
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, long_running_test

log = logging.getLogger(__name__)


class EbayApiCategoriesTest(EbayAuthenticatedAPITestCase):
    @long_running_test()
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

    # TODO: We cannot use here cassette cause it is not supporting gevent (somehow, second response is empty
    # if taken from cassette)
    @long_running_test()
    def test_ebay_categories_features(self):
        ebay = EbayCategories(self.ebay_token)
        features = ebay.get_features_for_categories(['353', '64540'])
        self.assertEqual(len(features), 2)
        feature = features['353']

        self.assertIsInstance(feature, EbayFeature)
        self.assertEqual(feature.details.category_id, '353')

        log.debug('Durations: %s', feature.details.durations)
        self.assertEqual(len(feature.details.durations), 9)
        self.assertEqual(len(feature.details.durations_dict), 9)

        self.assertEqual(feature.details.durations_dict['FixedPriceItem'], 8)
        self.assertIsNone(feature.details.payment_methods)
        self.assertTrue(feature.details.item_specifics_enabled)
        self.assertEqual(feature.payment_methods, [
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

        second_feature = features['64540']

        self.assertIsInstance(second_feature, EbayFeature)
        self.assertEqual(second_feature.details.category_id, '64540')

        self.assertEqual(len(second_feature.details.durations), 9)
        self.assertEqual(len(second_feature.details.durations_dict), 9)

        self.assertEqual(second_feature.details.durations_dict['FixedPriceItem'], 8)
        self.assertIsNone(second_feature.details.payment_methods)
        self.assertTrue(second_feature.details.item_specifics_enabled)
        self.assertEqual(second_feature.payment_methods, [
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

        feature_definition = feature.definition
        self.assertIsInstance(feature_definition, EbayFeatureDefinition)
        self.assertEqual(len(feature_definition.durations), 6)

        for duration in feature_definition.durations:
            self.assertIsInstance(duration, EbayListingDurationDefinition)

        # So in Category 353 we got SetId: 8 for FixedPriceItem, lets check if this is in definitions
        self.assertIsInstance(feature_definition.durations_dict[8], EbayListingDurationDefinition)
        log.debug('Original data: %s', feature_definition.durations_dict[8]._poposerializer_original_data)
        self.assertEqual(feature_definition.durations_dict[8].durations, ['Days_3', 'Days_5', 'Days_7', 'Days_10',
                                                                          'Days_30'])

        self.assertEqual(feature.get_duration_list_by_type('FixedPriceItem'), ['Days_3', 'Days_5', 'Days_7', 'Days_10',
                                                                               'Days_30'])