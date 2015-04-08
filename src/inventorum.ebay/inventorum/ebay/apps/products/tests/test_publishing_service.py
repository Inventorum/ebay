# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.categories.models import CategoryModel

from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestPublishingService(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(TestPublishingService, self).setUp()

    def test_failed_validation(self):
        # Product not in db
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test.json"):
            service = PublishingService(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.user)

        # No shipping services
        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Product has not shipping services selected')

        # Get product with shipping

        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test_with_shipping.json"):
            service = PublishingService(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.user)

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Couldnt find product [inv_id:640416] in database')

        # Right now I am mocking category assigment, in future there will be endpoint for it
        EbayProductModel.objects.create(
            inv_id=service.core_product.id,
            account=self.account,
            category=CategoryModel.objects.filter(country='DE').last()
        )

        # Should not raise anything!
        service.validate()

    # def test_successful_validation(self):
    #     with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test.json"):
    #         core_product = self.api_client.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID)
    #
    #     # Right now I am mocking category assigment, in future there will be endpoint for it
    #     EbayProductModel.objects.create(
    #         inv_id=core_product.id,
    #         account=self.account,
    #         category=CategoryModel.objects.filter(country='DE').last()
    #     )