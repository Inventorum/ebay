# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import logging
from inventorum_ebay.apps.accounts.tests import AccountTestMixin

from inventorum_ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum_ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, DurationModel
from inventorum_ebay.apps.categories.tests.factories import CategoryFactory
from inventorum_ebay.apps.items import EbaySKU
from inventorum_ebay.apps.items.ebay_items_sync_services import IncomingEbayItemSyncer, EbayItemsSync
from inventorum_ebay.apps.products import EbayItemPublishingStatus
from inventorum_ebay.apps.products.models import EbayItemModel
from inventorum_ebay.apps.products.services import PublishingPreparationService, PublishingService, UnpublishingService
from inventorum_ebay.apps.products.tests import ProductTestMixin
from inventorum_ebay.apps.shipping.tests import ShippingServiceTestMixin
from inventorum_ebay.lib.celery import celery_test_case
from inventorum_ebay.lib.core_api.clients import UserScopedCoreAPIClient
from inventorum_ebay.lib.core_api.tests.factories import CoreProductFactory
from inventorum_ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayPicture, EbayPickupInStoreDetails, \
    EbayShippingDetails, EbayShippingServiceOption, EbayPriceModel
from inventorum_ebay.tests import Countries, MockedTest, StagingTestAccount, IntegrationTest
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase
from inventorum.util.celery import TaskExecutionContext
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
            item_id='123abc'
        )
        self.default_user = EbayUserFactory.create(account=self.account)

        self.core_api_mock = self.patch(
            'inventorum_ebay.apps.accounts.models.EbayAccountModel.core_api',
            new_callable=PropertyMock(spec_set=UserScopedCoreAPIClient),
        )

        self.schedule_core_api_publishing_status_update_mock = self.patch(
            'inventorum_ebay.apps.items.ebay_items_sync_services.schedule_core_api_publishing_status_update'
        )

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

    def test_serialize_item_with_sku(self):
        self.core_api_mock.get_product.return_value = CoreProductFactory.create(inv_id=self.test_inv_product_id)

        common_category_attrs = dict(ebay_leaf=True, features=None)
        self.category_model = CategoryFactory.create(external_id='1245', name="EAN disabled", country='DE',
                                                     **common_category_attrs)
        CategoryFactory.create(external_id='1245', name="EAN disabled", country='AT', **common_category_attrs)

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

        self.assertEqual(self.schedule_core_api_publishing_status_update_mock.call_count, 1)
        self.schedule_core_api_publishing_status_update_mock.assert_called_with(
            ebay_item_id=ebay_model.id,
            context=TaskExecutionContext(
                account_id=self.account.id,
                user_id=self.account.default_user.id,
                request_id=None
            )
        )

    def test_convert_item_without_sku(self):
        self.item.sku = 'weirdRandomStuff'

        IncomingEbayItemSyncer(account=self.account, item=self.item).run()
        # No EbayItemModel should be created, as it is not an inventorum product.
        self.assertEquals(EbayItemModel.objects.count(), 0)

    def test_serialize_duplicated_item(self):
        self.core_api_mock.get_product.return_value = CoreProductFactory.create(inv_id=self.test_inv_product_id)

        common_category_attrs = dict(ebay_leaf=True, features=None)
        self.category_model = CategoryFactory.create(external_id='1245', name="EAN disabled", **common_category_attrs)

        IncomingEbayItemSyncer(account=self.account, item=self.item).run()
        self.assertPostcondition(EbayItemModel.objects.count(), 1)
        ebay_model = EbayItemModel.objects.first()
        self.assertIsInstance(ebay_model, EbayItemModel)

        # start Syncer again with the same item, shouldn't create another EbayItem
        IncomingEbayItemSyncer(account=self.account, item=self.item).run()
        self.assertPostcondition(EbayItemModel.objects.count(), 1)


class IntegrationTestEbayItemsSync(EbayAuthenticatedAPITestCase, AccountTestMixin, ProductTestMixin,
                                   ShippingServiceTestMixin):

    def setUp(self):
        super(IntegrationTestEbayItemsSync, self).setUp()
        self.prepare_account_for_publishing(self.account)

    @IntegrationTest.use_cassette('items_sync/get_product_id_from_core_api_for_ebay_item_serializer.yaml')
    def test_convert_items_without_sku(self):
        common_category_attrs = dict(ebay_leaf=True, features=None)

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

        self.category_model = CategoryFactory.create(external_id='22416', name="EAN disabled", **common_category_attrs)

        EbayItemsSync(account=self.account).run()

        self.assertPostcondition(EbayItemModel.objects.count(), 0)

    @IntegrationTest.use_cassette('items_sync/publish_and_sync_published_item.yaml')
    @celery_test_case()
    def test_create_product_with_sku_and_serialize_it(self):
        self.assertPrecondition(EbayItemModel.objects.count(), 0)

        # ---- create and publish the test product ---- #
        product = self.get_valid_ebay_product_for_publishing(account=self.account,
                                                             inv_id=StagingTestAccount.Products.IPAD_STAND)

        preparation_service = PublishingPreparationService(product, self.user)
        preparation_service.validate()
        item = preparation_service.create_ebay_item()

        publishing_service = PublishingService(item, self.user)
        publishing_service.publish()
        # deleted the item to make sure that it is recreated by the serializer
        item.delete()

        # ---- start sync ----#
        self.assertPrecondition(EbayItemModel.objects.count(), 0)
        EbayItemsSync(account=self.account).run()
        self.assertPostcondition(EbayItemModel.objects.count(), 1)

        ebay_model = EbayItemModel.objects.first()
        self.assertIsInstance(ebay_model, EbayItemModel)
        self.assertEqual(ebay_model.publishing_status, EbayItemPublishingStatus.PUBLISHED)

        # ---- unpublish the test product ---- #
        unpublishing_service = UnpublishingService(ebay_model, self.user)
        unpublishing_service.unpublish()

        self.assertEqual(ebay_model.publishing_status, EbayItemPublishingStatus.UNPUBLISHED)
