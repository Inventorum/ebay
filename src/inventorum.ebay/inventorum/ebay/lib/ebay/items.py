# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.items import EbayAddItemResponse, EbayUnpublishReasons, EbayEndItemResponse, \
    EbayReviseFixedPriceItemResponse, EbayGetItemResponse


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

    def get_items(self):
        """
        Get List of Items, published on ebay.
        <GranularityLevel>Fine</GranularityLevel>
        <StartTimeFrom>2015-07-12T21:59:59.005Z</StartTimeFrom>
        <StartTimeTo>2015-08-10T21:59:59.005Z</StartTimeTo>
        <Pagination>
            <EntriesPerPage>2</EntriesPerPage>
        </Pagination>
        :return: getItem response
        """
        response = self.execute('GetSellerList', {
            'GranularityLevel': 'Fine',
            'StartTimeFrom': '2015-07-12T21:59:59.005Z',
            'StartTimeTo': '2015-08-10T21:59:59.005Z',
            'Pagination': {'EntriesPerPage': '2'}
        })
        # get only some items, need to get all (paging over start and )
        # return response
        return EbayGetItemResponse.create_from_data(data=response)

        # ask for offset and limit(number)
