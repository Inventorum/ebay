import logging
from inventorum.ebay.lib.ebay.items import EbayItems
from inventorum.ebay.tests import EbayTest
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase

log = logging.getLogger(__name__)


class TestForSerializeEbayItems(EbayAuthenticatedAPITestCase):

    @EbayTest.use_cassette("full_test_for_serialize_get_items_from_ebay.yaml")
    def test_response_from_ebay(self):
        items = EbayItems(self.ebay_token)
        response = items.get_items()

        log.debug(response)
        self.assertEqual(response.items[0].sku, 'invrc_677218')
        self.assertEqual(response.items[0].paypal_email_address, 'bartosz@hernas.pl')

        self.assertEqual(response.items[0].pictures[0].url,
                         'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F')

        self.assertEqual(response.items[0].shipping_details.shipping_service_options[0].shipping_service,
                         "DE_UPSStandard")

# {'Ack': 'Success',
# 'Timestamp': '2015-08-13T12:11:16.452Z',
# 'ItemsPerPage': '2',
# 'ItemArray': {'Item': [
#     {'SKU': 'invrc_677218',
#   'PayPalEmailAddress': 'bartosz@hernas.pl',
#   'ShipToLocations': 'DE',
#      'ReservePrice': {'_currencyID': 'EUR', 'value': '0.0'},
#       'Title': 'Aaa', 'ProxyItem': 'false',
#      'HitCounter': 'NoHitCounter',
#       'ListingType': 'FixedPriceItem',
#       'Location': 'Berlin',
#       'SellerProfiles': {
#         'SellerPaymentProfile': {'PaymentProfileID': '70836070023',
#                                  'PaymentProfileName': 'PayPal:Sofortige Bezahlung'},
#         'SellerReturnProfile': {'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte',
#                                 'ReturnProfileID': '70043489023'},
#         'SellerShippingProfile': {'ShippingProfileID': '71813223023',
#                                   'ShippingProfileName': 'Pauschal:UPS Standard(EUR 3,00),Deutsche Post'}},
#       'ReturnPolicy': {'ShippingCostPaidByOption': 'Buyer',
#                       'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren',
#                       'ReturnsWithinOption': 'Days_14', 'ReturnsWithin': '14 Tage',
#                       'ReturnsAcceptedOption': 'ReturnsAccepted',
#                       'ReturnsAccepted': u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.'},
#       'PickupInStoreDetails': {'EligibleForPickupInStore': 'true'}, 'ListingDuration': 'Days_30',
#       'PictureDetails': {'GalleryType': 'Gallery', 'PhotoDisplay': 'PicturePack', 'PictureURL': [
#          'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F',
#          'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/hXYAAOSwDNdVpN-B/$_1.JPG?set_id=880000500F',
#          'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/uqQAAOSwgQ9VpN-B/$_1.JPG?set_id=880000500F',
#          'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/DqIAAOSwu4BVpN-S/$_1.JPG?set_id=880000500F',
#          'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/xjoAAOSwT6pVpN-C/$_1.JPG?set_id=880000500F',
#          'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/tHkAAOSwPcVVpN-C/$_1.JPG?set_id=880000500F'],
#       'GalleryURL': 'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F'},
#       'BuyerProtection': 'ItemEligible',
#       'ItemID': '261967105601',
#       'StartPrice': {'_currencyID': 'EUR', 'value': '1.09'},
#       'eBayPlusEligible': 'false',
#       'ReviseStatus': {'ItemRevised': 'false'},
#       'PrimaryCategory': {'CategoryID': '50602',
#       'CategoryName': 'TV, Video & Audio:Haushaltsbatterien & Strom:Einweg-Batterien'},
#       'GetItFast': 'false',
#       'ShippingServiceCostOverrideList': {'ShippingServiceCostOverride': [
#         {'ShippingServicePriority': '1', 'ShippingServiceType': 'Domestic',
#          'ShippingServiceAdditionalCost': {'_currencyID': 'EUR', 'value': '0.0'},
#          'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '3.0'}},
#         {'ShippingServicePriority': '2', 'ShippingServiceType': 'Domestic',
#          'ShippingServiceAdditionalCost': {'_currencyID': 'EUR', 'value': '0.0'},
#          'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '1.5'}},
#         {'ShippingServicePriority': '3', 'ShippingServiceType': 'Domestic',
#          'ShippingServiceAdditionalCost': {'_currencyID': 'EUR', 'value': '0.0'},
#          'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '2.0'}}]}, 'Country': 'DE', 'HideFromSearch': 'false',
#      'ConditionID': '1000',
#      'ListingDetails': {'CheckoutEnabled': 'true', 'HasReservePrice': 'false', 'HasPublicMessages': 'false',
#                         'ConvertedReservePrice': {'_currencyID': 'EUR', 'value': '0.0'},
#                         'ConvertedStartPrice': {'_currencyID': 'EUR', 'value': '1.09'},
#                         'ConvertedBuyItNowPrice': {'_currencyID': 'USD', 'value': '0.0'},
#                         'ViewItemURLForNaturalSearch': 'http://www.ebay.de/itm/Aaa-/261967105601', 'Adult': 'false',
#                         'StartTime': '2015-07-14T10:07:48.000Z', 'EndingReason': 'NotAvailable',
#                         'ViewItemURL': 'http://www.ebay.de/itm/Aaa-/261967105601',
#                         'EndTime': '2015-07-14T12:49:28.000Z', 'BindingAuction': 'false',
#                         'HasUnansweredQuestions': 'false'}, 'PaymentMethods': 'PayPal',
#      'SellingStatus': {'ReserveMet': 'true', 'ConvertedCurrentPrice': {'_currencyID': 'EUR', 'value': '1.09'},
#                        'QuantitySold': '0', 'CurrentPrice': {'_currencyID': 'EUR', 'value': '1.09'},
#                        'SecondChanceEligible': 'false', 'BidIncrement': {'_currencyID': 'EUR', 'value': '0.0'},
#                        'BidCount': '0', 'ListingStatus': 'Completed',
#                        'MinimumToBid': {'_currencyID': 'EUR', 'value': '1.09'}}, 'AutoPay': 'true',
#      'ShippingPackageDetails': {'ShippingIrregular': 'false', 'ShippingPackage': 'None',
#                                 'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'},
#                                 'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'}},
#      'PostalCode': '13347', 'Quantity': '0', 'eBayPlus': 'false', 'TimeLeft': 'PT0S',
#      'BuyItNowPrice': {'_currencyID': 'USD', 'value': '0.0'}, 'DispatchTimeMax': '3', 'GiftIcon': '0',
#      'PostCheckoutExperienceEnabled': 'false', 'Site': 'Germany',
#      'BuyerGuaranteePrice': {'_currencyID': 'EUR', 'value': '20000.0'}, 'Currency': 'EUR',
#      'ConditionDisplayName': 'Neu', 'PrivateListing': 'false', 'LocationDefaulted': 'true',
#      'ShippingDetails': {'InsuranceFee': {'_currencyID': 'EUR', 'value': '0.0'},
#                          'InternationalShippingDiscountProfileID': '0', 'ShippingServiceOptions': [
#              {'ShippingTimeMax': '2', 'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '3.0'},
#               'ShippingServicePriority': '1', 'ShippingService': 'DE_UPSStandard', 'ExpeditedService': 'false',
#               'ShippingTimeMin': '1'},
#              {'ShippingTimeMax': '2', 'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '1.5'},
#               'ShippingServicePriority': '2', 'ShippingService': 'DE_DeutschePostBrief', 'ExpeditedService': 'false',
#               'ShippingTimeMin': '1'},
#              {'ShippingTimeMax': '3', 'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '2.0'},
#               'ShippingServicePriority': '3',
#               'ShippingService': 'DE_DHLExpressWorldwide',
#               'ExpeditedService': 'false',
#               'ShippingTimeMin': '1'}],
#       'InsuranceDetails': {'InsuranceOption': 'NotOffered'},
#       'InsuranceOption': 'NotOffered', 'ShippingDiscountProfileID': '0', 'CalculatedShippingRate': {
#              'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'},
#              'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'}},
#                          'SellerExcludeShipToLocationsPreference': 'true', 'ShippingType': 'Flat',
#                          'SalesTax': {'SalesTaxPercent': '0.0', 'ShippingIncludedInTax': 'false'},
#                          'ApplyShippingDiscount': 'false', 'ThirdPartyCheckout': 'false'}},
#     {'SKU': 'invproduction_12345678', 'PayPalEmailAddress': 'mail@jmaicher.de', 'ShipToLocations': 'DE',
#      'ReservePrice': {'_currencyID': 'EUR', 'value': '0.0'}, 'Title': 'Felt Brougham', 'ProxyItem': 'false',
#      'HitCounter': 'NoHitCounter', 'Location': 'Berlin',
#      'SellerProfiles': {'SellerPaymentProfile': {'PaymentProfileID': '72901342023', 'PaymentProfileName': 'PayPal#6'},
#                         'SellerReturnProfile': {'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte',
#                                                 'ReturnProfileID': '70043489023'},
#                         'SellerShippingProfile': {'ShippingProfileID': '75183898023',
#                                                   'ShippingProfileName': 'Pauschal:DHL Express Wo(Kostenlos),3 Werktage'}},
#      'ReturnPolicy': {'ShippingCostPaidByOption': 'Buyer',
#                       'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren',
#                       'ReturnsWithinOption': 'Days_14', 'ReturnsWithin': '14 Tage',
#                       'ReturnsAcceptedOption': 'ReturnsAccepted',
#                       'ReturnsAccepted': u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.'},
#      'ListingDuration': 'Days_30', 'PictureDetails': {'GalleryType': 'Gallery', 'PhotoDisplay': 'PicturePack',
#                                                       'PictureURL': 'http://app.intern.inventorum.com/uploads/2992/product/7a/6c/69/a3/43/c5/97/8c/d0/3e/d2/5e/96/99/46/7a6c69a343c5978cd03ed25e969946bd.ipad_retina.png',
#                                                       'GalleryURL': 'http://app.intern.inventorum.com/uploads/2992/product/7a/6c/69/a3/43/c5/97/8c/d0/3e/d2/5e/96/99/46/7a6c69a343c5978cd03ed25e969946bd.ipad_retina.png'},
#      'BuyerProtection': 'ItemIneligible', 'ItemID': '261993711957',
#      'StartPrice': {'_currencyID': 'EUR', 'value': '1.0'}, 'eBayPlusEligible': 'false',
#      'ReviseStatus': {'ItemRevised': 'true'},
#      'PrimaryCategory': {'CategoryID': '22416', 'CategoryName': 'Sport:Weitere Wintersportarten:Sonstige'},
#      'GetItFast': 'false', 'ListingType': 'FixedPriceItem', 'Country': 'DE', 'HideFromSearch': 'false',
#      'ConditionID': '1000',
#      'ListingDetails': {'CheckoutEnabled': 'true', 'HasReservePrice': 'false', 'HasPublicMessages': 'false',
#                         'ConvertedReservePrice': {'_currencyID': 'EUR', 'value': '0.0'},
#                         'ConvertedStartPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                         'ConvertedBuyItNowPrice': {'_currencyID': 'USD', 'value': '0.0'},
#                         'ViewItemURLForNaturalSearch': 'http://www.ebay.de/itm/Felt-Brougham-/261993711957',
#                         'Adult': 'false', 'StartTime': '2015-08-05T16:49:31.000Z', 'EndingReason': 'NotAvailable',
#                         'ViewItemURL': 'http://www.ebay.de/itm/Felt-Brougham-/261993711957',
#                         'EndTime': '2015-08-10T12:38:05.000Z', 'BindingAuction': 'false',
#                         'HasUnansweredQuestions': 'false'}, 'PaymentMethods': 'PayPal',
#      'SellingStatus': {'ReserveMet': 'true', 'ConvertedCurrentPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                        'QuantitySold': '0', 'CurrentPrice': {'_currencyID': 'EUR', 'value': '1.0'},
#                        'SecondChanceEligible': 'false', 'BidIncrement': {'_currencyID': 'EUR', 'value': '0.0'},
#                        'BidCount': '0', 'ListingStatus': 'Completed',
#                        'MinimumToBid': {'_currencyID': 'EUR', 'value': '1.0'}}, 'AutoPay': 'false',
#      'ShippingPackageDetails': {'ShippingIrregular': 'false', 'ShippingPackage': 'None',
#                                 'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'},
#                                 'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'}},
#      'PostalCode': '13355', 'Quantity': '111', 'eBayPlus': 'false', 'TimeLeft': 'PT0S',
#      'BuyItNowPrice': {'_currencyID': 'USD', 'value': '0.0'}, 'DispatchTimeMax': '3', 'GiftIcon': '0',
#      'PostCheckoutExperienceEnabled': 'false', 'Site': 'Germany',
#      'BuyerGuaranteePrice': {'_currencyID': 'EUR', 'value': '20000.0'}, 'Currency': 'EUR',
#      'ConditionDisplayName': 'Neu', 'PrivateListing': 'false', 'LocationDefaulted': 'true',
#      'ShippingDetails': {'InsuranceFee': {'_currencyID': 'EUR', 'value': '0.0'},
#                          'InternationalShippingDiscountProfileID': '0',
#                          'ShippingServiceOptions': {'ShippingTimeMax': '3',
#                                                     'ShippingServiceCost': {'_currencyID': 'EUR', 'value': '0.0'},
#                                                     'ShippingServicePriority': '1',
#                                                     'ShippingServiceAdditionalCost': {'_currencyID': 'EUR',
#                                                                                       'value': '0.0'},
#                                                     'ShippingService': 'DE_DHLExpressWorldwide',
#                                                     'ExpeditedService': 'false', 'ShippingTimeMin': '1'},
#                          'InsuranceDetails': {'InsuranceOption': 'NotOffered'}, 'InsuranceOption': 'NotOffered',
#                          'ShippingDiscountProfileID': '0', 'CalculatedShippingRate': {
#              'WeightMinor': {'_unit': 'gm', '_measurementSystem': 'Metric', 'value': '0'},
#              'WeightMajor': {'_unit': 'kg', '_measurementSystem': 'Metric', 'value': '0'}},
#                          'SellerExcludeShipToLocationsPreference': 'true', 'ShippingType': 'Flat',
#                          'SalesTax': {'SalesTaxPercent': '0.0', 'ShippingIncludedInTax': 'false'},
#                          'ApplyShippingDiscount': 'false', 'ThirdPartyCheckout': 'false'}}]},
#  'Seller': {'Status': 'Confirmed', 'FeedbackScore': '1', 'IDVerified': 'false', 'eBayGoodStanding': 'true',
#             'UserID': 'newmade', 'Site': 'Germany', 'AboutMePage': 'false', 'FeedbackRatingStar': 'None',
#             'VATStatus': 'VATExempt', 'UserIDChanged': 'false', 'FeedbackPrivate': 'false',
#             'PositiveFeedbackPercent': '66.7',
#             'SellerInfo': {'CheckoutEnabled': 'true', 'StoreOwner': 'false', 'AllowPaymentEdit': 'true',
#                            'SafePaymentExempt': 'false', 'LiveAuctionAuthorized': 'false', 'MerchandizingPref': 'OptIn',
#                            'CIPBankAccountStored': 'true', 'QualifiesForB2BVAT': 'false', 'GoodStanding': 'true'},
#             'NewUser': 'false', 'MotorsDealer': 'false', 'RegistrationDate': '2015-03-31T08:57:26.000Z'},
#  'ReturnedItemCountActual': '2', 'Version': '933', 'PageNumber': '1', 'Build': 'E933_INTL_APISELLING_17621711_R1',
#  'PaginationResult': {'TotalNumberOfPages': '7', 'TotalNumberOfEntries': '13'}, 'HasMoreItems': 'true'}



