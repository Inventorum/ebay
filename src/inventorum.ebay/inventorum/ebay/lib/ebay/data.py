# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, IntegerField, BooleanField, DateTimeField


class EbayParser(object):
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    @classmethod
    def parse_date(cls, str_date):
        """
        Parse given ebay date as string to datetime
        :param str_date: Comming from ebay
        :return: Parsed date

        :type str_date: str | unicode
        :rtype: datetime
        """
        return datetime.strptime(str_date, cls.DATE_FORMAT)

    @classmethod
    def parse_bool(cls, str_bool):
        return str_bool == "true"


class EbayUserAddress(object):
    name = None
    street = None
    street1 = None
    city = None
    country = None
    postal_code = None

    def __init__(self, name, street, street1, city, country, postal_code):
        self.name = name
        self.street = street
        self.street1 = street1
        self.city = city
        self.country = country
        self.postal_code = postal_code


class EbayUserAddressSerializer(POPOSerializer):
    Name = CharField(source='name')
    Street = CharField(source='street', default="", required=False, allow_null=True)
    Street1 = CharField(source='street1', default="", required=False, allow_null=True)
    CityName = CharField(source='city')
    Country = CharField(source='country')
    PostalCode = CharField(source='postal_code')

    class Meta:
        model = EbayUserAddress


class EbaySellerInfo(object):
    qualifies_for_b2b_vat = None
    store_owner = None

    def __init__(self, qualifies_for_b2b_vat, store_owner):
        self.qualifies_for_b2b_vat = qualifies_for_b2b_vat
        self.store_owner = store_owner


class EbaySellerInfoSerializer(POPOSerializer):
    QualifiesForB2BVAT = BooleanField(source='qualifies_for_b2b_vat')
    StoreOwner = BooleanField(source='store_owner')

    class Meta:
        model = EbaySellerInfo


class EbayUser(object):
    email = None
    user_id = None
    id_verified = False
    status = False
    registration_address = None
    registration_date = None
    seller_info = None

    def __init__(self, email, user_id, id_verified, status, registration_address, registration_date, seller_info):
        self.email = email
        self.user_id = user_id
        self.id_verified = id_verified
        self.status = status
        self.registration_address = registration_address
        self.registration_date = registration_date
        self.seller_info = seller_info


    @classmethod
    def create_from_data(cls, data):
        serializer = EbayUserSerializer(data=data)
        return serializer.build()


class EbayUserSerializer(POPOSerializer):
    Email = CharField(source='email')
    UserID = CharField(source='user_id')
    IDVerified = BooleanField(source='id_verified')
    Status = CharField(source='status')
    RegistrationAddress = EbayUserAddressSerializer(source='registration_address')
    RegistrationDate = DateTimeField(source='registration_date')
    SellerInfo = EbaySellerInfoSerializer(source='seller_info')

    class Meta:
        model = EbayUser


class EbayToken(object):
    """
    Data object to keeps expiration time and value
    """
    expiration_time = None
    value = None

    def __init__(self, value, expiration_time):
        self.expiration_time = expiration_time
        self.value = value


class EbayCategory(object):
    name = None
    parent_id = 0
    category_id = 0
    level = 0
    b2b_vat_enabled = False
    best_offer_enabled = False
    auto_pay_enabled = False
    leaf = False
    item_lot_size_disabled = False
    virtual = False
    expired = False

    def __init__(self, name, parent_id, category_id, level, auto_pay_enabled=False, best_offer_enabled=False,
                 item_lot_size_disabled=False, virtual=False, expired=False, leaf=False, b2b_vat_enabled=False):
        self.name = name
        self.parent_id = parent_id
        self.category_id = category_id
        self.level = level
        self.b2b_vat_enabled = b2b_vat_enabled
        self.best_offer_enabled = best_offer_enabled
        self.auto_pay_enabled = auto_pay_enabled
        self.leaf = leaf
        self.item_lot_size_disabled = item_lot_size_disabled
        self.virtual = virtual
        self.expired = expired


    @property
    def can_publish(self):
        return not self.expired

    @classmethod
    def create_from_data(cls, data):
        """
        Create Ebay category from json data
        :param data:
        :return: EbayCategory
        :rtype: EbayCategory
        :type data: dict
        """
        serializer = EbayCategorySerializer(data=data)
        obj = serializer.build()
        return obj


class EbayCategorySerializer(POPOSerializer):
    CategoryName = CharField(source='name')
    CategoryParentID = CharField(source='parent_id')
    CategoryID = CharField(source='category_id')
    CategoryLevel = IntegerField(source='level')
    B2BVATEnabled = BooleanField(source='b2b_vat_enabled', required=False)
    BestOfferEnabled = BooleanField(source='best_offer_enabled', required=False)
    AutoPayEnabled = BooleanField(source='auto_pay_enabled', required=False)
    LeafCategory = BooleanField(source='leaf', required=False)
    LSD = BooleanField(source='item_lot_size_disabled', required=False)
    Virtual = BooleanField(source='virtual', required=False)
    Expired = BooleanField(source='expired', required=False)

    class Meta:
        model = EbayCategory

    def validate(self, data):
        if data['parent_id'] == data['category_id']:
            data['parent_id'] = None
        return data
