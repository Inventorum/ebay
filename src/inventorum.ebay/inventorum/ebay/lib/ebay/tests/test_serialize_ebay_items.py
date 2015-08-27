import logging
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase
import datetime

log = logging.getLogger(__name__)


class TestForGetDataFromEbay(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("full_test_for_serialize_get_item_ids_from_ebay.yaml")
    def test_get_item_ids_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_item_ids()

        log.debug(response)
        log.debug(datetime.datetime.now())

        self.assertEqual(response.items[0].item_id, '261967105601')
        self.assertEqual(response.items[18].item_id, '262005246355')

    @EbayTest.use_cassette("full_test_for_serialize_get_item_from_ebay.yaml")
    def test_get_item_from_ebay(self):
        items = EbayItems(self.ebay_token)
        id_1 = '261967105601'
        item1 = items.get_item(id_1)
        log.debug(item1)
        self.assertEqual(item1.item_id, id_1)
        self.assertEqual(item1.sku, 'invrc_677218')
        self.assertEqual(item1.country, 'DE')
        self.assertEqual(item1.shipping_details.shipping_service_options[0].shipping_service, 'DE_UPSStandard')

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
