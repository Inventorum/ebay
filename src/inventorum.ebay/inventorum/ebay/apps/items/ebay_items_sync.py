import logging
from inventorum.ebay.apps.products.models import EbayItemModel

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

        self.sync = IncomingEbayOrderSyncer(self.account)


class OldEbayItemImporter(object):
    """ Gets ebay_item and converts it to ebay_item_model -> store in database """

    @classmethod
    def convert_to_ebay_item_model(cls, ebay_item):
        log.info(ebay_item)


class IncomingEbayOrderSyncer(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def __call__(self, ebay_item):
        """
        :type ebay_items: inventorum.ebay.lib.ebay.data.items.EbayFixedPriceItem
        """

        if hasattr(ebay_item, 'sku') and ebay_item.sku.startswith('inv'):
            OldEbayItemImporter.convert_to_ebay_item_model(ebay_item)
            
        else:
            # Currently, we do not perform any updates since we're only fetching completed orders
            log.info("Item was not created via Inventorum".format(ebay_item))
