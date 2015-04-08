# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
import unittest
from inventorum.ebay.apps.categories.models import CategoryModel

from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.apps.products.builders import TradingEbayProductDataBuilder
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestPublishingService(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(TestPublishingService, self).setUp()

    def _assign_category(self, product):
        category, c = CategoryModel.objects.get_or_create(external_id='64540')
        product.category = category
        product.save()

    def _create_product(self, core_product):
        product = EbayProductModel.objects.create(
            inv_id=core_product.id,
            account=self.account
        )
        return product

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

        # Right now I am mocking that we once saved a product for ebay
        product = self._create_product(service.core_product)

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'You need to select category')
        self._assign_category(product)
        # Should not raise anything finally!
        service.validate()

    def test_preparation(self):
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test_with_shipping.json"):
            service = PublishingService(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.user)

        product = self._create_product(service.core_product)

        self._assign_category(product)
        service.prepare()

        last_item = product.items.last()
        self.assertEqual(last_item.name, "SlowRoad Shipping Details")
        self.assertEqual(last_item.description, "Some description")
        self.assertEqual(last_item.postal_code, "13355")
        self.assertEqual(last_item.quantity, 3000)
        self.assertEqual(last_item.gross_price, Decimal("599.99"))
        self.assertEqual(last_item.country, 'DE')
        self.assertEqual(last_item.publishing_status, EbayProductPublishingStatus.DRAFT)

    def test_builder(self):
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test_with_shipping.json"):
            service = PublishingService(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.user)

        product = self._create_product(service.core_product)

        self._assign_category(product)
        service.prepare()
        last_item = product.items.last()

        # Check data builder
        builder = TradingEbayProductDataBuilder(last_item)
        data = builder.build()
        self.assertEqual(data, {u'Item': {
            u'ConditionID': 1000,
            u'Country': 'DE',
            u'Currency': u'EUR',
            u'Description': u'Some description',
            u'DispatchTimeMax': 3,
            u'ListingType': u'FixedPriceItem',
            u'PostalCode': u'13355',
            u'PrimaryCategory': {u'CategoryID': u'64540'},
            u'Quantity': 3000,
            u'ReturnPolicy': {
                u'Description': u'',
                u'ReturnsAcceptedOption': u'ReturnsAccepted'
            },
            u'StartPrice': Decimal('599.9900000000'),
            u'Title': u'SlowRoad Shipping Details'
        }})

