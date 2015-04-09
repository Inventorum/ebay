# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields


class EbayShippingService(object):
    def __init__(self, id, cost, additional_cost=None):
        self.id = id
        self.cost = cost
        self.additional_cost = additional_cost


class EbayFixedPriceItem(object):
    def __init__(self, title, description, listing_duration, country, postal_code, quantity, start_price,
                 paypal_email_address, payment_methods, category_id, shipping_services):
        if not all([isinstance(s, EbayShippingService) for s in shipping_services]):
            raise TypeError("shipping_services must be list of EbayShippingService instances")

        self.title = title
        self.description = description
        self.listing_duration = listing_duration
        self.country = country
        self.postal_code = postal_code
        self.quantity = quantity
        self.start_price = start_price
        self.paypal_email_address = paypal_email_address
        self.payment_methods = payment_methods
        self.category_id = category_id
        self.shipping_services = shipping_services

    def dict(self):
        data = {
            'Title': self.title,
            'Description': self.description,
            'ListingDuration': self.listing_duration,
            'Country': self.country,
            'PostalCode': self.postal_code,
            'Quantity': self.quantity,
            'StartPrice': self.start_price,
            'PayPalEmailAddress': self.paypal_email_address,
            'PaymentMethods': self.payment_methods,
            'PrimaryCategory': {'CategoryID': self.category_id},
        }

        # Static data
        data.update(**self._static_data)

        # Shipping
        shipping = [self._build_shipping_details(s) for s in self.shipping_services]
        data['ShippingDetails'] = shipping

        return {'Item': data}

    def _build_shipping_details(self, shipping):
        """
        :type shipping: inventorum.ebay.apps.products.models.EbayItemShippingDetails
        """
        return {
            'ShippingServiceOptions': {
                'ShippingServicePriority': 1,
                'ShippingServiceAdditionalCost': shipping.additional_cost or 0,
                'ShippingServiceCost': shipping.cost,
                'ShippingService': shipping.id,
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


class EbayAddItemResponse(object):
    def __init__(self, item_id, start_time, end_time):
        self.item_id = item_id
        self.start_time = start_time
        self.end_time = end_time

    @classmethod
    def create_from_data(cls, data):
        serializer = EbayAddItemResponseDeserializer(data=data)
        return serializer.build()


class EbayAddItemResponseDeserializer(POPOSerializer):
    ItemID = fields.CharField(source='item_id')
    StartTime = fields.DateTimeField(source='start_time')
    EndTime = fields.DateTimeField(source='end_time')

    class Meta:
        model = EbayAddItemResponse