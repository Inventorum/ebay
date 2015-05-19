# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.services import PublishingPreparationService, PublishingValidationException
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.tests import StagingTestAccount, ApiTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestValidationOfAttribtuesInProductService(EbayAuthenticatedAPITestCase, ProductTestMixin):

    def test_missing_attributes_in_one_variation(self):

        product = self.get_product(StagingTestAccount.Products.WITH_VARIATIONS_MISSING_ATTRS, self.account)
        self.assign_valid_shipping_services(product)
        self.assign_product_to_valid_category(product)

        with ApiTest.use_cassette("get_product_with_missing_attrs.yaml"):
            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, "All variations needs to have exactly the same number of attributes")

    def test_variation_without_attributes(self):

        product = self.get_product(StagingTestAccount.Products.WITH_VARIATIONS_NO_ATTRS, self.account)
        self.assign_valid_shipping_services(product)
        self.assign_product_to_valid_category(product)

        with ApiTest.use_cassette("get_product_with_no_attrs.yaml"):
            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, "Variations need to have at least one attribute")