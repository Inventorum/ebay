# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict
from BeautifulSoup import CData
from inventorum.ebay.lib.db.fields import MoneyField
from inventorum.ebay.lib.ebay.data import EbayParser
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from inventorum.ebay.lib.utils import int_or_none
from rest_framework import fields
from rest_framework.fields import ListField, CharField, DictField


class EbayPriceModel(object):
    def __init__(self, currencyID, value):
        self.currencyID = currencyID
        self.value = value

    def dict(self):
        return {
            'CurrenceID': self.currencyID,
            'Value': self.value
        }


class EbayVariation(object):
    def __init__(self, sku, gross_price, quantity, specifics, images, ean=None):
        """
        :type sku: unicode
        :type gross_price: decimal.Decimal
        :type quantity: int
        :type specifics: list[EbayItemSpecific]
        :type images: list[EbayPicture]
        :type ean: unicode | None
        """
        self.sku = sku
        self.gross_price = gross_price
        self.quantity = quantity
        self.specifics = specifics
        self.images = images
        self.ean = ean

    def get_specific_values_by_name(self, name):
        for specific in self.specifics:
            if specific.name == name:
                return specific.values
        return None

    def dict(self):
        data = {
            'SKU': self.sku,
            'Quantity': self.quantity,
            'StartPrice': EbayParser.encode_price(self.gross_price),
            'VariationSpecifics': {
                'NameValueList': [s.dict() for s in self.specifics]
            }
        }

        if self.ean:
            data["VariationProductListingDetails"] = {
                "EAN": self.ean
            }

        return data


class EbayItemSpecific(object):
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def dict(self):
        data = {
            'Name': self.name,
        }
        values = list(set(self.values))

        if len(values) == 1:
            data['Value'] = values[0]
        elif len(values) > 1:
            data['Value'] = values
        return data


class EbayPayment(object):
    def __init__(self, method):
        self.method = method

    def dict(self):
        return {
            'PaymentMethod': self.method
        }


class EbayPicture(object):
    def __init__(self, url):
        if url.startswith('https'):
            raise TypeError('Ebay does not accept url with https for pictures')

        self.url = url

    def dict(self):
        return {
            'PictureURL': self.url
        }


class EbayItemShippingService(object):
    def __init__(self, id, cost, additional_cost=None):
        self.id = id
        self.cost = cost
        self.additional_cost = additional_cost

    def dict(self):
        return {'ShippingServicePriority': 1,
                'ShippingServiceAdditionalCost': EbayParser.encode_price(self.additional_cost or 0),
                'ShippingServiceCost': EbayParser.encode_price(self.cost),
                'ShippingService': self.id}


