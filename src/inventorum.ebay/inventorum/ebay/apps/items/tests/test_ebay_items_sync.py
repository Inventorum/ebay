# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from decimal import Decimal

from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.auth.models import EbayTokenModel
from inventorum.ebay.apps.items.ebay_items_sync import IncomingEbayItemSyncer
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
        self.default_user = EbayUserFactory.create(account=self.account)

        self.assertPrecondition(EbayItemModel.objects.count(), 0)

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
            sku='inv_1234',
            category_id='',
            item_id='123abc')

        sync = IncomingEbayItemSyncer(account=self.account)
        log.debug(sync(item))
