# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import datetime

from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.ebay.data.items import EbayAddItemResponse, EbayUnpublishReasons, EbayEndItemResponse, \
    EbayReviseFixedPriceItemResponse, EbayGetItemResponse, EbayGetSellerListResponse


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

    def get_items_from_seller_list(self, page_nr, entries_per_page):
        """
        Get List of ItemIds from the Items, published on ebay.
        <GranularityLevel>Fine</GranularityLevel>
        <StartTimeFrom>2015-07-12T21:59:59.005Z</StartTimeFrom>
        <StartTimeTo>2015-08-14T17:16:59.005Z</StartTimeTo>
        <Pagination>
            <EntriesPerPage>2</EntriesPerPage>
        </Pagination>
        :type page_nr int
        :type entries_per_page int with maximal 200
        :rtype: EbayGetSellerListResponse
        :return: EbayGetSellerListResponse
        """
        response = self.execute('GetSellerList', {
            'DetailLevel': 'ReturnAll',
            'EndTimeFrom': EbayParser.format_date(datetime.datetime.now()),
            # 120 days is ebay max for date range filters
            'EndTimeTo': EbayParser.format_date(datetime.datetime.now() + datetime.timedelta(days=120)),
            'IncludeVariations': 'True',
            'Pagination': {
                'EntriesPerPage': entries_per_page,
                'PageNumber': page_nr}
        })
        return EbayGetSellerListResponse.create_from_data(data=response)

    def get_all_items_from_seller_list(self, entries_per_page):
        """
        Get List of all ItemIds from the Items, published on ebay.
        :rtype [EbayFixedPrizedItem]
        :return: getItem response
        """
        page_nr = 1
        response = self.get_items_from_seller_list(page_nr, entries_per_page)
        while response.page_number > page_nr:
            page_nr += 1
            next_response = self.get_items_from_seller_list(page_nr, entries_per_page)
            for item in next_response.items:
                response.items.append(item)

        return response

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