class EbayFixedPriceItem(object):
    def __init__(self, title, description, listing_duration, country, postal_code, quantity, start_price, sku,
                 paypal_email_address, payment_methods, category_id=None, shipping_services=(), pictures=None,
                 item_specifics=None, variations=None, ean=None, is_click_and_collect=False):
        """
        :type title: unicode
        :type description: unicode
        :type listing_duration: unicode
        :type country: unicode
        :type postal_code: unicode
        :type quantity: int
        :type start_price: decimal.Decimal
        :type paypal_email_address: unicode
        :type payment_methods: list[unicode]
        :type category_id: unicode
        :type shipping_services: list[EbayShippingService]
        :type pictures: list[EbayPicture]
        :type item_specifics: list[EbayItemSpecific]
        :type variations: list[EbayVariation]
        :type sku: unicode
        :type ean: unicode | None
        :type is_click_and_collect: bool
        """

        if not all([isinstance(s, EbayItemShippingService) for s in shipping_services]):
            raise TypeError("shipping_services must be list of EbayItemShippingService instances")

        if item_specifics and not all([isinstance(s, EbayItemSpecific) for s in item_specifics]):
            raise TypeError("item_specifics must be list of EbayItemSpecific instances")

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
        self.sku = sku
        self.ean = ean
        self.is_click_and_collect = is_click_and_collect

    def dict(self):
        data = {
            'Title': self.title,
            'SKU': self.sku,
            'Description': str(CData(self.description)),
            'ListingDuration': self.listing_duration,
            'Country': self.country,
            'PostalCode': self.postal_code,
            'PayPalEmailAddress': self.paypal_email_address,
            'PaymentMethods': self.payment_methods,
            'PrimaryCategory': {'CategoryID': self.category_id},
        }
        if self.pictures:
            data['PictureDetails'] = {'PictureURL': [p.url for p in self.pictures]}
        if self.shipping_services:
            data['ShippingDetails'] = {'ShippingServiceOptions': [s.dict() for s in self.shipping_services]}

        if self.item_specifics:
            data['ItemSpecifics'] = {
                'NameValueList': [s.dict() for s in self.item_specifics]
            }

        if self.variations:
            data['Variations'] = {
                'Variation': [v.dict() for v in self.variations],
                'VariationSpecificsSet': self._build_variation_specifics_set(),
                'Pictures': self._build_variation_pictures_set()
            }
        else:
            data['Quantity'] = self.quantity
            data['StartPrice'] = EbayParser.encode_price(self.start_price)

        if self.is_click_and_collect:
            data['PickupInStoreDetails'] = {
                'EligibleForPickupInStore': True
            }
            data['AutoPay'] = True

        if self.ean:
            data['ProductListingDetails'] = {
                'EAN': self.ean
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

    def _build_variation_specifics_set(self):
        specifics = defaultdict(list)
        for variation in self.variations:
            for specific in variation.specifics:
                specifics[specific.name].extend(specific.values)

        specifics_objects = [EbayItemSpecific(key, values) for key, values in specifics.iteritems()]
        return {'NameValueList': [so.dict() for so in specifics_objects]}

    def _build_variation_pictures_set(self):
        first_specific_from_first_variation = self.variations[0].specifics[0]
        main_name = first_specific_from_first_variation.name

        def build_picture_set(value, pictures):
            return {
                'VariationSpecificValue': value,
                'PictureURL': [p.url for p in pictures]
            }

        picture_sets = []
        for variation in self.variations:
            specifics_values = variation.get_specific_values_by_name(main_name)
            picture_sets.extend([build_picture_set(value, variation.images) for value in specifics_values])

        return {
            'VariationSpecificName': main_name,
            'VariationSpecificPictureSet': picture_sets
        }


class EbayAddItemResponse(object):
    def __init__(self, item_id, start_time, end_time, message=None):
        self.item_id = item_id
        self.start_time = start_time
        self.end_time = end_time
        self.message = message

    @classmethod
    def create_from_data(cls, data):
        serializer = EbayAddItemResponseDeserializer(data=data)
        return serializer.build()


class EbayAddItemResponseDeserializer(POPOSerializer):
    ItemID = fields.CharField(source='item_id')
    Message = fields.CharField(source='message', required=False)
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


class EbayReviseFixedPriceVariation(object):
    def __init__(self, original_variation, new_quantity=None, new_start_price=None, is_deleted=False):
        """
        :type original_variation: EbayVariation
        :type new_quantity: int
        :type new_start_price: decimal.Decimal
        :type is_deleted: bool
        """
        self.original_variation = original_variation
        self.new_quantity = new_quantity
        self.new_start_price = new_start_price
        self.is_deleted = is_deleted

    def dict(self):
        original_data = self.original_variation.dict()
        if self.new_quantity:
            original_data['Quantity'] = self.new_quantity
        if self.new_start_price:
            original_data['StartPrice'] = EbayParser.encode_price(self.new_start_price)

        if self.is_deleted:
            #  If a variation has any purchases (i.e., an order line item was created and QuantitySold is greather
            # than 0), you can't delete the variation, but you can set its quantity to zero. If a variation has no
            # purchases, you can delete it.
            original_data['Quantity'] = 0

        return original_data


class EbayReviseFixedPriceItem(object):
    def __init__(self, item_id, quantity=None, start_price=None, variations=None):
        """
        :type variations: list[EbayReviseFixedPriceVariation]
        """
        self.item_id = item_id
        self.quantity = int_or_none(quantity)
        self.start_price = start_price
        self.variations = variations or []

    def dict(self):
        data = {
            'ItemID': self.item_id
        }

        if not self.variations:
            if self.quantity is not None:
                data['Quantity'] = self.quantity

            if self.start_price is not None:
                data['StartPrice'] = EbayParser.encode_price(self.start_price)
        else:
            data['Variations'] = {
                'Variation': [v.dict() for v in self.variations]
            }

        return {'Item': data}


class EbayReviseFixedPriceItemResponse(object):
    @classmethod
    def create_from_data(cls, data):
        """
        :rtype: EbayReviseInventoryStatusResponse
        """
        return EbayReviseFixedPriceItemResponse()


class EbayReviseFixedPriceItemResponseDeserializer(POPOSerializer):
    ItemID = fields.CharField(source='item_id')


class EbayItemShippingSerializer(POPOSerializer):
    ShippingServiceAdditionalCost = fields.DecimalField(source='id', max_digits=5, decimal_places=2)
    ShippingServiceCost = fields.DecimalField(source='cost', max_digits=5, decimal_places=2)

    class Meta:
        model = EbayItemShippingService


class EbayPictureURLField(fields.CharField):
    def to_internal_value(self, data):
        url = super(EbayPictureURLField, self).to_internal_value(data)
        return EbayPicture(url=url)


class EbayItemPictureSerializer(POPOSerializer):
    class Meta:
        model = EbayPicture

    def create(self, validated_data):
        return map(self.Meta.model, validated_data['urls'])

    def to_internal_value(self, data):
        return {'urls': data.get('PictureURL', [])}


class EbayItemSpecificationsSerializer(POPOSerializer):
    ItemSpecific = fields.CharField(source='name')
    Value = ListField(child=CharField(), source="values")

    class Meta:
        model = EbayItemSpecific


class EbayItemVariationSerializer(POPOSerializer):
    SKU = fields.CharField(source='sku')
    StartPrice = fields.DecimalField(source='gross_price', max_digits=4, decimal_places=2)
    # foo = MoneyField()
    Quantity = fields.IntegerField(source='quantity')
    ItemSpecifics = EbayItemSpecificationsSerializer(many=True)
    EbayPictures = EbayItemPictureSerializer(many=True)
    EAN = fields.CharField(source='ean')

    class Meta:
        model = EbayVariation


class EbayStartPriceSerializer(POPOSerializer):
    _currencyID = fields.CharField(source='currencyID', max_length=3)
    value = fields.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        model = EbayPriceModel


class EbayItemSerializer(POPOSerializer):
    Title = fields.CharField(source='title')
    Description = fields.CharField(source='description', default='')  # not existing in response?
    ListingDuration = fields.CharField(source='listing_duration')
    Country = fields.CharField(source='country')
    PostalCode = fields.CharField(source='postal_code')
    Quantity = fields.IntegerField(source='quantity')
    StartPrice = EbayStartPriceSerializer(source='start_price')
    PayPalEmailAddress = fields.EmailField(source='paypal_email_address')
    PaymentMethods = fields.CharField(source='payment_methods')
    CategoryId = fields.CharField(source='category_id', required=False)
    # ShippingDetails = EbayItemShippingSerializer(many=True) todo: write serializer with fields
    PictureDetails = EbayItemPictureSerializer(source='pictures')
    # ItemSpecifics = EbayItemSpecificationsSerializer(many=True, required=False)
    # Variations = EbayItemVariationSerializer(many=True, required=False)
    SKU = fields.CharField(source='sku')
    EAN = fields.CharField(source='ean', required=False)
    # IsClickAndCollect = fields.BooleanField(source='is_click_and_collect', required=False)

    class Meta:
        model = EbayFixedPriceItem


class EbayGetItemResponse(object):
    def __init__(self, items):
        self.items = items

    @classmethod
    def create_from_data(cls, data):
        """
        :rtype: EbayPaymentSerializer
        """
        if not data['Ack'] == 'Success':
            return None

        serializer = EbayGetItemsResponseDeserializer(data=data['ItemArray'])
        return serializer.build()


class EbayGetItemsResponseDeserializer(POPOSerializer):
    Item = EbayItemSerializer(many=True, source='items')

    class Meta:
        model = EbayGetItemResponse










