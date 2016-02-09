from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal
from inventorum.ebay.lib.ebay.data.items import EbayGetItemResponse, EbayFixedPriceItem

from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.lib.ebay.tests.example_ebay_item_response import EbayResponseItemExample
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestGetDataFromEbay(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("full_test_for_serialize_get_item_ids_from_ebay.yaml")
    def test_get_item_ids_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_all_items_from_seller_list(1)  # just 1 entry per page, to test pagination as well

        self.assertEqual(response.items[0].item_id, '262283040813')
        self.assertEqual(response.items[18].item_id, '262005246355')

    @EbayTest.use_cassette("full_test_for_serialize_get_item_from_ebay.yaml")
    def test_get_item_from_ebay(self):
        items = EbayItems(self.ebay_token)
        id_1 = '262250114732'
        item1 = items.get_item(id_1)
        self.assertEqual(item1.item_id, id_1)
        self.assertEqual(item1.start_price.value, Decimal('1.09'))
        self.assertEqual(item1.title, 'Aaa')
        self.assertEqual(item1.sku, 'invrc_677218')
        self.assertEqual(item1.country, 'DE')
        self.assertEqual(item1.postal_code, '13347')
        self.assertEqual(item1.shipping_details.shipping_service_options[0].shipping_service, 'DE_UPSStandard')
        self.assertEqual(item1.primary_category.category_id, '50602')
        self.assertEqual(item1.listing_duration, 'Days_30')
        self.assertEqual(item1.payment_methods, 'PayPal')
        self.assertEqual(item1.paypal_email_address, 'info@inventorum.com')
        self.assertEqual(item1.pictures[0].url,
                         'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F')
        self.assertTrue(item1.pick_up.is_click_and_collect)
        self.assertIsNone(item1.ean)
        self.assertIsNone(item1.variation)

        # second item with variation
        id_2 = '262005246355'
        item2 = items.get_item(id_2)
        self.assertEqual(item2.item_id, id_2)
        self.assertEqual(item2.sku, 'invproduction_2811435')
        self.assertEqual(item2.country, 'DE')
        self.assertEqual(item2.pictures[0].url,
                         'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/S3YAAOSw9N1Vzgml/$_1.JPG?set_id=880000500F')
        self.assertEqual(item2.variation[0].pictures[0].values[0].picture_url,
                         'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/E8QAAOSwPcVV0acl/$_1.JPG?set_id=880000500F')
        self.assertEqual(item2.variation[0].variations[1].sku, 'invproduction_2811437')
        self.assertEqual(item2.shipping_details.shipping_service_options[0].shipping_service, 'DE_DeutschePostBrief')
        self.assertEqual(item2.primary_category.category_id, '15687')

    @EbayTest.use_cassette("serialize_get_not_expired_items_from_ebay")
    def test_not_get_expired_items_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_all_items_from_seller_list(1)  # with 1 entry per page, it tests pagination as well
        for i in range(len(response.items)):
            cur_item = items.get_item(response.items[i].item_id)
            self.assertEqual(response.items[i].item_id, cur_item.item_id)
        self.assertEqual(i, 5)

    def test_serialize_data_from_ebay(self):
        ebay_response_example = EbayResponseItemExample.response
        item = EbayGetItemResponse.create_from_data(data=ebay_response_example)

        self.assertIsInstance(item, EbayFixedPriceItem)
