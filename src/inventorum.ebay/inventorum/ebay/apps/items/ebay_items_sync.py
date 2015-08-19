import logging

log = logging.getLogger(__name__)


class EbayItemsSync(object):
    """ Gets all item_ids and then all items from ebay.
        Filters received ebay_items if sku exists ->
        Call OldEbayItemImporter """
    pass


class OldEbayItemImporter(object):
    """ Gets ebay_item and converts it to ebay_item_model -> store in database """
    pass
