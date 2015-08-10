import logging
from inventorum.ebay.lib.ebay.items import EbayItems

log = logging.getLogger(__name__)


class ImportProductFromEbayService(object):
    log.info('Trying to import products from ebay')

    def __init__(self, account):
        """
        Checking if items ebay is asking for are still in stock
        :param account: account for what the ebay products can be imported
        :type account: [inventorum.ebay.apps.accounts.models.EbayAccountModel]
        """
        self.account = account

    def pull_data(self):
        """
        wdqwd
        :return:
        """
        ebay_api = EbayItems(self.account.token.ebay_object)
        items = ebay_api.get_items()