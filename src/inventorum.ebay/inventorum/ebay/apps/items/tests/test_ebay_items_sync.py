# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.apps.items import EbaySKU
from inventorum.ebay.apps.items.ebay_items_sync_services import IncomingEbayItemSyncer
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.lib.ebay.data.items import EbayFixedPriceItem, EbayPicture, EbayPickupInStoreDetails, \
    EbayShippingDetails, EbayShippingServiceOption
from inventorum.ebay.lib.ebay.tests.factories import EbayTokenFactory
from inventorum.ebay.tests import Countries
from inventorum.ebay.tests.testcases import UnitTestCase
import logging

log = logging.getLogger(__name__)


class UnitTestEbayItemsSyncer(UnitTestCase):
    def setUp(self):
        super(UnitTestEbayItemsSyncer, self).setUp()

        ebay_token = EbayTokenFactory.create()
        self.account = EbayAccountFactory.create(token=EbayTokenModel.create_from_ebay_token(ebay_token))
        self.item = EbayItemModel()
        self.default_user = EbayUserFactory.create(account=self.account)

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

    def test_convert_item_with_sku(self):

        item = EbayFixedPriceItem(
            title='testProduct',
            country=Countries.DE,
            description='30',
            listing_duration='30',
            postal_code='12345',
            quantity=1,
            start_price=Decimal('1.00'),
            paypal_email_address='test@inventorum.com',
            payment_methods=['CreditCard', 'Bar'],
            shipping_details=EbayShippingDetails(EbayShippingServiceOption(shipping_service='DE_UPSStandard')),
            pictures=[
                EbayPicture(url='http://www.testpicture.de/image.png')],
            pick_up=EbayPickupInStoreDetails(is_eligible_for_pick_up=False),
            sku=EbaySKU.get_env_prefix() + '1234',
            category_id='',
            item_id='123abc')

        IncomingEbayItemSyncer(account=self.account, item=item).run()

        self.assertPostcondition(EbayItemModel.objects.count(), 1)

        ebay_model = EbayItemModel.objects.first()
        self.assertIsInstance(ebay_model, EbayItemModel)

        self.assertEqual(ebay_model.account, self.account)
        self.assertEqual(ebay_model.listing_duration, '30')
        self.assertEqual(ebay_model.quantity, 1)
        self.assertEqual(ebay_model.gross_price, 1.00)
        self.assertIsNotNone(ebay_model.category)
        self.assertEqual(ebay_model.country, 'DE')
        self.assertEqual(ebay_model.description, '30')
        self.assertIsNone(ebay_model.ean)
        self.assertEqual(ebay_model.is_click_and_collect, False)
        self.assertEqual(ebay_model.paypal_email_address, 'test@inventorum.com')
        self.assertEqual(ebay_model.postal_code, '12345')

        self.assertEqual(ebay_model.images.count(), 1)
        self.assertEqual(ebay_model.images.first().url, 'http://www.testpicture.de/image.png')

    def test_convert_item_without_sku(self):

        item = EbayFixedPriceItem(
            title='testProduct',
            country=Countries.DE,
            description='30',
            listing_duration='30',
            postal_code='12345',
            quantity=1,
            start_price=Decimal('1.00'),
            paypal_email_address='test@inventorum.com',
            payment_methods=['CreditCard', 'Bar'],
            shipping_details=EbayShippingDetails(EbayShippingServiceOption(shipping_service='DE_UPSStandard')),
            pictures=[
                EbayPicture(url='http://www.testpicture.de/image.png')],
            pick_up=EbayPickupInStoreDetails(is_eligible_for_pick_up=False),
            category_id='',
            item_id='123abc')

        IncomingEbayItemSyncer(account=self.account, item=item).run()

        self.assertPostcondition(EbayItemModel.objects.count(), 0)
