# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal as D, Decimal

from inventorum.ebay.tests import StagingTestAccount

from ebaysdk.response import Response, ResponseDataObject
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory
from inventorum.ebay.tests import ApiTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, \
    UnpublishingService, PublishingPreparationService
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.products.tests.factories import EbayProductSpecificFactory, EbayProductFactory
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.lib.core_api.tests.factories import CoreProductFactory, CoreProductVariationFactory, \
    CoreProductAttributeFactory, CoreInfoFactory
from inventorum.ebay.lib.ebay.data.categories import EbayCategory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from mock import PropertyMock

log = logging.getLogger(__name__)


class TestPublishingServices(EbayAuthenticatedAPITestCase, ProductTestMixin, ShippingServiceTestMixin):
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
        product = self.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
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

        self.assertEqual(e.exception.message, 'Product is already published')

        item.publishing_status = EbayItemPublishingStatus.UNPUBLISHED
        item.save()

        product = self.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
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

        # Add click & collect to check validation of payment methods!
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            # Mark product as click and collect product
            product.is_click_and_collect = True
            product.save()

            # Disable Paypal
            account = self.user.account
            account.payment_method_paypal_enabled = False
            account.save()

            service = PublishingPreparationService(product, self.user)

            # Enable click and collect
            service.core_account.settings.ebay_click_and_collect = True

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

            self.assertEqual(e.exception.message,
                             "Click&Collect requires to use PayPal as payment method!")

        product.is_click_and_collect = False
        product.save()

        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            # Enable Paypal, remove email
            account = self.user.account
            account.payment_method_paypal_enabled = True
            account.payment_method_paypal_email_address = None
            account.save()

            service = PublishingPreparationService(product, self.user)

            with self.assertRaises(PublishingValidationException) as e:
                service.validate()

            self.assertEqual(e.exception.message,
                             'Missing paypal email addres, however paypal payment method is enabled!')

        account = self.user.account
        account.payment_method_paypal_email_address = "bartosz@hernas.pl"
        account.save()

        product = self.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)
        with ApiTest.use_cassette("get_product_simple_for_publishing_test.yaml"):
            service = PublishingPreparationService(product, self.user)
            # Should not raise anything finally!
            service.validate()

    def test_preparation(self):
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)

        with ApiTest.use_cassette("get_product_simple_for_publishing_test_with_shipping.yaml"):
            service = PublishingPreparationService(product, self.user)

            self._assign_category(product)
            self._add_specific_to_product(product)
            self.assign_valid_shipping_services(product)

            service.create_ebay_item()

        last_item = product.items.last()
        self.assertEqual(last_item.inv_product_id, 640416)
        self.assertEqual(last_item.name, "SlowRoad Shipping Details")
        self.assertEqual(last_item.description, "Some description")
        self.assertEqual(last_item.postal_code, "13355")
        self.assertEqual(last_item.quantity, 3000)
        self.assertEqual(last_item.gross_price, D("599.99"))
        self.assertEqual(last_item.tax_rate, D("7"))
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
        self.assertEqual(last_image.inv_image_id, 2918)
        self.assertTrue(last_image.url.startswith('https://app.inventorum.net/'),
                        "Image does not start with https:// (%s)" % last_image.url)

        shipping_services = last_item.shipping.all()
        self.assertEqual(shipping_services.count(), 2)

        self.assertEqual(shipping_services[0].external_id, 'DE_DHLPaket')
        self.assertEqual(shipping_services[0].cost, D('5.00'))
        self.assertEqual(shipping_services[0].additional_cost, D('3.00'))

        self.assertEqual(shipping_services[1].external_id, 'DE_HermesPaket')
        self.assertEqual(shipping_services[1].cost, D('4.50'))
        self.assertEqual(shipping_services[1].additional_cost, D('1.00'))

    def test_account_shipping_fallback(self):
        product = self.get_product(StagingTestAccount.Products.SIMPLE_PRODUCT_ID, self.account)

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
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
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
            'SKU': 'invtest_640416',
            'ConditionID': 1000,
            'Country': 'DE',
            'Currency': 'EUR',
            'Description': '<![CDATA[Some description]]>',
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
            'PictureDetails': {'PictureURL': ['http://app.inventorum.net/uploads/img-hash/3931/c077/30b1/c4ac/2992/ae9'
                                              '2/f6f8/3931c07730b1c4ac2992ae92f6f8dfdc_ipad_retina.JPEG']},
            'ShippingDetails': {'ShippingServiceOptions': [{'ShippingService': 'DE_DHLPaket',
                                                            'ShippingServiceAdditionalCost': '3.00',
                                                            'ShippingServiceCost': '5.00',
                                                            'ShippingServicePriority': 1},
                                                           {'ShippingService': 'DE_HermesPaket',
                                                            'ShippingServiceAdditionalCost': '1.00',
                                                            'ShippingServiceCost': '4.50',
                                                            'ShippingServicePriority': 1}]},
        }})

    @ApiTest.use_cassette("get_product_with_ean_for_publishing.yaml")
    def test_builder_with_ean(self):
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITH_EAN, self.account)
        self.assign_valid_shipping_services(product)
        self.assign_product_to_valid_category(product)

        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()

        ebay_item = preparation_service.create_ebay_item()
        self.assertEqual(ebay_item.ean, "75678164125")

        data = ebay_item.ebay_object.dict()["Item"]

        self.assertTrue("ProductListingDetails" in data)
        self.assertTrue("EAN" in data["ProductListingDetails"])
        self.assertEqual(data["ProductListingDetails"]["EAN"], "75678164125")

    def test_ean_validation(self):
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITHOUT_EAN, self.account)
        self.assign_valid_shipping_services(product)

        # prove that the product is valid for publishing if category does not require EAN
        category = CategoryFactory.create(features__ean_required=False)
        product.category = category
        product.save()

        with ApiTest.use_cassette("get_product_without_ean_for_publishing.yaml"):
            preparation_service = PublishingPreparationService(product, self.user)
            # no raise means it's valid
            preparation_service.validate()

        category.features.ean_required = True
        category.features.save()

        with ApiTest.use_cassette("get_product_without_ean_for_publishing.yaml"):
            preparation_service = PublishingPreparationService(product, self.user)
            with self.assertRaises(PublishingValidationException) as exc:
                preparation_service.validate()

        self.assertEqual(exc.exception.message,
                         "The selected category requires a valid EAN")

    def test_builder_with_variations_and_ean(self):
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITH_VARIATIONS_AND_EAN, self.account)
        self.assign_valid_shipping_services(product)
        self.assign_product_to_valid_category(product)

        with ApiTest.use_cassette("get_product_with_variations_and_ean_for_publishing.yaml"):
            preparation_service = PublishingPreparationService(product, self.user)
            preparation_service.validate()
            ebay_item = preparation_service.create_ebay_item()

            self.assertIsNone(ebay_item.ean)

            self.assertEqual(ebay_item.variations.first().ean, "978020113447")
            self.assertEqual(ebay_item.variations.last().ean, "978020113448")

            data = ebay_item.ebay_object.dict()["Item"]

            self.assertFalse("ProductListingDetails" in data)

            variations_data = data['Variations']['Variation']
            self.assertEqual(len(variations_data), 2)

            self.assertTrue("VariationProductListingDetails" in variations_data[0])
            self.assertTrue("EAN" in variations_data[0]["VariationProductListingDetails"])
            self.assertEqual(variations_data[0]["VariationProductListingDetails"]["EAN"], "978020113448")

            self.assertTrue("VariationProductListingDetails" in variations_data[1])
            self.assertTrue("EAN" in variations_data[1]["VariationProductListingDetails"])
            self.assertEqual(variations_data[1]["VariationProductListingDetails"]["EAN"], "978020113447")

        # if product has no real ean (ean does not apply), the proper default value should be taken
        product.ean_does_not_apply = True
        product.save()

        with ApiTest.use_cassette("get_product_with_variations_and_ean_for_publishing.yaml"):
            preparation_service = PublishingPreparationService(product, self.user)
            preparation_service.validate()

            ebay_item = preparation_service.create_ebay_item()
            self.assertIsNone(ebay_item.ean)

            self.assertEqual(ebay_item.variations.first().ean, "Does not apply")
            self.assertEqual(ebay_item.variations.last().ean, "Does not apply")

            data = ebay_item.ebay_object.dict()["Item"]

            variations_data = data['Variations']['Variation']
            self.assertEqual(len(variations_data), 2)

            self.assertTrue("VariationProductListingDetails" in variations_data[0])
            self.assertTrue("EAN" in variations_data[0]["VariationProductListingDetails"])
            self.assertEqual(variations_data[0]["VariationProductListingDetails"]["EAN"], "Does not apply")

            self.assertTrue("VariationProductListingDetails" in variations_data[1])
            self.assertTrue("EAN" in variations_data[1]["VariationProductListingDetails"])
            self.assertEqual(variations_data[1]["VariationProductListingDetails"]["EAN"], "Does not apply")

    def test_ean_validation_with_variations(self):
        product = EbayProductFactory.create()
        category = CategoryFactory.create()

        product.shipping_services.create(service=self.get_shipping_service_dhl(), cost=Decimal("3.99"))
        product.category = category
        product.save()

        core_product = CoreProductFactory.create(variations=[
            CoreProductVariationFactory.create(
                ean=None,
                attributes=[CoreProductAttributeFactory.create(key="size", values=["S"])]
            ),
            CoreProductVariationFactory.create(
                ean=None,
                attributes=[CoreProductAttributeFactory.create(key="size", values=["M"])]
            )
        ])

        # mock core api to return fake product
        core_api = "inventorum.ebay.apps.accounts.models.EbayUserModel.core_api"
        core_api_mock = self.patch(core_api, new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient))
        core_api_mock.get_product.return_value = core_product
        core_api_mock.reset_mock()

        self.assertFalse(category.features.ean_required)
        self.assertTrue(all(v.ean is None for v in core_product.variations))

        # ean not required and not given => validate should not raise
        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()

        category.features.ean_required = True
        category.features.save()

        # ean required but not given => validate should raise
        expected_exception = "The selected category requires each variation to have a valid EAN"

        preparation_service = PublishingPreparationService(product, self.user)
        with self.assertRaises(PublishingValidationException) as exc:
                preparation_service.validate()

        self.assertEqual(exc.exception.message, expected_exception)

        # add ean only to one variation => validate should still raise
        core_product.variations[0].ean = "123456789012"
        preparation_service = PublishingPreparationService(product, self.user)
        with self.assertRaises(PublishingValidationException) as exc:
                preparation_service.validate()

        self.assertEqual(exc.exception.message, expected_exception)

        # add ean to the second variation as well => product should be valid again, i.e. not raise
        core_product.variations[1].ean = "123456789012"
        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()

        # remove ean again, mark product as "ean-less" => should still be valid
        core_product.variations[0].ean = core_product.variations[1].ean = None

        product.ean_does_not_apply = True
        product.save()

        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()

    @ApiTest.use_cassette("test_publishing_service_publish_and_unpublish.yaml", match_on=['body'])
    def test_publishing(self):
        product = self.get_product(StagingTestAccount.Products.IPAD_STAND, self.account)

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
        product = self.get_product(StagingTestAccount.Products.WITH_VARIATIONS_VALID_ATTRS, self.account)
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
        self.assertEqual(first_variation_obj.quantity, 1)
        self.assertEqual(first_variation_obj.gross_price, D("150"))
        self.assertEqual(first_variation_obj.tax_rate, D("7"))
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

        first_variation = variations_data[1]

        self.assertEqual(first_variation, {
            'Quantity': 1,
            'StartPrice': '150.00',
            'SKU': 'invtest_666030',
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'Größe (*)',
                        'Value': '22'
                    },
                    {
                        'Name': 'Material (*)',
                        'Value': 'Denim'
                    },
                    {
                        'Name': 'Farbe (*)',
                        'Value': 'Red'
                    },
                ]
            }
        })

        second_variation = variations_data[0]

        self.assertEqual(second_variation, {
            'Quantity': 2,
            'StartPrice': '130.00',
            'SKU': 'invtest_666031',
            'VariationSpecifics': {
                'NameValueList': [
                    {
                        'Name': 'Größe (*)',
                        'Value': '50'
                    },
                    {
                        'Name': 'Material (*)',
                        'Value': 'Leather'
                    },
                    {
                        'Name': 'Farbe (*)',
                        'Value': 'Blue'
                    },
                ]
            }
        })

        self.assertEqual(data['Variations']['VariationSpecificsSet'], {
            'NameValueList': [
                {
                    'Name': 'Farbe (*)',
                    'Value': ['Blue', 'Red']
                },
                {
                    'Name': 'Material (*)',
                    'Value': ['Leather', 'Denim']
                },
                {
                    'Name': 'Größe (*)',
                    'Value': ['50', '22']
                }
            ]
        })

        pictures_set = data['Variations']['Pictures']
        self.assertEqual(pictures_set,
                         {
                             'VariationSpecificName': 'Größe (*)',
                             'VariationSpecificPictureSet': [
                                 {
                                     'PictureURL': [
                                         'http://app.inventorum.net/uploads/img-hash/29de/128c/e87a/4c7c/2f6d/1424/ea3c/29de128ce87a4c7c2f6d1424ea3cc424_ipad_retina.JPEG'],
                                     'VariationSpecificValue': '50'
                                 },
                                 {
                                     'PictureURL': [
                                         'http://app.inventorum.net/uploads/img-hash/a2b4/90f3/6717/6129/9548/428d/6205/a2b490f3671761299548428d6205e2e0_ipad_retina.JPEG'],
                                     'VariationSpecificValue': '22'
                                 }
                             ]
                         })

    def test_product_with_invalid_attributes_for_ebay(self):
        product = self.get_product(StagingTestAccount.Products.WITH_VARIATIONS_INVALID_ATTRS, self.account)
        with ApiTest.use_cassette("get_product_with_variations_invalid_attrs_for_testing_builder.yaml"):
            self._assign_category(product)
            self.assign_valid_shipping_services(product)
            self._add_specific_to_product(product)

            preparation_service = PublishingPreparationService(product, self.user)
            with self.assertRaises(PublishingValidationException) as exc:
                preparation_service.validate()

            self.assertEqual(exc.exception.message,
                             "All variations needs to have exactly the same number of attributes")

    @ApiTest.use_cassette("get_product_for_click_and_collect.yaml")
    def test_builder_for_click_and_collect(self):
        product = self.get_product(StagingTestAccount.Products.PRODUCT_WITH_SHIPPING_SERVICES, self.account)
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

    def test_publish_for_click_and_collect(self):
        with ApiTest.use_cassette("test_publish_product_for_click_and_collect.yaml") as cass:
            product = self.get_product(StagingTestAccount.Products.IPAD_STAND, self.account)
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

        inventory_add_request = None
        for r in requests:
            if r.uri == 'https://api.ebay.com/selling/inventory/v1/inventory/delta/add':
                inventory_add_request = r
                break

        self.assertIsNotNone(inventory_add_request)
        body = Response(ResponseDataObject({'content': inventory_add_request.body.encode('utf-8')}, [])).dict()
        self.assertEqual(body, {
            'AddInventoryRequest': {'Locations': {'Location': {'Availability': 'IN_STOCK',
                                                               'LocationID': 'invdev_346',
                                                               'Quantity': '5'}},
                                    'SKU': last_item.sku}})
