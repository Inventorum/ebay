# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from collections import defaultdict

from BeautifulSoup import CData
from inventorum.ebay.lib.ebay.data import EbayParser, EbayArrayField, EbayListSerializer
from inventorum.ebay.lib.ebay.data.responses import PaginationResultType
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from inventorum.ebay.lib.utils import int_or_none
from rest_framework import fields
from rest_framework.fields import ListField, CharField, IntegerField


class EbayPriceModel(object):
    def __init__(self, currency_id, value):
        self.currencyID = currency_id
        self.value = value


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
    def __init__(self, shipping_id, cost, additional_cost=None):
        self.shipping_id = shipping_id
        self.cost = cost
        self.additional_cost = additional_cost

    def dict(self):
        return {'ShippingServicePriority': 1,
                'ShippingServiceAdditionalCost': EbayParser.encode_price(self.additional_cost or 0),
                'ShippingServiceCost': EbayParser.encode_price(self.cost),
                'ShippingService': self.shipping_id}


class EbayFixedPriceItem(object):
    def __init__(self, title, description, listing_duration, country, postal_code, quantity, start_price,
                 paypal_email_address, payment_methods, pictures, category_id=None, sku=None, shipping_services=(),
                 item_specifics=None, variations=None, ean=None, is_click_and_collect=False, shipping_details=None,
                 pick_up=None, variation=None, item_id=None, primary_category=None):
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
        :type category_id: unicode | None
        :type shipping_services: list[EbayShippingService]
        :type pictures: list[EbayPicture]
        :type item_specifics: list[EbayItemSpecific] | None
        :type variations: list[EbayVariation] | None
        :type sku: unicode | None
        :type ean: unicode | None
        :type is_click_and_collect: bool

        :type shipping_details: EbayShippingDetails | None
        :type pick_up: EbayPickupInStoreDetails | None
        :type variation: EbayVariations | None
        :type item_id: unicode | None
        :type primary_category: Category | None
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
        self.shipping_details = shipping_details
        self.pick_up = pick_up
        self.variation = variation
        self.item_id = item_id
        self.primary_category = primary_category

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
            #  If a variation has any purchases (i.e., an order line item was created and QuantitySold is greater
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


class EbayGetSellerListResponse(object):
    def __init__(self, items, pagination_result, page_number):
        self.items = items
        self.pagination_result = pagination_result
        self.page_number = page_number

    @classmethod
    def create_from_data(cls, data):
        """
        :rtype: EbayPaymentSerializer
        """
        if data['Ack'] != 'Success':
            return None

        serializer = EbayGetSellerListResponseDeserializer(data=data)
        return serializer.build()


