# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields


class EbayPicture(object):
    def __init__(self, url):
        if url.startswith('https'):
            raise TypeError('Ebay does not accept url with https for pictures')

        self.url = url

    def dict(self):
        return {
            'PictureURL': self.url
        }


class EbayShippingService(object):
    def __init__(self, id, cost, additional_cost=None):
        self.id = id
        self.cost = cost
        self.additional_cost = additional_cost

    def dict(self):
        return {
            'ShippingServiceOptions': {
                'ShippingServicePriority': 1,
                'ShippingServiceAdditionalCost': self.additional_cost or 0,
                'ShippingServiceCost': self.cost,
                'ShippingService': self.id,
            }
        }


class EbayFixedPriceItem(object):
    def __init__(self, title, description, listing_duration, country, postal_code, quantity, start_price,
                 paypal_email_address, payment_methods, category_id, shipping_services, pictures=None):
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
        self.pictures = pictures or []

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
        if self.pictures:
            data['PictureDetails'] = [p.dict() for p in self.pictures]
        if self.shipping_services:
            data['ShippingDetails'] = [s.dict() for s in self.shipping_services]

        # Static data
        data.update(**self._static_data)

        return {'Item': data}

    @property
    def _static_data(self):
        return {
            'Currency': 'EUR',
            'ListingType': 'FixedPriceItem',
            'ReturnPolicy': {
                'ReturnsAcceptedOption': 'ReturnsAccepted',
                'Description': ''
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


class EbayUnpublishReasons(object):
    NOT_AVAILABLE = 'NotAvailable'
    INCORRECT = 'Incorrect'
    LOST_OR_BROKEN = 'LostOrBroken'
    OTHER_ERROR = 'OtherListingError'


class EbayEndItemResponse(object):
    def __init__(self, end_time):
        self.end_time = end_time

    @classmethod
    def create_from_data(cls, data):
        serializer = EbayEndItemResponseDeserializer(data=data)
        return serializer.build()


class EbayEndItemResponseDeserializer(POPOSerializer):
    EndTime = fields.DateTimeField(source='end_time')

    class Meta:
        model = EbayEndItemResponse