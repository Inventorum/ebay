# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal as D, Decimal

from inventorum.ebay.tests import StagingTestAccount

from ebaysdk.response import Response, ResponseDataObject
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory, CategorySpecificFactory, DurationFactory
from inventorum.ebay.tests import ApiTest
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.services import PublishingService, PublishingValidationException, \
    UnpublishingService, PublishingPreparationService
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.products.tests.factories import EbayProductSpecificFactory, EbayProductFactory, \
    EbayProductModelFactory
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.lib.core_api.tests.factories import CoreProductFactory, CoreProductVariationFactory, \
    CoreProductAttributeFactory, CoreInfoFactory, CoreTaxTypeFactory, CoreImageFactory
from inventorum.ebay.lib.ebay.data import SellerProfileCodeType, BuyerPaymentMethodCodeType
from inventorum.ebay.lib.ebay.data.tests.preferences_factories import GetUserPreferencesResponseTypeFactory, \
    SupportedSellerProfileTypeFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
from mock import PropertyMock, Mock

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


class UnitTestPublishingPreparationService(UnitTestCase, ShippingServiceTestMixin):
    """
    This test case does not communicate with eBay nor the core api. Instead, it mocks the communication with
    these external dependencies and allows to configure expected responses.
    """

    def setUp(self):
        super(UnitTestPublishingPreparationService, self).setUp()

        self.setup_mocked_dependencies()
        self.setup_valid_configuration()

    def setup_mocked_dependencies(self):
        self.core_api_mock = self.patch('inventorum.ebay.apps.accounts.models.EbayUserModel.core_api',
                                        new_callable=PropertyMock(return_value=Mock(spec_set=UserScopedCoreAPIClient)))
        self.ebay_get_user_preferences_mock = self.patch(
            'inventorum.ebay.apps.products.services.EbayPreferences.get_user_preferences')

    def setup_valid_configuration(self):
        # create models that are required to configure a valid ebay product
        self.category = CategoryFactory.create(name='Some leaf category',
                                               external_id='712304',
                                               features__ean_required=False,
                                               features__durations=[DurationFactory(value='Days_30'),
                                                                    DurationFactory(value='Days_60'),
                                                                    DurationFactory(value='Days_90')])
        self.category_specific = CategorySpecificFactory.create(name="Brand",
                                                                category=self.category)

        self.shipping_service = self.get_shipping_service_dhl()

        # create and configure ebay product model
        self.ebay_product = EbayProductModelFactory.create(account=self.account,
                                                           category=self.category,
                                                           ean_does_not_apply=False)

        self.ebay_product.specific_values.create(specific=self.category_specific,
                                                 value="Felt")

        self.ebay_product.shipping_services.create(service=self.shipping_service,
                                                   cost=Decimal('4.90'))

        # expect valid default responses from the core api and from eBay
        self.expect_core_product(core_product=self.get_valid_core_product())
        self.expect_core_info(core_info=self.get_valid_core_info())
        self.expect_ebay_seller_profiles(seller_profiles=[self.get_valid_ebay_return_seller_profile()])

        # enable and configure payment methods
        self.account.payment_method_paypal_enabled = True
        self.account.payment_method_paypal_email_address = "julian@inventorum.com"

        self.account.payment_method_bank_transfer_enabled = True
        self.account.save()

    # -Helper methods ---------------------------

    def get_valid_core_product(self):
        """
        :rtype: inventorum.ebay.lib.core_api.models.CoreProduct
        """
        return CoreProductFactory.create(id=941284,
                                         name='Felt Brougham',
                                         description='Awesome street bikes are awesome',
                                         ean="038678561125",
                                         gross_price=D('499.99'),
                                         quantity=100,
                                         tax_type_id=32345,
                                         images=[CoreImageFactory.create(
                                             urls__ipad_retina='http://image/felt_brougham.png')])

    def get_valid_core_product_with_variations(self):
        variations = [
            CoreProductVariationFactory.create(id=942445,
                                               ean='118678561129',
                                               quantity=30,
                                               gross_price='29.99',
                                               tax_type_id=32346,
                                               attributes=[CoreProductAttributeFactory.create(key='color',
                                                                                              values=['black']),
                                                           CoreProductAttributeFactory.create(key='size',
                                                                                              values=['s'])],
                                               images=[CoreImageFactory.create(
                                                   urls__ipad_retina='http://image/shirt_s_black.png')]),
            CoreProductVariationFactory.create(id=942446,
                                               ean='118678561130',
                                               quantity=20,
                                               gross_price='34.99',
                                               tax_type_id=32346,
                                               attributes=[CoreProductAttributeFactory.create(key='color',
                                                                                              values=['italy']),
                                                           CoreProductAttributeFactory.create(key='size',
                                                                                              values=['m'])],
                                               images=[CoreImageFactory.create(
                                                   urls__ipad_retina='http://image/shirt_m_italy.png')])]

        return CoreProductFactory.create(id=941441,
                                         name='Felt Tracking T-Shirt',
                                         description='Awesome T-Shirts are awesome',
                                         gross_price=D("0.00"),
                                         quantity=50,
                                         tax_type_id=32346,
                                         variations=variations)

    def get_valid_core_info(self):
        """
        :rtype: inventorum.ebay.lib.core_api.models.CoreInfo
        """
        return CoreInfoFactory.create(tax_types=[CoreTaxTypeFactory.create(id=32345, tax_rate=D('19.000')),
                                                 CoreTaxTypeFactory.create(id=32346, tax_rate=D('7.000'))],
                                      account__billing_address__zipcode='33098',
                                      account__settings__ebay_click_and_collect=False)

    def get_valid_ebay_return_seller_profile(self):
        """
        :rtype: inventorum.ebay.lib.ebay.data.preferences.SupportedSellerProfileType
        """
        return SupportedSellerProfileTypeFactory.create(profile_id="73359920011",
                                                        profile_type=SellerProfileCodeType.RETURN_POLICY,
                                                        category_group__is_default=True)

    def expect_core_product(self, core_product):
        """
        :type core_product: inventorum.ebay.lib.core_api.models.CoreProduct
        """
        self.core_api_mock.get_product.reset_mock()
        self.core_api_mock.get_product.return_value = core_product

    def expect_core_info(self, core_info):
        """
        :type core_info: inventorum.ebay.lib.core_api.models.CoreInfo
        """
        self.core_api_mock.get_account_info.reset_mock()
        self.core_api_mock.get_account_info.return_value = core_info

    def expect_ebay_seller_profiles(self, seller_profiles):
        """
        :type seller_profiles: list[inventorum.ebay.lib.ebay.data.preferences.SupportedSellerProfileType]
        """
        self.ebay_get_user_preferences_mock.reset_mock()

        ebay_user_preferences = GetUserPreferencesResponseTypeFactory.create(
            seller_profile_preferences__supported_seller_profiles=seller_profiles)
        self.ebay_get_user_preferences_mock.return_value = ebay_user_preferences

    # -Test methods -----------------------------

    def test_validation_and_builder_with_valid_configuration(self):
        # the preparation service should not raise with this configuration
        preparation_service = PublishingPreparationService(self.ebay_product, self.user)
        preparation_service.validate()

        ebay_item = preparation_service.create_ebay_item()
        ebay_item = ebay_item.reload()

        self.assertEqual(ebay_item.account, self.account)
        self.assertEqual(ebay_item.product, self.ebay_product)
        self.assertEqual(ebay_item.category, self.category)
        self.assertEqual(ebay_item.name, 'Felt Brougham')
        self.assertEqual(ebay_item.description, 'Awesome street bikes are awesome')
        self.assertEqual(ebay_item.ean, '038678561125')
        self.assertEqual(ebay_item.quantity, 100)
        self.assertEqual(ebay_item.gross_price, D("499.99"))
        self.assertEqual(ebay_item.tax_rate, D("19.000"))

        self.assertEqual(ebay_item.postal_code, '33098')
        self.assertEqual(ebay_item.country, 'DE')
        self.assertEqual(ebay_item.paypal_email_address, 'julian@inventorum.com')

        self.assertEqual(ebay_item.listing_duration, 'Days_90', 'Listing duration should be the max. allowed listing '
                                                                'duration of the selected category')

        self.assertEqual(ebay_item.ebay_seller_profile_return_policy_id, '73359920011')

        # validate payment methods
        payment_methods = ebay_item.payment_methods.all()
        self.assertEqual(payment_methods.count(), 2, 'Paypal and bank transfer should be enabled ')
        self.assertItemsEqual([p.external_id for p in payment_methods], [BuyerPaymentMethodCodeType.PayPal,
                                                                         BuyerPaymentMethodCodeType.MoneyXferAccepted])
        # validate shipping services
        shipping_details = ebay_item.shipping.all()
        self.assertEqual(shipping_details.count(), 1, 'There should be one shipping service')
        self.assertEqual(shipping_details[0].cost, D("4.90"))
        self.assertEqual(shipping_details[0].external_id, "DE_DHLPaket")

        # validate images
        images = ebay_item.images.all()
        self.assertEqual(images.count(), 1, 'There should be one image')
        self.assertEqual(images[0].url, 'http://image/felt_brougham.png')

        # validate item specifics
        specific_values = ebay_item.specific_values.all()
        self.assertEqual(specific_values.count(), 1)
        self.assertEqual(specific_values[0].specific, self.category_specific)
        self.assertEqual(specific_values[0].value, 'Felt')

        # assert complete ebay payload
        data = ebay_item.ebay_object.dict()
        self.assertEqual(data['Item'], {'ConditionID': 1000,
                                        'Country': 'DE',
                                        'Currency': 'EUR',
                                        'Description': '<![CDATA[Awesome street bikes are awesome]]>',
                                        'DispatchTimeMax': 3,
                                        'ItemSpecifics': {'NameValueList': [{'Name': 'Brand',
                                                                             'Value': 'Felt'}]},
                                        'ListingDuration': 'Days_90',
                                        'ListingType': 'FixedPriceItem',
                                        'PayPalEmailAddress': 'julian@inventorum.com',
                                        'PaymentMethods': ['MoneyXferAccepted', 'PayPal'],
                                        'PictureDetails': {
                                            'PictureURL': ['http://image/felt_brougham.png']},
                                        'PostalCode': '33098',
                                        'PrimaryCategory': {'CategoryID': '712304'},
                                        'ProductListingDetails': {'EAN': '038678561125'},
                                        'Quantity': 100,
                                        'ReturnPolicy': {'Description': '',
                                                         'ReturnsAcceptedOption': 'ReturnsAccepted'},
                                        'SKU': 'invtest_941284',
                                        'ShippingDetails': {
                                            'ShippingServiceOptions': [{'ShippingService': 'DE_DHLPaket',
                                                                        'ShippingServiceAdditionalCost': '0.00',
                                                                        'ShippingServiceCost': '4.90',
                                                                        'ShippingServicePriority': 1}]},
                                        'StartPrice': '499.99',
                                        'Title': 'Felt Brougham'})

    def test_validation_and_builder_with_variations(self):
        self.expect_core_product(core_product=self.get_valid_core_product_with_variations())

        preparation_service = PublishingPreparationService(self.ebay_product, self.user)
        preparation_service.validate()

        ebay_item = preparation_service.create_ebay_item()
        ebay_item = ebay_item.reload()

        variations = ebay_item.variations.all()
        self.assertEqual(variations.count(), 2)

        # assert item variation data for the first variation
        variation_a = variations.get(inv_product_id=942445)
        self.assertEqual(variation_a.ean, '118678561129')
        self.assertEqual(variation_a.quantity, 30)
        self.assertEqual(variation_a.gross_price, D('29.99'))
        self.assertEqual(variation_a.tax_rate, D('7.000'))

        variation_a_images = variation_a.images.all()
        self.assertEqual(variation_a_images.count(), 1)
        self.assertEqual(variation_a_images[0].url, 'http://image/shirt_s_black.png')

        variation_a_specifics = variation_a.specifics.all()
        self.assertEqual(variation_a_specifics.count(), 2)

        self.assertEqual(variation_a_specifics[0].name, "size")
        self.assertEqual(variation_a_specifics[0].values.first().value, "s")
        self.assertEqual(variation_a_specifics[1].name, "color")
        self.assertEqual(variation_a_specifics[1].values.first().value, "black")

        # assert item variation data for the second variation
        variation_b = variations.get(inv_product_id=942446)
        self.assertEqual(variation_b.ean, '118678561130')
        self.assertEqual(variation_b.quantity, 20)
        self.assertEqual(variation_b.gross_price, D('34.99'))
        self.assertEqual(variation_b.tax_rate, D('7.000'))

        variation_b_images = variation_b.images.all()
        self.assertEqual(variation_b_images.count(), 1)
        self.assertEqual(variation_b_images[0].url, 'http://image/shirt_m_italy.png')

        variation_b_specifics = variation_b.specifics.all()
        self.assertEqual(variation_b_specifics.count(), 2)

        self.assertEqual(variation_b_specifics[0].name, "size")
        self.assertEqual(variation_b_specifics[0].values.first().value, "m")
        self.assertEqual(variation_b_specifics[1].name, "color")
        self.assertEqual(variation_b_specifics[1].values.first().value, "italy")

        # assert complete ebay payload with variations
        data = ebay_item.ebay_object.dict()
        self.assertEqual(data['Item']['Variations'],
                         {'Variation': [{'Quantity': 20,
                                         'SKU': 'invtest_942446',
                                         'StartPrice': '34.99',
                                         'VariationProductListingDetails': {'EAN': '118678561130'},
                                         'VariationSpecifics': {
                                             'NameValueList': [{'Name': 'Gr\xf6\xdfe (*)', 'Value': 'm'},
                                                               {'Name': 'Farbe (*)', 'Value': 'italy'}]}},
                                        {'Quantity': 30,
                                         'SKU': 'invtest_942445',
                                         'StartPrice': '29.99',
                                         'VariationProductListingDetails': {'EAN': '118678561129'},
                                         'VariationSpecifics': {
                                             'NameValueList': [{'Name': 'Gr\xf6\xdfe (*)', 'Value': 's'},
                                                               {'Name': 'Farbe (*)', 'Value': 'black'}]}}],
                          'Pictures': {'VariationSpecificName': 'Gr\xf6\xdfe (*)',
                                       'VariationSpecificPictureSet': [
                                           {'PictureURL': ['http://image/shirt_m_italy.png'],
                                            'VariationSpecificValue': 'm'},
                                           {'PictureURL': ['http://image/shirt_s_black.png'],
                                            'VariationSpecificValue': 's'}]},
                          'VariationSpecificsSet': {'NameValueList': [
                              {'Name': 'Farbe (*)', 'Value': ['black', 'italy']},
                              {'Name': 'Gr\xf6\xdfe (*)', 'Value': ['s', 'm']}]}})

    def test_validation_and_builder_with_click_and_collect(self):
        # activate click and collect for the core account
        core_info = self.get_valid_core_info()
        core_info.account.settings.ebay_click_and_collect = True
        self.expect_core_info(core_info)

        # activate click and collect for the product
        self.ebay_product.is_click_and_collect = True
        self.ebay_product.save()

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        self.assertEqual(ebay_item.is_click_and_collect, True)

        # Check data builder
        ebay_item = ebay_item.ebay_object

        data = ebay_item.dict()
        item_data = data['Item']
        self.assertIn('PickupInStoreDetails', item_data)
        self.assertIn('AutoPay', item_data)
        self.assertEqual(item_data['AutoPay'], True)

        self.assertIn('EligibleForPickupInStore', item_data['PickupInStoreDetails'])
        self.assertEqual(item_data['PickupInStoreDetails']['EligibleForPickupInStore'], True)

    def test_attribute_validation(self):
        core_product = self.get_valid_core_product_with_variations()

        # Precondition: Both variations have two attributes
        self.assertEqual(len(core_product.variations[0].attributes), 2)
        self.assertEqual(len(core_product.variations[1].attributes), 2)

        # We remove one attribute from the second variation
        core_product.variations[1].attributes.pop()

        self.expect_core_product(core_product)

        preparation_service = PublishingPreparationService(self.ebay_product, self.user)
        with self.assertRaises(PublishingValidationException) as exc:
            preparation_service.validate()

        self.assertEqual(exc.exception.message,
                         'All variations needs to have exactly the same number of attributes')

    def test_return_policy_validation(self):
        # when there is no configured seller profile
        seller_profiles = []
        self.expect_ebay_seller_profiles(seller_profiles)

        # ean not required and not given => validate should not raise
        expected_exception = 'Product could not be published! There is no default ' \
                             'return policy defined in your eBay account.'

        preparation_service = PublishingPreparationService(self.ebay_product, self.user)
        with self.assertRaises(PublishingValidationException) as exc:
            preparation_service.validate()

        self.assertEqual(exc.exception.message, expected_exception)

        # when there is no configured default return seller profile
        seller_profiles = [SupportedSellerProfileTypeFactory.create(profile_type=SellerProfileCodeType.PAYMENT,
                                                                    category_group__is_default=True),
                           SupportedSellerProfileTypeFactory.create(profile_type=SellerProfileCodeType.SHIPPING,
                                                                    category_group__is_default=True)]
        self.expect_ebay_seller_profiles(seller_profiles)

    def test_account_shipping_fallback(self):
        self.ebay_product.shipping_services.delete()
        self.assertEqual(self.ebay_product.shipping_services.count(), 0,
                         'Precondition: The product should have no shipping service configurations')
        self.assertEqual(self.ebay_product.shipping_services.count(), 0,
                         'Precondition: The account should have no shipping services configuration')

        # Add valid shipping service configuration to account
        self.account.shipping_services.create(service=self.get_shipping_service_hermes(),
                                              cost=D("3.00"), additional_cost=D("0.00"))

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        shipping_services = ebay_item.shipping.all()

        self.assertEqual(shipping_services.count(), 1)
        self.assertEqual(shipping_services[0].external_id, "DE_HermesPaket")
        self.assertEqual(shipping_services[0].cost, D("3.00"))
        self.assertEqual(shipping_services[0].additional_cost, D("0.00"))

    def test_ean_does_not_apply_for_product(self):
        # expect core product with some EAN
        core_product = self.get_valid_core_product()
        self.assertIsNotNone(core_product.ean, 'Precondition: Core product has EAN')
        self.expect_core_product(core_product)

        # activate ean does not apply for product
        self.ebay_product.ean_does_not_apply = True

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        self.assertEqual(ebay_item.ean, 'Does not apply', 'Postcondition: Product should be published with '
                                                          'EAN ``Does not apply``')

    def test_ean_does_not_apply_for_product_with_variations(self):
        # expect core product with variations with some EAN
        core_product = self.get_valid_core_product_with_variations()
        self.assertIsNotNone(core_product.variations[0].ean, 'Precondition: Core variation has EAN')
        self.assertIsNotNone(core_product.variations[1].ean, 'Precondition: Core variation has EAN')
        self.expect_core_product(core_product)

        # activate ean does not apply for product
        self.ebay_product.ean_does_not_apply = True

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        variations = list(ebay_item.variations.all())
        self.assertEqual(variations[0].ean, 'Does not apply', 'Postcondition: Variation should be published '
                                                              'with EAN ``Does not apply``')
        self.assertEqual(variations[1].ean, 'Does not apply', 'Postcondition: Variation should be published '
                                                              'with EAN ``Does not apply``')

    def test_ean_does_not_apply_fallback(self):
        # expect core product without ean
        core_product = self.get_valid_core_product()
        core_product.ean = None
        self.expect_core_product(core_product)

        self.assertEqual(self.category.features.ean_required, False,
                         'Precondition: Category does not require a valid EAN')

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        self.assertEqual(ebay_item.ean, None, 'EAN can be ``None`` when category does not require a valid EAN')

        # change category to require a valid EAN
        self.category.features.ean_required = True
        self.category.features.save()

        self.ebay_product = self.ebay_product.reload()
        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        self.assertEqual(ebay_item.ean, 'Does not apply', 'EAN should fallback to ``Does not apply`` when required '
                                                          'by the category but not set in core api')

    def test_ean_does_not_apply_fallback_with_variations(self):
        # expect core product with variations without ean
        core_product = self.get_valid_core_product_with_variations()
        core_product.variations[0].ean = None
        core_product.variations[1].ean = None
        self.expect_core_product(core_product)

        self.assertEqual(self.category.features.ean_required, False,
                         'Precondition: Category does not require a valid EAN')

        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        variations = list(ebay_item.variations.all())
        self.assertEqual(variations[0].ean, None,
                         'EAN can be ``None`` when category does not require a valid EAN')
        self.assertEqual(variations[1].ean, None,
                         'EAN can be ``None`` when category does not require a valid EAN')

        # change category to require a valid EAN
        self.category.features.ean_required = True
        self.category.features.save()

        self.ebay_product = self.ebay_product.reload()
        service = PublishingPreparationService(self.ebay_product, self.user)
        service.validate()
        ebay_item = service.create_ebay_item()

        variations = list(ebay_item.variations.all())
        self.assertEqual(variations[0].ean, 'Does not apply',
                         'EAN should fallback to ``Does not apply`` when required by the category '
                         'but not set for the variation in the core api')

        self.assertEqual(variations[1].ean, 'Does not apply',
                         'EAN should fallback to ``Does not apply`` when required by the category '
                         'but not set for the variation in the core api')
