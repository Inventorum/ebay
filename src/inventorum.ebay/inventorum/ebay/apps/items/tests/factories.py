import factory
from inventorum.ebay.apps.items.ebay_items_sync import EbayItemsSync


class ItemModelFactory(factory.Factory):
    FACTORY_FOR = EbayItemsSync
