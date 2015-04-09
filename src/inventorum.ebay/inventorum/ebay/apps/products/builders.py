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
        payment_methods = list(self.item.payment_methods.all().values_list('external_id', flat=True))
        data = {
            'Title': self.item.name,
            'Description': self.item.description,
            'ListingDuration': self.item.listing_duration,
            'Country': unicode(self.item.country),
            'PostalCode': self.item.postal_code,
            'Quantity': self.item.quantity,
            'StartPrice': self.item.gross_price,
            'PayPalEmailAddress': self.item.paypal_email_address,
            'PaymentMethods': payment_methods,
            'PrimaryCategory': {'CategoryID': self.item.category.external_id},
        }

        # Static data
        data.update(**self._static_data)

        # Shipping
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
