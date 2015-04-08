# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django_countries import countries

class GenericEbayProductDataBuilder(object):
    def __init__(self, item):
        """
        :type item: inventorum.ebay.apps.products.models.EbayItemModel
        """
        self.item = item

    def build(self):
        raise NotImplemented


class TradingEbayProductDataBuilder(GenericEbayProductDataBuilder):
    def build(self):
        data = {
            'Title': self.item.name,
            'Description': self.item.description,
            'Country': unicode(self.item.country),
            'PostalCode': self.item.postal_code,
            'Quantity': self.item.quantity,
            'StartPrice': self.item.gross_price,
            'PrimaryCategory': {'CategoryID': self.item.category.external_id},
        }
        data.update(**self._static_data)
        shipping = [self._build_shipping_details(s) for s in self.item.shipping.all()]
        data['ShippingDetails'] = shipping
        return {'Item': data}

    def _build_shipping_details(self, shipping):
        """
        :type shipping: inventorum.ebay.apps.products.models.EbayItemShippingDetails
        """
        return {
            'ShippingServiceOptions': {
                'ShippingServicePriority': 1,
                'ShippingServiceAdditionalCost': shipping.additional_cost,
                'ShippingServiceCost': shipping.cost,
                'ShippingService': shipping.external_id,
            }
        }
    @property
    def _static_data(self):
        return {
            'Currency': 'EUR',
            'ListingType': 'FixedPriceItem',
            'ReturnPolicy': {
                'ReturnsAcceptedOption': u'ReturnsAccepted',
                'Description': u''
            },
            'DispatchTimeMax': 3,
            'ConditionID': 1000
        }






# {'Item': {
#     'Description': u'nek 0,28, 47514, Venceremos, A5 Notenheft Lin. 14, BUND, 100% Recyclingpapier, ean 4015290475144',
#     'Title': u'Notenheft A5 quer Lin 14',
#     'Country': u'Germany',
#     'Currency': u'EUR',
#     'PostalCode': u'10119',
#     'ListingType': u'FixedPriceItem',
#     'ReturnPolicy': {
#         'ReturnsAcceptedOption': u'ReturnsAccepted', 'Description': u''
#     }, 'PictureDetails': None}}
#     'DispatchTimeMax': 3,
#     'ConditionID': 1000,
#     'Quantity': 20,
#     'StartPrice': Decimal('4.74810'),
#     'PrimaryCategory': {'CategoryID': u'6699'},
#     'ShippingDetails': [
#         {'ShippingServiceOptions': {
#             'ShippingServicePriority': 1,
#             'ShippingServiceAdditionalCost': 0.0,
#             'ShippingService': u'First service',
#             'ShippingServiceCost': 2.0}}],

#     'ListingDuration': u'Days_30',
#     'PaymentMethods': [u'PayPal'],
#     'PayPalEmailAddress': None,



