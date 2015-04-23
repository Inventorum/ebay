# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import Ebay
from inventorum.ebay.lib.ebay.data.items import EbayAddItemResponse, EbayUnpublishReasons, EbayEndItemResponse, \
    EbayReviseFixedPriceItemResponse


class EbayItems(Ebay):

    def publish(self, item):
        """
        Publish item to ebay
        :type item: inventorum.ebay.lib.ebay.data.items.EbayFixedPriceItem
        :rtype: EbayAddItemResponse
        """
        response = self.execute('AddItem', item.dict())
        return EbayAddItemResponse.create_from_data(response)

    def unpublish(self, item_id, reason=EbayUnpublishReasons.NOT_AVAILABLE):
        """
        :type item_id: unicode
        :type reason: unicode
        :rtype: EbayEndItemResponse
        """
        response = self.execute('EndItem', {
            'ItemID': item_id,
            'EndingReason': reason
        })
        return EbayEndItemResponse.create_from_data(response)

    def revise_fixed_price_item(self, revise_fixed_price_item):
        """
        :type revise_fixed_price_item: inventorum.ebay.lib.ebay.data.items.EbayReviseFixedPriceItem
        :rtype: EbayReviseFixedPriceItemResponse
        """
        response = self.execute('ReviseInventoryStatus', revise_fixed_price_item.dict())
        return EbayReviseFixedPriceItemResponse.create_from_data(response)
