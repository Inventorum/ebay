import logging
from django.db import transaction
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory

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

        self.sync = IncomingEbayItemSyncer(self.account)


class EbayItemImporter(object):
    """ Gets ebay_item and converts it to ebay_item_model -> store in database """
    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.sync = IncomingEbayItemSyncer(account)

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

        item_model.save()


def start_importer_to_convert_to_ebay_item_model(self, ebay_item):
    importer = EbayItemImporter(self.account)
    importer.convert_to_ebay_item_model(ebay_item)


def add_sku_for_ebay_model(self, ebay_item):
    # needs to be done over new product entry in database, than retry
    # ebay_item.sku = 'inv_123'
    # start_importer_to_convert_to_ebay_item_model(self, ebay_item)

    log.info('No sku for item: ' + ebay_item.item_id + 'Of accountId: ' + self.account.id)


class IncomingEbayItemSyncer(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def __call__(self, ebay_item):
        """
        :type ebay_item: inventorum.ebay.lib.ebay.data.items.EbayFixedPriceItem
        """

        if hasattr(ebay_item, 'sku') and ebay_item.sku is not None:
            if ebay_item.sku.startswith('inv'):
                start_importer_to_convert_to_ebay_item_model(self, ebay_item)
            else:
                log.warning('There was an ebay item with another sku (not inventorum): ' + ebay_item.sku)
                add_sku_for_ebay_model(self, ebay_item)
        else:
            # Currently, we do not perform any updates since we're only fetching completed orders
            log.info("Item was not created via Inventorum".format(ebay_item))
            add_sku_for_ebay_model(self, ebay_item)