class EbayItemID(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        ItemID = fields.CharField(source='item_id')

    #################################################

    def __init__(self, item_id):
        self.item_id = item_id


EbayItemID.Serializer.Meta.model = EbayItemID


class EbayGetSellerListResponseDeserializer(POPOSerializer):
    ItemArray = EbayArrayField(source='items', item_key='Item', item_deserializer=EbayItemID.Serializer,
                               allow_null=True)
    PaginationResult = PaginationResultType.Deserializer(source="pagination_result")
    PageNumber = IntegerField(source="page_number")

    class Meta:
        model = EbayGetSellerListResponse


class EbayReviseFixedPriceItemResponseDeserializer(POPOSerializer):
    ItemID = fields.CharField(source='item_id')


class EbayShippingServiceOption(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        ShippingService = fields.CharField(source='shipping_service')

    #################################################

    def __init__(self, shipping_service):
        self.shipping_service = shipping_service


EbayShippingServiceOption.Serializer.Meta.model = EbayShippingServiceOption


class EbayShippingDetails(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        ShippingServiceOptions = EbayShippingServiceOption.Serializer(many=True, source='shipping_service_options')

    #################################################

    def __init__(self, shipping_service_options):
        self.shipping_service_options = shipping_service_options


EbayShippingDetails.Serializer.Meta.model = EbayShippingDetails


class EbayPickupInStoreDetails(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        EligibleForPickupInStore = fields.BooleanField(source='is_click_and_collect')

    #################################################

    def __init__(self, is_click_and_collect):
        self.is_click_and_collect = is_click_and_collect


EbayPickupInStoreDetails.Serializer.Meta.model = EbayPickupInStoreDetails


class EbayVariationList(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        Name = fields.CharField(source='name')
        Value = fields.CharField(source='value')

    #################################################

    def __init__(self, name, value):
        self.name = name
        self.value = value


EbayVariationList.Serializer.Meta.model = EbayVariationList


class EbayVariationSpecifics(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        NameValueList = EbayVariationList.Serializer(many=True, source='name_value_list')

    #################################################

    def __init__(self, name_value_list):
        self.name_value_list = name_value_list


EbayVariationSpecifics.Serializer.Meta.model = EbayVariationSpecifics


class EbayItemPictureSerializer(POPOSerializer):
    class Meta:
        model = EbayPicture

    def to_internal_value(self, data):
        return {'urls': data.get('PictureURL', [])}

    def create(self, validated_data):
        return map(self.Meta.model, validated_data['urls'])


class EbayAmountSerializer(POPOSerializer):
    _currencyID = fields.CharField(source='currency_id', max_length=3)
    value = fields.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        model = EbayPriceModel


class EbayItemVariation(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        SKU = fields.CharField(source='sku')
        StartPrice = EbayAmountSerializer(source='start_price')
        Quantity = fields.IntegerField(source='quantity')

    #################################################

    def __init__(self, start_price, quantity, sku=None):
        self.start_price = start_price
        self.sku = sku
        self.quantity = quantity


EbayItemVariation.Serializer.Meta.model = EbayItemVariation


class EbayVariationPictureSet(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        PictureURL = fields.CharField(source='picture_url')
        VariationSpecificValue = fields.CharField(source='variation_specific_value')

    #################################################

    def __init__(self, variation_specific_value, picture_url=None):
        self.picture_url = picture_url
        self.variation_specific_value = variation_specific_value


EbayVariationPictureSet.Serializer.Meta.model = EbayVariationPictureSet


class EbayVariationPicture(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        VariationSpecificName = fields.CharField(source='name')
        VariationSpecificPictureSet = EbayVariationPictureSet.Serializer(many=True, source='values')

    #################################################

    def __init__(self, name, values):
        self.name = name
        self.values = values


EbayVariationPicture.Serializer.Meta.model = EbayVariationPicture


class VariationSpecificSetValue(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        Name = fields.CharField(source='name')
        Value = fields.ListField(source='values')

    #################################################

    def __init__(self, name, values):
        self.name = name
        self.values = values


VariationSpecificSetValue.Serializer.Meta.model = VariationSpecificSetValue


class EbayItemVariationSpecificSet(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        NameValueList = VariationSpecificSetValue.Serializer(many=True, source='values')

    #################################################

    def __init__(self, values):
        self.values = values


EbayItemVariationSpecificSet.Serializer.Meta.model = EbayItemVariationSpecificSet


class EbayVariations(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None
            list_serializer_class = EbayListSerializer

        Pictures = EbayVariationPicture.Serializer(many=True, source='pictures', required=False)
        Variation = EbayItemVariation.Serializer(many=True, source='variation')
        VariationSpecificsSet = EbayItemVariationSpecificSet.Serializer(many=True, source='variation_specifics_set')

    #################################################

    def __init__(self, variation, variation_specifics_set, pictures=None):
        self.pictures = pictures
        self.variations = variation
        self.variation_specifics_set = variation_specifics_set


EbayVariations.Serializer.Meta.model = EbayVariations


class EbayItemSpecificationsSerializer(POPOSerializer):
    ItemSpecific = fields.CharField(source='name')
    Value = ListField(child=CharField(), source="values")

    class Meta:
        model = EbayItemSpecific
        list_serializer_class = EbayListSerializer


class PrimaryCategory(object):
    #################################################

    class Serializer(POPOSerializer):
        class Meta(POPOSerializer.Meta):
            model = None

        CategoryID = fields.CharField(source='category_id', required=False)
        CategoryName = fields.CharField(source='category_name', required=False)

    #################################################

    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name


PrimaryCategory.Serializer.Meta.model = PrimaryCategory


class EbayItemSerializer(POPOSerializer):
    Title = fields.CharField(source='title')
    Description = fields.CharField(source='description', default='')
    ListingDuration = fields.CharField(source='listing_duration')
    Country = fields.CharField(source='country')
    PostalCode = fields.CharField(source='postal_code')
    Quantity = fields.IntegerField(source='quantity')
    StartPrice = EbayAmountSerializer(source='start_price')
    PayPalEmailAddress = fields.EmailField(source='paypal_email_address')
    PaymentMethods = fields.CharField(source='payment_methods')
    PrimaryCategory = PrimaryCategory.Serializer(source='primary_category')
    ShippingDetails = EbayShippingDetails.Serializer(source='shipping_details')
    PictureDetails = EbayItemPictureSerializer(source='pictures')
    ItemSpecifics = EbayItemSpecificationsSerializer(source='item_specifics', many=True, required=False)
    Variations = EbayVariations.Serializer(source='variation', many=True, required=False)
    SKU = fields.CharField(source='sku', default='')
    EAN = fields.CharField(source='ean', required=False)
    PickupInStoreDetails = EbayPickupInStoreDetails.Serializer(source='pick_up', required=False)
    ItemID = fields.CharField(source='item_id')

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
        if data['Ack'] != 'Success':
            return None

        serializer = EbayItemSerializer(data=data['Item'])
        return serializer.build()