#########################################
# {'Ack': 'Success',
# 'Timestamp': '2015-08-11T08:30:14.429Z',
# 'ItemsPerPage': '100',
# 'ItemArray':
#   {'Item':
#       [
#       {'SKU': 'invrc_677218',
#       'PayPalEmailAddress': 'bartosz@hernas.pl',
#       'ShipToLocations': 'DE',
#       'ReservePrice':
#           {'_currencyID': 'EUR',
#           'value': '0.0'
#           },
#       'Title': 'Aaa',
#       'ProxyItem': 'false',
#       'HitCounter': 'NoHitCounter',
#       'ListingType': 'FixedPriceItem',
#       'Location': 'Berlin',
#       'SellerProfiles':
#           {'SellerPaymentProfile':
#               {'PaymentProfileID': '70836070023',
#               'PaymentProfileName': 'PayPal:Sofortige Bezahlung'
#               },
#           'SellerReturnProfile':
#               {'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte',
#               'ReturnProfileID': '70043489023'
#               },
#           'SellerShippingProfile':
#               {'ShippingProfileID': '71813223023',
#               'ShippingProfileName': 'Pauschal:UPS Standard(EUR 3,00),Deutsche Post'
#               }
#            },
#       'ReturnPolicy':
#           {'ShippingCostPaidByOption': 'Buyer',
#           'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren',
#           'ReturnsWithinOption': 'Days_14',
#           'ReturnsWithin': '14 Tage',
#           'ReturnsAcceptedOption': 'ReturnsAccepted',
#           'ReturnsAccepted':
#               u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.
#           '},
#       'PickupInStoreDetails':
#           {'EligibleForPickupInStore': 'true'
#           },
#       'ListingDuration': 'Days_30',
#       'PictureDetails':
#          {'GalleryType': 'Gallery',
#            'PhotoDisplay': 'PicturePack',
#               'PictureURL': [
#                   'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F',
#                   'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/hXYAAOSwDNdVpN-B/$_1.JPG?set_id=880000500F',
#                   'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/uqQAAOSwgQ9VpN-B/$_1.JPG?set_id=880000500F',
#                   'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/DqIAAOSwu4BVpN-S/$_1.JPG?set_id=880000500F',
#                   'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/xjoAAOSwT6pVpN-C/$_1.JPG?set_id=880000500F',
#                   'http://i.ebayimg.com/00/s/MTMzNFg3NTA=/z/tHkAAOSwPcVVpN-C/$_1.JPG?set_id=880000500F'
#               ],
#               'GalleryURL': 'http://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/usoAAOSwgQ9VpN-D/$_1.JPG?set_id=880000500F'
#               },
#           'BuyerProtection': 'ItemEligible',
#           'ItemID': '261967105601',
#           'StartPrice':
#               {'_currencyID': 'EUR',
#               'value': '1.09'
#               },
#           'eBayPlusEligible': 'false',
#           'ReviseStatus':
#               {'ItemRevised': 'false'},
#           'PrimaryCategory':
#               {'CategoryID': '50602',
#               'CategoryName': 'TV, Video & Audio:Haushaltsbatterien & Strom:Einweg-Batterien'},
#           'GetItFast': 'false',
#           'ShippingServiceCostOverrideList':
#               {'ShippingServiceCostOverride':
#                   [
#                   {'ShippingServicePriority': '1',
#                       'ShippingServiceType': 'Domestic',
#                       'ShippingServiceAdditionalCost':
#                           {'_currencyID': 'EUR',
#                           'value': '0.0'},
#                       'ShippingServiceCost':
#                           {'_currencyID': 'EUR',
#                           'value': '3.0'}
#                   },
#                   {'ShippingServicePriority': '2',
#                       'ShippingServiceType': 'Domestic',
#                       'ShippingServiceAdditionalCost':
#                           {'_currencyID': 'EUR',
#                           'value': '0.0'},
#                       'ShippingServiceCost':
#                           {'_currencyID': 'EUR',
#                           'value': '1.5'}
#                   },
#                   {'ShippingServicePriority': '3',
#                       'ShippingServiceType': 'Domestic',
#                       'ShippingServiceAdditionalCost':
#                           {'_currencyID': 'EUR',
#                           'value': '0.0'},
#                       'ShippingServiceCost':
#                           {'_currencyID': 'EUR',
#                           'value': '2.0'}
#                   }
#                   ]
#               },
#           'Country': 'DE',
#           'HideFromSearch': 'false',
#           'ConditionID': '1000',
#           'ListingDetails':
#               {'CheckoutEnabled': 'true',
#               'HasReservePrice': 'false',
#               'HasPublicMessages': 'false',
#               'ConvertedReservePrice':
#                   {'_currencyID': 'EUR',
#                   'value': '0.0'},
#               'ConvertedStartPrice':
#                   {'_currencyID': 'EUR',
#                   'value': '1.09'},
#               'ConvertedBuyItNowPrice':
#                   {'_currencyID': 'USD',
#                   'value': '0.0'},
#               'ViewItemURLForNaturalSearch': 'http://www.ebay.de/itm/Aaa-/261967105601',
#               'Adult': 'false',
#               'StartTime': '2015-07-14T10:07:48.000Z',
#               'EndingReason': 'NotAvailable',
#               'ViewItemURL': 'http://www.ebay.de/itm/Aaa-/261967105601',
#               'EndTime': '2015-07-14T12:49:28.000Z',
#               'BindingAuction': 'false',
#               'HasUnansweredQuestions': 'false'},
#           'PaymentMethods': 'PayPal',
#           'SellingStatus':
#               {'ReserveMet': 'true',
#               'ConvertedCurrentPrice':
#                   {'_currencyID': 'EUR',
#                   'value': '1.09'},
#               'QuantitySold': '0',
#               'CurrentPrice':
#                   {'_currencyID': 'EUR',
#                   'value': '1.09'},
#               'SecondChanceEligible': 'false',
#               'BidIncrement':
#                   {'_currencyID': 'EUR',
#                   'value': '0.0'},
#               'BidCount': '0',
#               'ListingStatus': 'Completed',
#               'MinimumToBid':
#                   {'_currencyID': 'EUR',
#                   'value': '1.09'}
#               },
#           'AutoPay': 'true',
#           'ShippingPackageDetails':
#               {'ShippingIrregular': 'false',
#               'ShippingPackage': 'None',
#               'WeightMajor':
#                   {'_unit': 'kg',
#                   '_measurementSystem': 'Metric',
#                   'value': '0'},
#               'WeightMinor':
#                   {'_unit': 'gm',
#                   '_measurementSystem': 'Metric',
#                   'value': '0'}
#               },
#           'PostalCode': '13347',
#           'Quantity': '0',
#           'eBayPlus': 'false',
#           'TimeLeft': 'PT0S',
#           'BuyItNowPrice':
#               {'_currencyID': 'USD',
#               'value': '0.0'},
#           'DispatchTimeMax': '3',
#           'GiftIcon': '0',
#           'PostCheckoutExperienceEnabled': 'false',
#           'Site': 'Germany',
#           'BuyerGuaranteePrice':
#               {'_currencyID': 'EUR',
#               'value': '20000.0'},
#           'Currency': 'EUR',
#           'ConditionDisplayName': 'Neu',
#           'PrivateListing': 'false',
#           'LocationDefaulted': 'true',
#           'ShippingDetails':
#               {'InsuranceFee':
#                   {'_currencyID': 'EUR',
#                   'value': '0.0'},
#               'InternationalShippingDiscountProfileID': '0',
#               'ShippingServiceOptions':
#                   [
#                   {'ShippingTimeMax': '2',
#                   'ShippingServiceCost':
#                       {'_currencyID': 'EUR',
#                       'value': '3.0'},
#                   'ShippingServicePriority': '1',
#                   'ShippingService': 'DE_UPSStandard',
#                   'ExpeditedService': 'false',
#                   'ShippingTimeMin': '1'},
#                   {'ShippingTimeMax': '2',
#                   'ShippingServiceCost':
#                       {'_currencyID': 'EUR',
#                       'value': '1.5'},
#                   'ShippingServicePriority': '2',
#                   'ShippingService': 'DE_DeutschePostBrief',
#                   'ExpeditedService': 'false',
#                   'ShippingTimeMin': '1'},
#                   {'ShippingTimeMax': '3',
#                   'ShippingServiceCost':
#                       {'_currencyID': 'EUR',
#                       'value': '2.0'},
#                   'ShippingServicePriority': '3',
#                   'ShippingService': 'DE_DHLExpressWorldwide',
#                   'ExpeditedService': 'false',
#                   'ShippingTimeMin': '1'
#                   }
#                   ],
#               'InsuranceDetails':
#                   {'InsuranceOption': 'NotOffered'},
#                   'InsuranceOption': 'NotOffered',
#                   'ShippingDiscountProfileID': '0',
#                   'CalculatedShippingRate':
#                       {'WeightMinor':
#                           {'_unit': 'gm',
#                           '_measurementSystem': 'Metric',
#                           'value': '0'},
#                       'WeightMajor':
#                           {'_unit': 'kg',
#                           '_measurementSystem': 'Metric',
#                           'value': '0'}
#                       },
#                   'SellerExcludeShipToLocationsPreference': 'true',
#                   'ShippingType': 'Flat',
#                   'SalesTax':
#                       {'SalesTaxPercent': '0.0',
#                       'ShippingIncludedInTax': 'false'},
#                   'ApplyShippingDiscount': 'false',
#                   'ThirdPartyCheckout': 'false'
#                   }
#               },
#######next product######
#       {'SKU': 'invproduction_12345678',
#        'PayPalEmailAddress': 'mail@jmaicher.de',
#        'ShipToLocations': 'DE',
#        'ReservePrice':
#           {'_currencyID': 'EUR',
#               'value': '0.0'},
#           'Title': 'Felt Brougham',
#           'ProxyItem': 'false',
#           'HitCounter': 'NoHitCounter',
#           'Location': 'Berlin',
#           'SellerProfiles':
#               {'SellerPaymentProfile':
#                   {'PaymentProfileID': '72901342023',
#                   'PaymentProfileName': 'PayPal#6'},
#               'SellerReturnProfile':
#                   {'ReturnProfileName': 'Verbraucher haben das Recht, den Artikel unte',
#                    'ReturnProfileID': '70043489023'},
#               'SellerShippingProfile':
#                   {'ShippingProfileID': '75183898023',
#                   'ShippingProfileName': 'Pauschal:DHL Express Wo(Kostenlos),3 Werktage'}
#               },
#           'ReturnPolicy':
#               {'ShippingCostPaidByOption': 'Buyer',
#               'ShippingCostPaidBy': u'K\xe4ufer tr\xe4gt die unmittelbaren Kosten der R\xfccksendung der Waren',
#               'ReturnsWithinOption': 'Days_14',
#               'ReturnsWithin': '14 Tage',
#               'ReturnsAcceptedOption': 'ReturnsAccepted',
#               'ReturnsAccepted':
#                   u'Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zur\xfcckzugeben.'},
#           'ListingDuration': 'Days_30',
#           'PictureDetails':
#               {'GalleryType': 'Gallery',
#               'PhotoDisplay': 'PicturePack',
#               'PictureURL': 'http://app.intern.inventorum.com/uploads/2992/product/7a/6c/69/a3/
#                       43/c5/97/8c/d0/3e/d2/5e/96/99/46/7a6c69a343c5978cd03ed25e969946bd.ipad_retina.png',
#               'GalleryURL': 'http://app.intern.inventorum.com/uploads/2992/product/7a/6c/69/a3/43/c5/97/8c/d0/3e/
#                   d2/5e/96/99/46/7a6c69a343c5978cd03ed25e969946bd.ipad_retina.png'},
#               'BuyerProtection': 'ItemIneligible',
#               'ItemID': '261993711957',
#               'StartPrice':
#                   {'_currencyID': 'EUR',
#                   'value': '1.0'},
#               'eBayPlusEligible': 'false',
#               'ReviseStatus':
#                   {'ItemRevised': 'true'},
#               'PrimaryCategory':
#                   {'CategoryID': '22416',
#                   'CategoryName': 'Sport:Weitere Wintersportarten:Sonstige'},
#               'GetItFast': 'false',
#               'ListingType': 'FixedPriceItem',
#               'Country': 'DE',
#               'HideFromSearch': 'false',
#               'ConditionID': '1000',
#               'ListingDetails':
#                   {'CheckoutEnabled': 'true',
#                   'HasReservePrice': 'false',
#                   'HasPublicMessages': 'false',
#                   'ConvertedReservePrice':
#                       {'_currencyID': 'EUR',
#                       'value': '0.0'},
#                   'ConvertedStartPrice':
#                       {'_currencyID': 'EUR',
#                       'value': '1.0'},
#                   'ConvertedBuyItNowPrice':
# (...)
