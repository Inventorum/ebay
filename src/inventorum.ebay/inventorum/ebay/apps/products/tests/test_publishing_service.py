# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
import unittest
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory

from inventorum.ebay.apps.core_api.tests import CoreApiTest, ApiTest
from inventorum.ebay.apps.products import EbayProductPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel, EbayItemModel, EbayProductSpecificModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, UnpublishingService
from inventorum.ebay.apps.products.tests.factories import EbayProductSpecificFactory
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestPublishingService(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(TestPublishingService, self).setUp()

    def _get_product(self, inv_product_id, account):
        return EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=account)[0]

    def _assign_category(self, product):
        leaf_category = CategoryFactory.create(name="Leaf category", external_id='64540')

        self.specific = CategorySpecificFactory.create(category=leaf_category)
        self.required_specific = CategorySpecificFactory.create_required(category=leaf_category, max_values=2)

        features = CategoryFeaturesModel.objects.create(
            category=leaf_category
        )
        durations = ['Days_5', 'Days_120']

        for d in durations:
            duration = DurationModel.objects.create(
                value=d
            )
            features.durations.add(duration)

        product.category = leaf_category
        product.save()

    def _add_specific_to_product(self, product):
        EbayProductSpecificFactory.create(product=product, specific=self.required_specific, value="Test")
        EbayProductSpecificFactory.create(product=product, specific=self.required_specific, value="Test 2")

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

        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

            self.assertEqual(e.exception.message,
                             'You need to pass all required specifics (missing: [%s])!' % self.required_specific.pk)

            self._add_specific_to_product(product)
            # Should not raise anything finally!
            service.validate()

    def test_preparation(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
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

        specific_values = last_item.specific_values.all()
        self.assertEqual(specific_values.count(), 2)
        last_specific = specific_values.last()
        self.assertEqual(last_specific.value, 'Test')
        self.assertEqual(last_specific.specific.pk, self.required_specific.pk)

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
            self.assertEqual(shipping_services[0].cost, Decimal('5'))
            self.assertEqual(shipping_services[0].additional_cost, Decimal('2'))

    def test_builder(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
            service.prepare()
            last_item = product.items.last()

        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()
        self.assertEqual(data, {'Item': {
            'ConditionID': 1000,
            'Country': 'DE',
            'Currency': 'EUR',
            'Description': 'Some description',
            'DispatchTimeMax': 3,
            'ListingType': 'FixedPriceItem',
            'PostalCode': '13355',
            'PrimaryCategory': {'CategoryID': '64540'},
            'Quantity': 3000,
            'ReturnPolicy': {
                'Description': '',
                'ReturnsAcceptedOption': 'ReturnsAccepted'
            },
            'ItemSpecifics': {'NameValueList': [{'Name': self.required_specific.name,
                                                 'Value': ['Test', 'Test 2']}]},
            'StartPrice': Decimal('599.9900000000'),
            'Title': 'SlowRoad Shipping Details',
            'ListingDuration': 'Days_120',
            'PayPalEmailAddress': 'bartosz@hernas.pl',
            'PaymentMethods': ['PayPal'],
            'PictureDetails': [{'PictureURL': 'http://app.inventorum.net/uploads/img-hash/3931/c077/30b1/c4ac/2992/ae9'
                                              '2/f6f8/3931c07730b1c4ac2992ae92f6f8dfdc_ipad_retina.JPEG'}],
            'ShippingDetails': [
                {
                    'ShippingServiceOptions': {
                        'ShippingService': 'DE_DHLPaket',
                        'ShippingServiceAdditionalCost': Decimal('3.0000000000'),
                        'ShippingServiceCost': Decimal('20.0000000000'),
                        'ShippingServicePriority': 1
                    }
                },
                {
                    'ShippingServiceOptions': {
                        'ShippingService': 'DE_HermesPaket',
                        'ShippingServiceAdditionalCost': Decimal('1.0000000000'),
                        'ShippingServiceCost': Decimal('10.0000000000'),
                        'ShippingServicePriority': 1
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
        service.change_state(item, EbayProductPublishingStatus.PUBLISHED)

        item = product.published_item
        self.assertIsNotNone(item)
        self.assertEqual(item.publishing_status, EbayProductPublishingStatus.PUBLISHED)
        self.assertIsNotNone(item.published_at)
        self.assertIsNotNone(item.ends_at)
        self.assertIsNone(item.unpublished_at)

        # And now unpublish
        unpublish_service = UnpublishingService(product, self.user)
        unpublish_service.validate()
        unpublish_service.unpublish(unpublish_service.get_item())

        item = product.published_item
        self.assertIsNone(item)

        last_item = product.items.last()
        self.assertEqual(last_item.publishing_status, EbayProductPublishingStatus.UNPUBLISHED)
        self.assertIsNotNone(last_item.published_at)
        self.assertIsNotNone(last_item.unpublished_at)

    def test_builder_with_variations(self):
        product = self._get_product(StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS, self.account)
        with ApiTest.use_cassette("get_product_with_variations_fro_testing_builder.yaml"):
            service = PublishingService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
            service.prepare()
            last_item = product.items.last()

        self.assertEqual(last_item.variations.count(), 2)

        first_variation_obj = last_item.variations.first()
        self.assertEqual(first_variation_obj.quantity, 30)
        self.assertEqual(first_variation_obj.gross_price, Decimal("150"))
        self.assertEqual(first_variation_obj.specifics.count(), 3)

        for specific in first_variation_obj.specifics.all():
            self.assertEqual(specific.values.count(), 1)


        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()
        self.assertEqual(data['Variations']['VariationSpecificsSet'], {
            'NameValueList': [
                {
                    'Name': 'color',
                    'Value': ['Red', 'Blue']
                },
                {
                    'Name': 'material',
                    'Value': ['Denim', 'Leather']
                },
                {
                    'Name': 'size',
                    'Value': ['22', '50']
                }
            ]
        })

        variations_data = data['Variations']['Variation']
        self.assertEqual(len(variations_data), 2)

        first_variation = variations_data[0]

        self.assertEqual(first_variation, {
            'Quantity': 30,
            'StartPrice': Decimal('150'),
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'color',
                        'Value': ['Red']
                    },
                    {
                        'Name': 'material',
                        'Value': ['Denim']
                    },
                    {
                        'Name': 'size',
                        'Value': ['22']
                    }
                ]
            }
        })

        second_variation = variations_data[0]

        self.assertEqual(second_variation, {
            'Quantity': 50,
            'StartPrice': Decimal('130'),
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'color',
                        'Value': ['Blue']
                    },
                    {
                        'Name': 'material',
                        'Value': ['Leather']
                    },
                    {
                        'Name': 'size',
                        'Value': ['50']
                    }
                ]
            }
        })


