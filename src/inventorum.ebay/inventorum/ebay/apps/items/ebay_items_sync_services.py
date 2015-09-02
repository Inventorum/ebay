from __future__ import absolute_import, unicode_literals
import logging
from django.db import transaction
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.items import EbaySKU
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayItemModel, EbayItemImageModel
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.lib.ebay.items import EbayItems
from array import array


log = logging.getLogger(__name__)


class EbayItemsSync(object):
    """ Gets all item_ids and then all items from ebay.
        To filter received ebay_items if sku exists it
        calls EbayItemImporter. """

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        assert self.account.is_ebay_authenticated, "Account {} is not authenticated to ebay".format(account)

        ebay_api = EbayItems(self.account.token.ebay_object)
        ids = ebay_api.get_item_ids()

        for item_id in ids:
            self.item = ebay_api.get_item(item_id)
            IncomingEbayItemSyncer(self.account, self.item).run()


class IncomingEbayItemSyncer(object):
    def __init__(self, account, item):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        :type item: inventorum.ebay.apps.products.EbayItemModel
        """
        self.account = account
        self.item = item

    def run(self):
        """
        Checks if an ebay item has a valid sku.
        :type ebay_item: inventorum.ebay.lib.ebay.data.items.EbayFixedPriceItem
        """
        if getattr(self.item, 'sku', None) is not None:
            if EbaySKU.belongs_to_current_env(self.item.sku):
                self.convert_to_ebay_item_model()
            else:
                log.warning('There was an ebay item with another sku (not inventorum): %s', self.item.sku)
                log.warning('No sku for item: %s Of accountId: %s', self.item.item_id, self.account.id)
        else:
            # Currently, we do not perform any updates since we're only fetching completed orders
            log.warning("Item was not created via Inventorum".format(self.item))
            log.warning('No sku for item: ' + str(self.item.item_id) + 'Of accountId: ' + str(self.account.id))

    @transaction.atomic()
    def convert_to_ebay_item_model(self):
        """
        Create database model for ebay item and stores it into db.
        """
        item_model = EbayItemModel()
        item_model.item_id = self.item.item_id
        item_model.category = CategoryFactory()
        item_model.description = self.item.description
        item_model.postal_code = self.item.postal_code
        item_model.ean = self.item.ean
        item_model.is_click_and_collect = self.item.pick_up.is_eligible_for_pick_up
        item_model.gross_price = self.item.start_price
        item_model.quantity = self.item.quantity
        item_model.name = self.item.title
        item_model.inv_product_id = self.item.sku.split('_')[1]
        item_model.account_id = self.account.id
        item_model.listing_duration = self.item.listing_duration
        item_model.country = self.item.country
        item_model.product = EbayProductFactory.create()
        item_model.paypal_email_address = self.item.paypal_email_address
        item_model.publishing_status = EbayItemPublishingStatus.PUBLISHED

        item_model.save()

        for picture in self.item.pictures:
            item_model.images.create(url=picture.url)
