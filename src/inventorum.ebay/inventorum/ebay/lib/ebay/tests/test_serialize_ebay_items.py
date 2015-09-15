from __future__ import absolute_import, unicode_literals
import logging
from decimal import Decimal
from inventorum.ebay.lib.ebay.data.items import EbayGetItemResponse, EbayFixedPriceItem

from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestGetDataFromEbay(EbayAuthenticatedAPITestCase):
    @EbayTest.use_cassette("full_test_for_serialize_get_item_ids_from_ebay.yaml")
    def test_get_item_ids_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_all_items_from_seller_list(1)  # just 1 entry per page, to test pagination as well

        self.assertEqual(response.items[0].item_id, '261967105601')
        self.assertEqual(response.items[18].item_id, '262005246355')

    @EbayTest.use_cassette("full_test_for_serialize_get_item_from_ebay.yaml")
    def test_get_item_from_ebay(self):
        items = EbayItems(self.ebay_token)
        id_1 = '261967105601'
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
        self.assertEqual(item1.paypal_email_address, 'bartosz@hernas.pl')
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
        response = {'Ack': 'Success', 'Timestamp': '2015-09-15T08:54:48.431Z', 'Version': '933', 'Build': 'E933_INTL_API_17625661_R1', 'Item': {'SKU': 'invproduction_2311685', 'PayPalEmailAddress': 'mail@jmalcher.de', 'ShipToLocations': 'DE', 'ReservePrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'Title': 'Kassenschublade', 'ProxyItem': 'false', 'HitCounter': 'NoHitCounter', 'Seller': {'Status': 'Confirmed', 'FeedbackScore': '1', 'IDVerified': 'false', 'eBayGoodStanding': 'true', 'UserID': 'newmade', 'Site': 'Germany', 'AboutMePage': 'false', 'FeedbackRatingStar': 'None', 'VATStatus': 'VATExempt', 'UserIDChanged': 'false', 'FeedbackPrivate': 'false', 'PositiveFeedbackPercent': '66.7', 'SellerInfo': {'CheckoutEnabled': 'true', 'StoreOwner': 'false', 'AllowPaymentEdit': 'true', 'SellerBusinessType': 'Commercial', 'SafePaymentExempt': 'false', 'LiveAuctionAuthorized': 'false', 'MerchandizingPref': 'OptIn', 'CIPBankAccountStored': 'true', 'QualifiesForB2BVAT': 'false', 'GoodStanding': 'true'}, 'NewUser': 'false', 'MotorsDealer': 'false', 'Email': 'tech+ebay@inventorum.com', 'RegistrationDate': '2015-03-31T08:57:26.000Z'}, 'ListingType': 'FixedPriceItem', 'Location': 'Berlin', 'SellerProfiles': {'SellerPaymentProfile': {'PaymentProfileID': '77179000023', 'PaymentProfileName': 'PayPal#8'}, 'SellerReturnProfile': {'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte', 'ReturnProfileID': '70043489023'}, 'SellerShippingProfile': {'ShippingProfileID': '71752373023', 'ShippingProfileName': u'Pauschal:DHL P\xe4ckchen(EUR 5,00),3 Werktage'}}, 'ReturnPolicy': {'ShippingCostPaidByOption': 'Buyer', 'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren', 'ReturnsWithinOption': 'Days_14', 'ReturnsWithin': '14 Tage', 'ReturnsAcceptedOption': 'ReturnsAccepted', 'ReturnsAccepted': u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.'}, 'BusinessSellerDetails': {'LegalInvoice': 'false', 'Email': 'tech+ebay@inventorum.com', 'Address': {'FirstName': 'John', 'Street1': 'Inventorum GmbH', 'Street2': 'Voltastr 5', 'CityName': 'Berlin', 'CountryName': 'Deutschland', 'Phone': '0172|4694679', 'LastName': 'Newman', 'PostalCode': '13355', 'StateOrProvince': 'default'}}, 'ListingDuration': 'Days_30', 'PictureDetails': {'GalleryType': 'Gallery', 'PhotoDisplay': 'PicturePack', 'PictureURL': 'http://i.ebayimg.com/00/s/NTAwWDUwMA==/z/mqQAAOSwLqFV9vfQ/$_1.JPG?set_id=8800005007', 'ExternalPictureURL': 'http://app.inventorum.com/uploads/img-hash/e4ba/dad9/38e1/5cec/82cf/79b8/b8ed/e4badad938e15cec82cf79b8b8ed1d7a_ipad_retina.JPEG', 'GalleryURL': 'http://i.ebayimg.com/00/s/NTAwWDUwMA==/z/mqQAAOSwLqFV9vfQ/$_1.JPG?set_id=8800005007'}, 'BuyerProtection': 'ItemIneligible', 'ItemID': '262048903191', 'StartPrice': {'_currencyID': 'EUR', 'value': '117.81'}, 'eBayPlusEligible': 'false', 'ReviseStatus': {'ItemRevised': 'false'}, 'PrimaryCategory': {'CategoryID': '118828', 'CategoryName': 'Business & Industrie:Ladenausstattung & -werbung:Ladenkassen & Scanner:Kassenladen'}, 'GetItFast': 'false', 'ShippingServiceCostOverrideList': {'ShippingServiceCostOverride': {'ShippingServicePriority': '1', 'ShippingServiceType': 'Domestic', 'ShippingServiceAdditionalCost': {'_currencyID': 'EUR', 'value': '0.0'}, 'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '59.0'}}}, 'Country': 'DE', 'HideFromSearch': 'false', 'ConditionID': '1000', 'ListingDetails': {'CheckoutEnabled': 'true', 'HasReservePrice': 'false', 'HasPublicMessages': 'false', 'ConvertedReservePrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'ConvertedStartPrice': {'_currencyID': 'EUR', 'value': '117.81'}, 'ConvertedBuyItNowPrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'ViewItemURLForNaturalSearch': 'http://www.ebay.de/itm/Kassenschublade-/262048903191', 'Adult': 'false', 'StartTime': '2015-09-14T16:36:01.000Z', 'ViewItemURL': 'http://www.ebay.de/itm/Kassenschublade-/262048903191', 'EndTime': '2015-10-14T16:36:01.000Z', 'BindingAuction': 'false', 'HasUnansweredQuestions': 'false'}, 'PaymentMethods': 'PayPal', 'SellingStatus': {'ReserveMet': 'true', 'ConvertedCurrentPrice': {'_currencyID': 'EUR', 'value': '117.81'}, 'QuantitySold': '0', 'LeadCount': '0', 'CurrentPrice': {'_currencyID': 'EUR', 'value': '117.81'}, 'SecondChanceEligible': 'false', 'BidIncrement': {'_currencyID': 'EUR', 'value': '0.0'}, 'BidCount': '0', 'ListingStatus': 'Active', 'MinimumToBid': {'_currencyID': 'EUR', 'value': '117.81'}, 'QuantitySoldByPickupInStore': '0'}, 'AutoPay': 'false', 'OutOfStockControl': 'true', 'ShippingPackageDetails': {'ShippingIrregular': 'false', 'ShippingPackage': 'None', 'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'}, 'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'}}, 'PostalCode': '13355', 'Quantity': '15', 'eBayPlus': 'false', 'TimeLeft': 'P29DT7H41M13S', 'BuyItNowPrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'DispatchTimeMax': '3', 'GiftIcon': '0', 'PostCheckoutExperienceEnabled': 'false', 'Site': 'Germany', 'BuyerGuaranteePrice': {'_currencyID': 'EUR', 'value': '20000.0'}, 'Currency': 'EUR', 'HitCount': '0', 'ConditionDisplayName': 'Neu', 'PrivateListing': 'false', 'LocationDefaulted': 'true', 'ShippingDetails': {'InsuranceFee': {'_currencyID': 'EUR', 'value': '0.0'}, 'InternationalShippingDiscountProfileID': '0', 'ShippingServiceOptions': {'ShippingTimeMax': '2', 'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '59.0'}, 'ShippingServicePriority': '1', 'ShippingServiceAdditionalCost': {'_currencyID': 'EUR', 'value': '0.0'}, 'ShippingService': 'DE_DHLPackchen', 'ExpeditedService': 'false', 'ShippingTimeMin': '1'}, 'InsuranceDetails': {'InsuranceOption': 'NotOffered'}, 'InsuranceOption': 'NotOffered', 'ShippingDiscountProfileID': '0', 'CalculatedShippingRate': {'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'}, 'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'}}, 'SellerExcludeShipToLocationsPreference': 'true', 'ShippingType': 'Flat', 'SalesTax': {'SalesTaxPercent': '0.0', 'ShippingIncludedInTax': 'false'}, 'ApplyShippingDiscount': 'false', 'ThirdPartyCheckout': 'false'}}}
        item = EbayGetItemResponse.create_from_data(data=response)

        self.assertIsInstance(item, EbayFixedPriceItem)
