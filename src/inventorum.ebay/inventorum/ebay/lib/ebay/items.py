# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.items import EbayAddItemResponse, EbayUnpublishReasons, EbayEndItemResponse, \
    EbayReviseFixedPriceItemResponse, EbayGetItemResponse, EbayGetItemId
import datetime


class EbayItems(EbayTrading):
    def publish(self, item):
        """
        Publish item to ebay
        :type item: inventorum.ebay.lib.ebay.data.items.EbayFixedPriceItem
        :rtype: EbayAddItemResponse
        """
        response = self.execute('AddFixedPriceItem', item.dict())
        return EbayAddItemResponse.create_from_data(response)

    def unpublish(self, item_id, reason=EbayUnpublishReasons.NOT_AVAILABLE):
        """
        :type item_id: unicode
        :type reason: unicode
        :rtype: EbayEndItemResponse
        """
        response = self.execute('EndFixedPriceItem', {
            'ItemID': item_id,
            'EndingReason': reason
        })
        return EbayEndItemResponse.create_from_data(response)

    def revise_fixed_price_item(self, revise_fixed_price_item):
        """
        :type revise_fixed_price_item: inventorum.ebay.lib.ebay.data.items.EbayReviseFixedPriceItem
        :rtype: EbayReviseFixedPriceItemResponse
        """
        response = self.execute('ReviseFixedPriceItem', revise_fixed_price_item.dict())
        return EbayReviseFixedPriceItemResponse.create_from_data(response)

    def get_item_ids(self):
        """
        Get List of ItemIds from the Items, published on ebay.
        <GranularityLevel>Fine</GranularityLevel>
        <StartTimeFrom>2015-07-12T21:59:59.005Z</StartTimeFrom>
        <StartTimeTo>2015-08-14T17:16:59.005Z</StartTimeTo>
        <Pagination>
            <EntriesPerPage>2</EntriesPerPage>
        </Pagination>
        :return: getItem response
        """
        response = self.execute('GetSellerList', {
            'DetailLevel': 'ReturnAll',
            'StartTimeFrom': '2015-07-12T21:59:59.005Z',
            'StartTimeTo': datetime.datetime.now(),
            'IncludeVariations': 'True',
            'Pagination': {'EntriesPerPage': '50'}
        })
        # get only some items, need to get all (paging over start and )
        return EbayGetItemId.create_from_data(data=response)

    def get_item(self, item_id):
        """
        Get List of item details, which is published on ebay.
        :type item_id: unicode
        :return: EbayGetItemResponse

        <!-- Insert a valid ItemID from a search (on Production or Sandbox, whichever is fitting). -->
            <ItemID>110043671232</ItemID>
        """
        response = self.execute('GetItem', {
            'ItemID': item_id
        })

        return EbayGetItemResponse.create_from_data(data=response)
