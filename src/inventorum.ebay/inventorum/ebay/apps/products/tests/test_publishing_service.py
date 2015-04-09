# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
import unittest
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel

from inventorum.ebay.apps.core_api.tests import CoreApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus
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

        features = CategoryFeaturesModel.objects.create(
            category=category
        )
        durations = ['Days_5', 'Days_120']
        for d in durations:
            duration = DurationModel.objects.create(
                value=d
            )
            features.durations.add(duration)

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
        service.core_account.settings.shipping_services = []
        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Product has not shipping services selected')

        # Get product w/o shipping but acc has
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test.json"):
            service = PublishingService(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.user)

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Couldnt find product [inv_id:463690] in database')

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
        self.assertEqual(last_item.paypal_email_address, 'john.newman@paypal.com')
        self.assertEqual(last_item.publishing_status, EbayProductPublishingStatus.DRAFT)
        self.assertEqual(last_item.listing_duration, 'Days_120')

        payment_methods = last_item.payment_methods.all()
        self.assertEqual(payment_methods.count(), 1)
        self.assertEqual(payment_methods.last().external_id, 'PayPal')

        shipping_services = last_item.shipping.all()
        self.assertEqual(shipping_services.count(), 2)

        self.assertEqual(shipping_services[0].external_id, 'DE_DHLPaket')
        self.assertEqual(shipping_services[0].cost, Decimal('20'))
        self.assertEqual(shipping_services[0].additional_cost, Decimal('3'))

        self.assertEqual(shipping_services[1].external_id, 'DE_HermesPaket')
        self.assertEqual(shipping_services[1].cost, Decimal('10'))
        self.assertEqual(shipping_services[1].additional_cost, Decimal('1'))

    def test_account_shipping_fallback(self):
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test.json"):
            service = PublishingService(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.user)

        product = self._create_product(service.core_product)

        self._assign_category(product)
        service.prepare()

        last_item = product.items.last()
        shipping_services = last_item.shipping.all()

        self.assertEqual(shipping_services.count(), 1)
        self.assertEqual(shipping_services[0].external_id, 'DE_HermesPaket')
        self.assertEqual(shipping_services[0].cost, Decimal('0'))
        self.assertEqual(shipping_services[0].additional_cost, None)

    def test_builder(self):
        with CoreApiTest.vcr.use_cassette("get_product_simple_for_publishing_test_with_shipping.json"):
            service = PublishingService(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.user)

        product = self._create_product(service.core_product)

        self._assign_category(product)
        service.prepare()
        last_item = product.items.last()

        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()
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
            u'Title': u'SlowRoad Shipping Details',
            u'ListingDuration': u'Days_120',
            u'PayPalEmailAddress': u'john.newman@paypal.com',
            u'PaymentMethods': ['PayPal'],
            u'ShippingDetails': [
                {
                    u'ShippingServiceOptions': {
                        u'ShippingService': u'DE_DHLPaket',
                        u'ShippingServiceAdditionalCost': Decimal('3.0000000000'),
                        u'ShippingServiceCost': Decimal('20.0000000000'),
                        u'ShippingServicePriority': 1
                    }
                },
                {
                    u'ShippingServiceOptions': {
                        u'ShippingService': u'DE_HermesPaket',
                        u'ShippingServiceAdditionalCost': Decimal('1.0000000000'),
                        u'ShippingServiceCost': Decimal('10.0000000000'),
                        u'ShippingServicePriority': 1
                    }
                }],
        }})

