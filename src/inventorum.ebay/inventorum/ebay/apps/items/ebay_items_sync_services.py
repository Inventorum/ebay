from __future__ import absolute_import, unicode_literals
import logging
from django.db import transaction
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.items import EbaySKU
from inventorum.ebay.apps.products import EbayItemPublishingStatus
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class EbayItemsSync(object):
    """ Gets all item_ids and then all items from ebay.
        Filters received ebay_items if sku exists ->
        Call OldEbayItemImporter """

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


class EbayItemImporter(object):
    """ Gets ebay_item and converts it to ebay_item_model -> store in database """

    def __init__(self, account, item):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.sync = IncomingEbayItemSyncer(account, item)

    @transaction.atomic()
    def convert_to_ebay_item_model(self, ebay_item):
        log.info(ebay_item)
        item_model = EbayItemModel()
        item_model.item_id = ebay_item.item_id
        item_model.category = CategoryFactory()
        item_model.description = ebay_item.description
        item_model.postal_code = ebay_item.postal_code
        item_model.ean = ebay_item.ean
        item_model.is_click_and_collect = ebay_item.pick_up.is_eligible_for_pick_up
        item_model.gross_price = ebay_item.start_price
        item_model.quantity = ebay_item.quantity
        item_model.name = ebay_item.title
        item_model.inv_product_id = ebay_item.sku.split('_')[1]
        item_model.account_id = self.sync.account.id

        item_model.listing_duration = ebay_item.listing_duration
        item_model.country = ebay_item.country
        item_model.product = EbayProductFactory.create()
        item_model.paypal_email_address = ebay_item.paypal_email_address
        item_model.publishing_status = EbayItemPublishingStatus.PUBLISHED

        item_model.save()


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
        if hasattr(self.item, 'sku') and self.item.sku is not None:
            if EbaySKU.belongs_to_current_env(self.item.sku):
                self.start_importer_to_convert_to_ebay_item_model()
            else:
                log.warning('There was an ebay item with another sku (not inventorum): %s', self.item.sku)
                log.warning('No sku for item: %s Of accountId: %s', self.item.item_id, self.account.id)
        else:
            # Currently, we do not perform any updates since we're only fetching completed orders
            log.warning("Item was not created via Inventorum".format(self.item))
            log.warning('No sku for item: ' + str(self.item.item_id) + 'Of accountId: ' + str(self.account.id))

    def start_importer_to_convert_to_ebay_item_model(self):
        importer = EbayItemImporter(self.account, self.item)
        importer.convert_to_ebay_item_model(self.item)

