import logging
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestForSerializeEbayItems(EbayAuthenticatedAPITestCase):

    def test_response_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_items()
        log.debug(response)
        # self.assertEqual(item, )




    # def build_mocked_ebay_response(self):
    #     <?xml version="1.0" encoding="UTF-8"?>
    #         <GetMyeBaySellingResponse xmlns="urn:ebay:apis:eBLBaseComponents">
    #         <Timestamp>2015-08-07T09:20:01.711Z</Timestamp>
    #         <Ack>Success</Ack>
    #         <Version>933</Version>
    #         <Build>E933_INTL_APISELLING_17621711_R1</Build>
    #         <ActiveList>
    #             <ItemArray>
    #                 <Item>
    #                     <BuyItNowPrice currencyID="EUR">1.0</BuyItNowPrice>
    #                     <ItemID>261993711957</ItemID>
    #                     <ListingDetails>
    #                         <StartTime>2015-08-05T16:49:31.000Z</StartTime>
    #                         <ViewItemURL>http://www.ebay.de/itm/Felt-Brougham-/261993711957</ViewItemURL>
    #                         <ViewItemURLForNaturalSearch>http://cgi.ebay.de/Felt-Brougham?item=261993711957&amp;category=22416&amp;cmd=ViewItem</ViewItemURLForNaturalSearch>
    #                     </ListingDetails>
    #                     <ListingDuration>Days_30</ListingDuration>
    #                     <ListingType>FixedPriceItem</ListingType>
    #                     <Quantity>111</Quantity>
    #                     <SellingStatus>
    #                         <CurrentPrice currencyID="EUR">1.0</CurrentPrice>
    #                     </SellingStatus>
    #                     <ShippingDetails>
    #                         <ShippingServiceOptions>
    #                             <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
    #                         </ShippingServiceOptions>
    #                         <ShippingType>Flat</ShippingType>
    #                     </ShippingDetails>
    #                     <TimeLeft>P28DT7H29M30S</TimeLeft>
    #                     <Title>Felt Brougham</Title>
    #                     <WatchCount>1</WatchCount>
    #                     <QuantityAvailable>111</QuantityAvailable>
    #                     <SKU>invproduction_12345678</SKU>
    #                     <PictureDetails>
    #                         <GalleryURL>http://thumbs.ebaystatic.com/pict/2619937119576464.jpg</GalleryURL>
    #                     </PictureDetails>
    #                     <ClassifiedAdPayPerLeadFee currencyID="EUR">0.0</ClassifiedAdPayPerLeadFee>
    #                     <SellerProfiles>
    #                         <SellerShippingProfile>
    #                             <ShippingProfileID>75183898023</ShippingProfileID>
    #                             <ShippingProfileName>Pauschal:DHL Express Wo(Kostenlos),3 Werktage</ShippingProfileName>
    #                         </SellerShippingProfile>
    #                         <SellerReturnProfile>
    #                             <ReturnProfileID>70043489023</ReturnProfileID>
    #                             <ReturnProfileName>Verbraucher haben das Recht, den Artikel unte</ReturnProfileName>
    #                         </SellerReturnProfile>
    #                         <SellerPaymentProfile>
    #                             <PaymentProfileID>72901342023</PaymentProfileID>
    #                             <PaymentProfileName>PayPal#6</PaymentProfileName>
    #                         </SellerPaymentProfile>
    #                     </SellerProfiles>
    #                 </Item>
    #             </ItemArray>
    #             <PaginationResult>
    #                 <TotalNumberOfPages>1</TotalNumberOfPages>
    #                 <TotalNumberOfEntries>1</TotalNumberOfEntries>
    #             </PaginationResult>
    #         </ActiveList>
    #     </GetMyeBaySellingResponse>

