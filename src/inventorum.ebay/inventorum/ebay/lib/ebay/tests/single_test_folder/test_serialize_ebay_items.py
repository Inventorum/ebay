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

    def test_get_item_from_ebay(self):
        items = EbayItems(self.ebay_token)
        id_1 = '261967105601'
        item1 = items.get_items(id_1)
        log.debug(item1)
        self.assertEqual(item1.sku, 'invrc_677218')

        id_2 = '262005246355'
        item2 = items.get_items(id_2)
        self.assertEqual(item2.sku, 'invproduction_2811435')
        self.assertEqual(item2.variation[0].pictures[0].values[0].picture_url,
                         'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/E8QAAOSwPcVV0acl/$_1.JPG?set_id=880000500F')


# {'Ack': 'Success', 'Timestamp': '2015-08-17T15:33:50.806Z', 'Version': '933', 'Build': 'E933_INTL_API_17625661_R1',
#  'Item': {'SKU': 'invproduction_2811435', 'PayPalEmailAddress': 'mail@jmaicher.de', 'ShipToLocations': 'DE',
#           'ReservePrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'Title': 'Inventorum Test T-Shirt',
#           'ProxyItem': 'false', 'HitCounter': 'NoHitCounter',
#           'Seller': {'Status': 'Confirmed', 'FeedbackScore': '1', 'IDVerified': 'false', 'eBayGoodStanding': 'true',
#                      'UserID': 'newmade', 'Site': 'Germany', 'AboutMePage': 'false', 'FeedbackRatingStar': 'None',
#                      'VATStatus': 'VATExempt', 'UserIDChanged': 'false', 'FeedbackPrivate': 'false',
#                      'PositiveFeedbackPercent': '66.7',
#                      'SellerInfo': {'CheckoutEnabled': 'true', 'StoreOwner': 'false', 'AllowPaymentEdit': 'true',
#                                     'SellerBusinessType': 'Commercial', 'SafePaymentExempt': 'false',
#                                     'LiveAuctionAuthorized': 'false', 'MerchandizingPref': 'OptIn',
#                                     'CIPBankAccountStored': 'true', 'QualifiesForB2BVAT': 'false',
#                                     'GoodStanding': 'true'}, 'NewUser': 'false', 'MotorsDealer': 'false',
#                      'Email': 'tech+ebay@inventorum.com', 'RegistrationDate': '2015-03-31T08:57:26.000Z'},
#           'Location': 'Berlin', 'SellerProfiles': {'SellerPaymentProfile': {'PaymentProfileID': '75393265023',
#                                                                             'PaymentProfileName': u'PayPal:\xdcberweisung in der Kaufabwicklung akze#0'},
#                                                    'SellerReturnProfile': {
#                                                        'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte',
#                                                        'ReturnProfileID': '70043489023'},
#                                                    'SellerShippingProfile': {'ShippingProfileID': '73296117023',
#                                                                              'ShippingProfileName': 'Pauschal:Deutsche Post(Kostenlos),3 Werktage'}},
#           'ReturnPolicy': {'ShippingCostPaidByOption': 'Buyer',
#                            'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren',
#                            'ReturnsWithinOption': 'Days_14', 'ReturnsWithin': '14 Tage',
#                            'ReturnsAcceptedOption': 'ReturnsAccepted',
#                            'ReturnsAccepted': u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.'},
#           'BusinessSellerDetails': {'LegalInvoice': 'false',
#                                     'Address': {'FirstName': 'John', 'Street1': 'Voltastr 5', 'CityName': 'Berlin',
#                                                 'CountryName': 'Deutschland', 'LastName': 'Newman',
#                                                 'PostalCode': '13355'}}, 'ListingDuration': 'Days_30',
#           'PictureDetails': {'GalleryType': 'Gallery', 'PhotoDisplay': 'None', 'PictureURL': [
#               'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/S3YAAOSw9N1Vzgml/$_1.JPG?set_id=880000500F',
#               'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/NZcAAOSwu4BV0Zvz/$_1.JPG?set_id=880000500F'],
#                              'GalleryURL': 'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/S3YAAOSw9N1Vzgml/$_1.JPG?set_id=880000500F'},
#           'BuyerProtection': 'ItemEligible', 'ItemID': '262005246355',
#           'StartPrice': {'_currencyID': 'EUR', 'value': '1.0'}, 'eBayPlusEligible': 'false',
#           'ReviseStatus': {'ItemRevised': 'true'},
#           'PrimaryCategory': {'CategoryID': '15687', 'CategoryName': 'Kleidung & Accessoires:Herrenmode:T-Shirts'},
#           'GetItFast': 'false', 'ListingType': 'FixedPriceItem', 'Country': 'DE', 'HideFromSearch': 'false',
#           'ConditionID': '1000',
#           'Variations':
#               {'Pictures':
#                   {'VariationSpecificPictureSet': [
#                     {'PictureURL': 'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/E8QAAOSwPcVV0acl/$_1.JPG?set_id=880000500F',
#                         'VariationSpecificValue': 'Green'},
#                     {'PictureURL': 'http://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/PjQAAOSwu4BV0ZxG/$_1.JPG?set_id=880000500F',
#                         'VariationSpecificValue': 'Blue'}],
#                   'VariationSpecificName': 'Farbe (*)'},
#               'Variation': [
#                     {'SKU': 'invproduction_2811436',
#                     'VariationSpecifics': {
#                         'NameValueList': [{'Name': 'Farbe (*)', 'Value': 'Green'},{'Name': u'Gr\xf6\xdfe (*)', 'Value': 'M'}]},
#                     'StartPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                     'SellingStatus': {'QuantitySold': '0', 'QuantitySoldByPickupInStore': '0'},
#                     'VariationProductListingDetails': None,
#                     'Quantity': '3'},
#                     {'SKU': 'invproduction_2811437',
#                      'VariationSpecifics': {'NameValueList': [
#                           {'Name': 'Farbe (*)', 'Value': 'Blue'}, {'Name': u'Gr\xf6\xdfe (*)', 'Value': 'S'}]},
#                       'StartPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                       'SellingStatus': {'QuantitySold': '0', 'QuantitySoldByPickupInStore': '0'},
#                       'VariationProductListingDetails': None,
#                       'Quantity': '1'}],
#                 'VariationSpecificsSet': {
#                      'NameValueList': [{'Name': 'Farbe (*)', 'Value': ['Blue', 'Green']}, {'Name': u'Gr\xf6\xdfe (*)', 'Value': ['S', 'M']}]}},
#
#
#
#
#           'PaymentMethods': ['PayPal', 'MoneyXferAcceptedInCheckout'],
#           'SellingStatus': {'ReserveMet': 'true', 'ConvertedCurrentPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                             'QuantitySold': '0', 'LeadCount': '0',
#                             'CurrentPrice': {'_currencyID': 'EUR', 'value': '1.0'}, 'SecondChanceEligible': 'false',
#                             'BidIncrement': {'_currencyID': 'EUR', 'value': '0.0'}, 'BidCount': '0',
#                             'ListingStatus': 'Active', 'MinimumToBid': {'_currencyID': 'EUR', 'value': '1.0'},
#                             'QuantitySoldByPickupInStore': '0'}, 'AutoPay': 'false',
#           'ShippingPackageDetails': {'ShippingIrregular': 'false', 'ShippingPackage': 'PackageThickEnvelope',
#                                      'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'},
#                                      'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'}},
#           'PostalCode': '13355', 'Quantity': '4', 'eBayPlus': 'false', 'TimeLeft': 'P26DT23H25M50S',
#           'BuyItNowPrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'DispatchTimeMax': '3',
#           'ListingDetails': {'CheckoutEnabled': 'true', 'HasReservePrice': 'false', 'HasPublicMessages': 'false',
#                              'ConvertedReservePrice': {'_currencyID': 'EUR', 'value': '0.0'},
#                              'ConvertedStartPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                              'ConvertedBuyItNowPrice': {'_currencyID': 'EUR', 'value': '0.0'},
#                              'ViewItemURLForNaturalSearch': 'http://www.ebay.de/itm/Inventorum-Test-T-Shirt-/262005246355',
#                              'Adult': 'false', 'StartTime': '2015-08-14T14:59:40.000Z',
#                              'ViewItemURL': 'http://www.ebay.de/itm/Inventorum-Test-T-Shirt-/262005246355',
#                              'EndTime': '2015-09-13T14:59:40.000Z', 'BindingAuction': 'false',
#                              'HasUnansweredQuestions': 'false'}, 'GiftIcon': '0',
#           'PostCheckoutExperienceEnabled': 'false', 'Site': 'Germany',
#           'BuyerGuaranteePrice': {'_currencyID': 'EUR', 'value': '20000.0'}, 'Currency': 'EUR', 'HitCount': '9',
#           'ConditionDisplayName': 'Neu mit Etikett', 'PrivateListing': 'false', 'LocationDefaulted': 'true',
#           'ShippingDetails': {'InsuranceFee': {'_currencyID': 'EUR', 'value': '0.0'},
#                               'InternationalShippingDiscountProfileID': '0',
#                               'ShippingServiceOptions': {'ShippingTimeMax': '2',
#                                                          'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '0.0'},
#                                                          'ShippingServicePriority': '1',
#                                                          'ShippingServiceAdditionalCost': {'_currencyID': 'EUR',
#                                                                                            'value': '0.0'},
#                                                          'ShippingService': 'DE_DeutschePostBrief',
#                                                          'FreeShipping': 'true', 'ExpeditedService': 'false',
#                                                          'ShippingTimeMin': '1'},
#                               'InsuranceDetails': {'InsuranceOption': 'NotOffered'}, 'InsuranceOption': 'NotOffered',
#                               'ShippingDiscountProfileID': '0', 'CalculatedShippingRate': {
#                   'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'},
#                   'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'}},
#                               'SellerExcludeShipToLocationsPreference': 'true', 'ShippingType': 'Flat',
#                               'SalesTax': {'SalesTaxPercent': '0.0', 'ShippingIncludedInTax': 'false'},
#                               'ApplyShippingDiscount': 'false', 'ThirdPartyCheckout': 'false'}}}
