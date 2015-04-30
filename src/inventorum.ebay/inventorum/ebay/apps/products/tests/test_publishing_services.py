# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from decimal import Decimal as D
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory

from inventorum.ebay.apps.core_api.tests import ApiTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, \
    UnpublishingService, PublishingPreparationService
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.products.tests.factories import EbayProductSpecificFactory
from inventorum.ebay.tests import StagingTestAccount
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestPublishingServices(EbayAuthenticatedAPITestCase, ProductTestMixin):

    def _get_product(self, inv_product_id, account):
        return EbayProductModel.objects.get_or_create(inv_id=inv_product_id, account=account)[0]

    def _assign_category(self, product):
        leaf_category = CategoryFactory.create(name="Leaf category", external_id='64540')

        self.specific = CategorySpecificFactory.create(category=leaf_category)
        self.required_specific = CategorySpecificFactory.create_required(category=leaf_category, max_values=2)

        product.category = leaf_category
        product.save()

    def _add_specific_to_product(self, product):
        EbayProductSpecificFactory.create(product=product, specific=self.required_specific, value="Test")
        EbayProductSpecificFactory.create(product=product, specific=self.required_specific, value="Test 2")

    def test_failed_validation(self):
        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, 'Neither product or account have configured shipping services')

        self.assign_valid_shipping_services(product)

        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

        self.assertEqual(e.exception.message, 'You need to select category')
        self._assign_category(service.product)

        service.core_product.gross_price = D("0.99")

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Price needs to be greater or equal than 1')

        service.core_product.gross_price = 1

        # mock that product was published
        item = service.create_ebay_item()
        item.publishing_status = EbayItemPublishingStatus.PUBLISHED
        item.save()

        with self.assertRaises(PublishingValidationException) as e:
            service.validate()

        self.assertEqual(e.exception.message, 'Product was already published')

        item.publishing_status = EbayItemPublishingStatus.UNPUBLISHED
        item.save()

        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

            self.assertEqual(e.exception.message,
                             'You need to pass all required specifics (missing: [%s])!' % self.required_specific.pk)

            self._add_specific_to_product(product)

        # Add click & collect to check validation of it!
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            # Mark product as click and collect product
            product.is_click_and_collect = True
            product.save()

            service = PublishingPreparationService(product, self.user)

            # Disable click and collect
            service.core_account.settings.ebay_click_and_collect = False

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

            self.assertEqual(e.exception.message,
                             "You cannot publish product with Click & Collect, because you don't have it enabled for "
                             "your account!")

        product.is_click_and_collect = False
        product.save()

        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)
            # Should not raise anything finally!
            service.validate()

    def test_preparation(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)

        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingPreparationService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
            self.assign_valid_shipping_services(product)

            service.create_ebay_item()

        last_item = product.items.last()
        self.assertEqual(last_item.name, "SlowRoad Shipping Details")
        self.assertEqual(last_item.description, "Some description")
        self.assertEqual(last_item.postal_code, "13355")
        self.assertEqual(last_item.quantity, 3000)
        self.assertEqual(last_item.gross_price, D("599.99"))
        self.assertEqual(last_item.country, 'DE')
        self.assertEqual(last_item.paypal_email_address, 'bartosz@hernas.pl')
        self.assertEqual(last_item.publishing_status, EbayItemPublishingStatus.DRAFT)
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
        self.assertEqual(shipping_services[0].cost, D('5.00'))
        self.assertEqual(shipping_services[0].additional_cost, D('3.00'))

        self.assertEqual(shipping_services[1].external_id, 'DE_HermesPaket')
        self.assertEqual(shipping_services[1].cost, D('4.50'))
        self.assertEqual(shipping_services[1].additional_cost, D('1.00'))

    def test_account_shipping_fallback(self):
        product = self._get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)

        self.account.shipping_services.create(service=self.get_shipping_service_hermes(),
                                              cost=D("3.00"), additional_cost=D("0.00"))

        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)

            self._assign_category(product)
            service.create_ebay_item()

        last_item = product.items.last()
        shipping_services = last_item.shipping.all()

        self.assertEqual(shipping_services.count(), 1)
        self.assertEqual(shipping_services[0].external_id, "DE_HermesPaket")
        self.assertEqual(shipping_services[0].cost, D("3.00"))
        self.assertEqual(shipping_services[0].additional_cost, D("0.00"))

    def test_builder(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingPreparationService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
            self.assign_valid_shipping_services(product)

            service.create_ebay_item()
            last_item = product.items.last()

        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()
        self.assertEqual(data, {'Item': {
            'SKU': 'invdev_{0}'.format(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES),
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
            'StartPrice': '599.99',
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
                        'ShippingServiceAdditionalCost': '3.00',
                        'ShippingServiceCost': '5.00',
                        'ShippingServicePriority': 1
                    }
                },
                {
                    'ShippingServiceOptions': {
                        'ShippingService': 'DE_HermesPaket',
                        'ShippingServiceAdditionalCost': '1.00',
                        'ShippingServiceCost': '4.50',
                        'ShippingServicePriority': 1
                    }
                }],
        }})

    @ApiTest.use_cassette("test_publishing_service_publish_and_unpublish.yaml", match_on=['body'])
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

        # assign valid shipping service
        self.assign_valid_shipping_services(product)

        # Try to publish
        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()
        item = preparation_service.create_ebay_item()

        publishing_service = PublishingService(item, self.user)
        publishing_service.initialize_publish_attempt()
        publishing_service.publish()
        publishing_service.finalize_publish_attempt()

        item = product.published_item
        self.assertIsNotNone(item)
        self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)
        self.assertIsNotNone(item.published_at)
        self.assertIsNotNone(item.ends_at)
        self.assertIsNone(item.unpublished_at)

        # And now unpublish
        unpublishing_service = UnpublishingService(item, self.user)
        unpublishing_service.unpublish()

        item = product.published_item
        self.assertIsNone(item)

        last_item = product.items.last()
        self.assertEqual(last_item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)
        self.assertIsNotNone(last_item.published_at)
        self.assertIsNotNone(last_item.unpublished_at)

    def test_builder_with_variations(self):
        product = self._get_product(StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS, self.account)
        with ApiTest.use_cassette("get_product_with_variations_for_testing_builder.yaml"):
            self._assign_category(product)
            self._add_specific_to_product(product)
            self.assign_valid_shipping_services(product)

            # Try to publish
            preparation_service = PublishingPreparationService(product, self.user)
            preparation_service.validate()
            last_item = preparation_service.create_ebay_item()

        self.assertEqual(last_item.variations.count(), 2)

        first_variation_obj = last_item.variations.first()
        self.assertEqual(first_variation_obj.quantity, 30)
        self.assertEqual(first_variation_obj.gross_price, D("150"))
        self.assertEqual(first_variation_obj.specifics.count(), 3)
        self.assertEqual(first_variation_obj.images.count(), 1)

        specifics = first_variation_obj.specifics.all()

        for specific in specifics:
            self.assertEqual(specific.values.count(), 1)

        self.assertEqual(specifics[0].name, "size")
        self.assertEqual(specifics[0].values.first().value, "22")

        self.assertEqual(specifics[1].name, "material")
        self.assertEqual(specifics[1].values.first().value, "Denim")

        self.assertEqual(specifics[2].name, "color")
        self.assertEqual(specifics[2].values.first().value, "Red")

        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()['Item']

        variations_data = data['Variations']['Variation']
        self.assertEqual(len(variations_data), 2)

        first_variation = variations_data[0]

        self.assertEqual(first_variation, {
            'Quantity': 30,
            'StartPrice': '150.00',
            'SKU': 'invdev_666030',
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'size',
                        'Value': '22'
                    },
                    {
                        'Name': 'material',
                        'Value': 'Denim'
                    },
                    {
                        'Name': 'color',
                        'Value': 'Red'
                    },
                ]
            }
        })

        second_variation = variations_data[1]

        self.assertEqual(second_variation, {
            'Quantity': 50,
            'StartPrice': '130.00',
            'SKU': 'invdev_666031',
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'size',
                        'Value': '50'
                    },
                    {
                        'Name': 'material',
                        'Value': 'Leather'
                    },
                    {
                        'Name': 'color',
                        'Value': 'Blue'
                    },
                ]
            }
        })

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

        pictures_set = data['Variations']['Pictures']
        self.assertEqual(pictures_set,
                         {
                             'VariationSpecificName': 'size',
                             'VariationSpecificPictureSet': [
                                 {
                                     'PictureURL': ['http://app.inventorum.net/uploads/img-hash/5c3e/ad51/fe29/ab83/df38/febd/4f3d/5c3ead51fe29ab83df38febd4f3d9c79_ipad_retina.JPEG'],
                                     'VariationSpecificValue': '22'
                                 },
                                 {
                                     'PictureURL': ['http://app.inventorum.net/uploads/img-hash/848d/489a/a390/cfc5/8bd1/d6d2/092b/848d489aa390cfc58bd1d6d2092b2d3e_ipad_retina.JPEG'],
                                     'VariationSpecificValue': '50'
                                 }
                             ]
                         })

    def test_product_with_invalid_attributes_for_ebay(self):
        product = self._get_product(StagingTestAccount.Products.WITH_VARIATIONS_INVALID_ATTRS, self.account)
        with ApiTest.use_cassette("get_product_with_variations_invalid_attrs_for_testing_builder.yaml"):
            self._assign_category(product)
            self.assign_valid_shipping_services(product)
            self._add_specific_to_product(product)

            preparation_service = PublishingPreparationService(product, self.user)
            with self.assertRaises(PublishingValidationException) as exc:
                preparation_service.validate()

            self.assertEqual(exc.exception.message, "All variations needs to have exactly the same number of attributes")


    @ApiTest.use_cassette("get_product_for_click_and_collect.yaml")
    def test_builder_for_click_and_collect(self):
        product = self._get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
        product.is_click_and_collect = True
        product.save()

        service = PublishingPreparationService(product, self.user)

        self._assign_category(product)
        self._add_specific_to_product(product)
        service.create_ebay_item()

        last_item = product.items.last()
        self.assertEqual(last_item.is_click_and_collect, True)

        # Check data builder
        ebay_item = last_item.ebay_object

        data = ebay_item.dict()
        item_data = data['Item']
        self.assertIn('PickupInStoreDetails', item_data)
        self.assertIn('AutoPay', item_data)
        self.assertEqual(item_data['AutoPay'], True)

        self.assertIn('EligibleForPickupInStore', item_data['PickupInStoreDetails'])
        self.assertEqual(item_data['PickupInStoreDetails']['EligibleForPickupInStore'], True)


    @ApiTest.use_cassette("test_publish_product_for_click_and_collect.yaml")
    def test_builder_for_click_and_collect(self):
        with ApiTest.use_cassette("test_publish_product_for_click_and_collect.yaml") as cass:
            product = self._get_product(StagingTestAccount.Products.IPAD_STAND, self.account)
            product.is_click_and_collect = True
            product.save()

            self.assign_product_to_valid_category(product)
            self.assign_valid_shipping_services(product)

            # Try to publish
            preparation_service = PublishingPreparationService(product, self.user)
            preparation_service.validate()
            item = preparation_service.create_ebay_item()

            publishing_service = PublishingService(item, self.user)
            publishing_service.initialize_publish_attempt()
            publishing_service.publish()
            publishing_service.finalize_publish_attempt()

            item = product.published_item
            self.assertIsNotNone(item)
            self.assertEqual(item.publishing_status, EbayItemPublishingStatus.PUBLISHED)
            self.assertIsNotNone(item.published_at)
            self.assertIsNotNone(item.ends_at)
            self.assertIsNone(item.unpublished_at)

            # And now unpublish
            unpublishing_service = UnpublishingService(item, self.user)
            unpublishing_service.unpublish()

            item = product.published_item
            self.assertIsNone(item)

            last_item = product.items.last()
            self.assertEqual(last_item.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)
            self.assertIsNotNone(last_item.published_at)
            self.assertIsNotNone(last_item.unpublished_at)

        requests = cass.requests
        uris = [r.uri for r in requests]
        self.assertIn('https://api.ebay.com/selling/inventory/v1/inventory/delta/add', uris)
        self.assertIn('https://api.ebay.com/selling/inventory/v1/inventory/delta/delete', uris)