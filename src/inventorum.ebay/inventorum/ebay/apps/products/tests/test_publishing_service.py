# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
import unittest
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel

from inventorum.ebay.apps.core_api.tests import CoreApiTest, ApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, UnpublishingService
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestPublishingService(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(TestPublishingService, self).setUp()

    def _get_product(self, inv_product_id, account):
        return EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=account)[0]

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

    def test_failed_validation(self):
        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingService(product, self.user)

            # No shipping services
            service.core_account.settings.shipping_services = []
            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, 'Product has not shipping services selected')

        # Get product w/o shipping but acc has
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, 'You need to select category')
        self._assign_category(service.product)

        service.core_product.gross_price = Decimal("0.99")

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Price needs to be greater or equal than 1')

        service.core_product.gross_price = 1

        # mock that product was published
        item = service._create_db_item()
        item.publishing_status = EbayProductPublishingStatus.PUBLISHED
        item.save()

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Product was already published')

        item.publishing_status = EbayProductPublishingStatus.UNPUBLISHED
        item.save()

        # Get product again cause it has cached item
        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingService(product, self.user)

            # Should not raise anything finally!
            service.validate()

    def test_preparation(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingService(product, self.user)

            self._assign_category(product)
            service.prepare()

        last_item = product.items.last()
        self.assertEqual(last_item.name, "SlowRoad Shipping Details")
        self.assertEqual(last_item.description, "Some description")
        self.assertEqual(last_item.postal_code, "13355")
        self.assertEqual(last_item.quantity, 3000)
        self.assertEqual(last_item.gross_price, Decimal("599.99"))
        self.assertEqual(last_item.country, 'DE')
        self.assertEqual(last_item.paypal_email_address, 'bartosz@hernas.pl')
        self.assertEqual(last_item.publishing_status, EbayProductPublishingStatus.DRAFT)
        self.assertEqual(last_item.listing_duration, 'Days_120')

        payment_methods = last_item.payment_methods.all()
        self.assertEqual(payment_methods.count(), 1)
        self.assertEqual(payment_methods.last().external_id, 'PayPal')

        images = last_item.images.all()
        self.assertEqual(images.count(), 1)

        last_image = images.last()
        self.assertEqual(last_image.inv_id, 2918)
        self.assertTrue(last_image.url.startswith('https://app.inventorum.net/'),
                        "Image does not starts with https:// (%s)" % last_image.url)

        shipping_services = last_item.shipping.all()
        self.assertEqual(shipping_services.count(), 2)

        self.assertEqual(shipping_services[0].external_id, 'DE_DHLPaket')
        self.assertEqual(shipping_services[0].cost, Decimal('20'))
        self.assertEqual(shipping_services[0].additional_cost, Decimal('3'))

        self.assertEqual(shipping_services[1].external_id, 'DE_HermesPaket')
        self.assertEqual(shipping_services[1].cost, Decimal('10'))
        self.assertEqual(shipping_services[1].additional_cost, Decimal('1'))

    def test_account_shipping_fallback(self):
        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingService(product, self.user)

            self._assign_category(product)
            service.prepare()

            last_item = product.items.last()
            shipping_services = last_item.shipping.all()

            self.assertEqual(shipping_services.count(), 1)
            self.assertEqual(shipping_services[0].external_id, 'DE_DHL2KGPaket')
            self.assertEqual(shipping_services[0].cost, Decimal('0'))
            self.assertEqual(shipping_services[0].additional_cost, None)

    def test_builder(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingService(product, self.user)

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
            u'PayPalEmailAddress': u'bartosz@hernas.pl',
            u'PaymentMethods': ['PayPal'],
            u'PictureDetails': [{'PictureURL': 'http://app.inventorum.net/uploads/img-hash/3931/c077/30b1/c4ac/2992/ae9'
                                               '2/f6f8/3931c07730b1c4ac2992ae92f6f8dfdc_ipad_retina.JPEG'}],
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

    @ApiTest.use_cassette("test_publishing_service_publish_and_unpublish.yaml")
    def test_publishing(self):
        product = self._get_product(StagingTestAccount.Products.IPAD_STAND, self.account)

        # 176973 is valid ebay category id
        category, c = CategoryModel.objects.get_or_create(external_id='176973')
        product.category = category
        product.save()

        features = CategoryFeaturesModel.objects.create(
            category=category
        )
        durations = ['Days_5', 'Days_30']
        for d in durations:
            duration = DurationModel.objects.create(
                value=d
            )
            features.durations.add(duration)

        # Try to publish
        service = PublishingService(product, self.user)
        service.validate()
        item = service.prepare()
        service.publish(item)

        item = product.published_item
        self.assertIsNotNone(item)
        self.assertEqual(item.publishing_status, EbayProductPublishingStatus.PUBLISHED)
        self.assertIsNotNone(item.published_at)
        self.assertIsNotNone(item.ends_at)
        self.assertIsNone(item.unpublished_at)

        # And now unpublish
        unpublish_service = UnpublishingService(product, self.user)
        unpublish_service.validate()
        unpublish_service.unpublish()

        item = product.published_item
        self.assertIsNone(item)

        last_item = product.items.last()
        self.assertEqual(last_item.publishing_status, EbayProductPublishingStatus.UNPUBLISHED)
        self.assertIsNotNone(last_item.published_at)
        self.assertIsNotNone(last_item.unpublished_at)


