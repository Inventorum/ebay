import logging
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class ImportProductFromEbayService(object):

    def __init__(self, account):
        """
        Checking if items ebay is asking for are still in stock
        :param account: account for what the ebay products can be imported
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def pull_data(self):
        """
        Pulls items from ebay.
        :type ebay: inventorum.ebay.apps.orders.models.OrderModel
        """
        log.info('Trying to import products from ebay')
        ebay_api = EbayItems(self.account.token.ebay_object)
        items = ebay_api.get_items()
