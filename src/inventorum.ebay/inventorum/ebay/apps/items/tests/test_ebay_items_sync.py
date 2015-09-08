# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging

from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.items import EbaySKU
from inventorum.ebay.apps.items.ebay_items_sync_services import IncomingEbayItemSyncer, EbayItemsSync
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.services import PublishingPreparationService, PublishingService, UnpublishingService
from inventorum.ebay.apps.products.tests import ProductTestMixin
from inventorum.ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum.ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum.ebay.lib.core_api.tests.factories import CoreProductFactory
from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayPicture, EbayPickupInStoreDetails, \
    EbayShippingDetails, EbayShippingServiceOption, EbayPriceModel
from inventorum.ebay.tests import Countries, MockedTest, StagingTestAccount
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
from mock import PropertyMock

log = logging.getLogger(__name__)


class UnitTestEbayItemsSyncer(EbayAuthenticatedAPITestCase):
    def setUp(self):
        super(UnitTestEbayItemsSyncer, self).setUp()

        self.test_inv_product_id = 1000000000000000123L
        self.item = EbayFixedPriceItem(
            title='testProduct',
            category_id='1245',
            country=Countries.DE,
            description='30',
            listing_duration='30',
            postal_code='12345',
            quantity=1,
            start_price=EbayPriceModel(currency_id='EUR', value=Decimal(1.00)),
            paypal_email_address='test@inventorum.com',
            payment_methods=['CreditCard', 'Bar'],
            shipping_details=EbayShippingDetails(EbayShippingServiceOption(shipping_service='DE_UPSStandard')),
            pictures=[
                EbayPicture(url='http://www.testpicture.de/image.png')],
            pick_up=EbayPickupInStoreDetails(is_click_and_collect=False),
            sku=EbaySKU.generate_sku(self.test_inv_product_id),
            item_id='123abc')
        self.default_user = EbayUserFactory.create(account=self.account)

        self.core_api_mock = self.patch(
            'inventorum.ebay.apps.accounts.models.EbayAccountModel.core_api',
            new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient),
        )

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

    def test_serialize_item_with_sku(self):
        self.core_api_mock.get_product.return_value = CoreProductFactory.create(inv_id=self.test_inv_product_id)

        common_category_attrs = dict(ebay_leaf=True, features=None)
        self.category_model = CategoryFactory.create(external_id='1245', name="EAN disabled", **common_category_attrs)
        self.category_model.save()

        IncomingEbayItemSyncer(account=self.account, item=self.item).run()

        self.assertPostcondition(EbayItemModel.objects.count(), 1)

        ebay_model = EbayItemModel.objects.first()
        self.assertIsInstance(ebay_model, EbayItemModel)

        self.assertEqual(ebay_model.account, self.account)
        self.assertEqual(ebay_model.listing_duration, '30')
        self.assertEqual(ebay_model.quantity, 1)
        self.assertEqual(ebay_model.gross_price, 1.00)
        self.assertEqual(ebay_model.country, 'DE')
        self.assertEqual(ebay_model.description, '30')
        self.assertIsNone(ebay_model.ean)
        self.assertEqual(ebay_model.is_click_and_collect, False)
        self.assertEqual(ebay_model.paypal_email_address, 'test@inventorum.com')
        self.assertEqual(ebay_model.postal_code, '12345')
        self.assertEqual(ebay_model.inv_product_id, self.test_inv_product_id)

        self.assertEqual(ebay_model.images.count(), 1)
        self.assertEqual(ebay_model.images.first().url, 'http://www.testpicture.de/image.png')
        self.assertIsNotNone(ebay_model.category)
        self.assertEqual(ebay_model.category.external_id, '1245')

        self.assertIsNotNone(ebay_model.product)
        self.assertEqual(ebay_model.product.inv_id, self.test_inv_product_id)

    def test_convert_item_without_sku(self):
        self.item.sku = 'weirdRandomStuff'

        IncomingEbayItemSyncer(account=self.account, item=self.item).run()
        # No EbayItemModel should be created, as it is not an inventorum product.
        self.assertEquals(EbayItemModel.objects.count(), 0)


class IntegrationTest(EbayAuthenticatedAPITestCase, ProductTestMixin, ShippingServiceTestMixin):
    @MockedTest.use_cassette('get_product_id_from_core_api_for_ebay_item_serializer.yaml', record_mode="new_episodes")
    def test_convert_items_without_sku(self):
        common_category_attrs = dict(ebay_leaf=True, features=None)

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

        self.category_model = CategoryFactory.create(external_id='22416', name="EAN disabled", **common_category_attrs)

        EbayItemsSync(account=self.account).run()

        self.assertPostcondition(EbayItemModel.objects.count(), 0)
        #
        # ebay_model = EbayItemModel.objects.first()
        # self.assertIsInstance(ebay_model, EbayItemModel)

    @MockedTest.use_cassette('create_product_with_sku_and_serialize_it.yaml', record_mode="new_episodes")
    def test_create_product_with_sku_and_serialize_it(self):
        self.assertPrecondition(EbayItemModel.objects.count(), 0)

        # ---- create and publish the test product ---- #
        product = self.get_product(StagingTestAccount.Products.IPAD_STAND, self.account)
        # 176973 is valid ebay category id
        category, c = CategoryModel.objects.get_or_create(external_id='7484')
        product.category = category
        product.ean_does_not_apply = True
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
        publishing_service.publish()
        item.publishing_status = EbayItemPublishingStatus.UNPUBLISHED
        item.save()

        # ---- start serializer ----#
        EbayItemsSync(account=self.account).run()
        self.assertPostcondition(EbayItemModel.objects.count(), 2)

        ebay_model = EbayItemModel.objects.first()
        self.assertIsInstance(ebay_model, EbayItemModel)

        # ---- unpublish the test product ---- #
        unpublishing_service = UnpublishingService(product.published_item, self.user)
        unpublishing_service.unpublish()

        item = product.published_item
        self.assertIsNone(item)
