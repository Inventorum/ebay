# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import fields


class EbayVariation(object):
    def __init__(self, gross_price, quantity, specifics):
        self.gross_price = gross_price
        self.quantity = quantity
        self.specifics = specifics

    def dict(self):
        return {
            'Quantity': self.quantity,
            'StartPrice': self.gross_price,
            'VariationSpecifics': {
                'NameValueList': [s.dict() for s in self.specifics]
            }
        }

class EbayItemSpecific(object):
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def dict(self):
        data = {
            'Name': self.name,
        }
        if len(self.values) == 1:
            data['Value'] = self.values[0]
        elif len(self.values) > 1:
            data['Value'] = self.values
        return data

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
                 paypal_email_address, payment_methods, category_id, shipping_services, pictures=None,
                 item_specifics=None, variations=None):

        if not all([isinstance(s, EbayShippingService) for s in shipping_services]):
            raise TypeError("shipping_services must be list of EbayShippingService instances")

        if item_specifics and not all([isinstance(s, EbayItemSpecific) for s in item_specifics]):
            raise TypeError("item_specifics must be list of EbayShippingService instances")

        if variations and not all([isinstance(v, EbayVariation) for v in variations]):
            raise TypeError("variations must be list of EbayVariation instances")

        self.title = title
        self.description = description
        self.listing_duration = listing_duration
        self.country = country
        self.postal_code = postal_code
        self.quantity = int(quantity)
        self.start_price = start_price
        self.paypal_email_address = paypal_email_address
        self.payment_methods = payment_methods
        self.category_id = category_id
        self.shipping_services = shipping_services
        self.pictures = pictures or []
        self.item_specifics = item_specifics or []
        self.variations = variations or []

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

        if self.item_specifics:
            data['ItemSpecifics'] = {
                'NameValueList': [s.dict() for s in self.item_specifics]
            }

        if self.variations:
            data['Variations'] = {
                'Variation': [v.dict() for v in self.variations]
            }

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