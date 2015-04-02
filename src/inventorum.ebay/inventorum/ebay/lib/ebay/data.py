# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.utils.datetime_safe import datetime
from inventorum.ebay.lib.ebay import Ebay


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

    @classmethod
    def create_from_data(cls, data):
        address = EbayUserAddress()
        address.name = data['Name']
        address.street = data['Street']
        address.street1 = data['Street1']
        address.city = data['CityName']
        address.country = data['Country']
        address.postal_code = data['PostalCode']
        return address


class EbayUser(object):
    email = None
    user_id = None
    id_verified = False
    status = False
    registration_address = EbayUserAddress()
    registration_date = None
    qualifies_for_b2b_vat = None
    store_owner = None

    @classmethod
    def create_from_data(cls, data):
        user = EbayUser()
        user.email = data['Email']
        user.id_verified = data['IDVerified'] == 'true'
        user.status = data['Status']
        user.user_id = data['UserID']
        user.qualifies_for_b2b_vat = data['SellerInfo']['QualifiesForB2BVAT'] == 'true'
        user.store_owner = data['SellerInfo']['StoreOwner'] == 'true'
        user.registration_address = EbayUserAddress.create_from_data(data['RegistrationAddress'])
        user.registration_date = EbayParser.parse_date(data['RegistrationDate'])
        return user


class EbayToken(object):
    """
    Data object to keeps expiration time and value
    """
    expiration_time = None
    value = None

    def __init__(self, value, expiration_time):
        self.expiration_time = expiration_time
        self.value = value


class EbayCategoryMappingFields(object):
    ALL = {
        'CategoryName': ('name', None),
        # Documentation says it is string...
        'CategoryParentID': ('parent_id', None),
        # Documentation says it is string...
        'CategoryID': ('category_id', None),
        'CategoryLevel': ('level', None),
        'Virtual': ('virtual', EbayParser.parse_bool),
        'Expired': ('expired', EbayParser.parse_bool),
        'LeafCategory': ('leaf', EbayParser.parse_bool),
        'B2BVATEnabled': ('b2b_vat_enabled', EbayParser.parse_bool),
        # If true, the category supports business-to-business (B2B) VAT listings. Applicable to the eBay Germany (DE),
        # Austria (AT), and Switzerland CH) sites only. If not present, the category does not support this feature.
        # Will not be returned if false.
        'BestOfferEnabled': ('best_offer_enabled', EbayParser.parse_bool),
        'AutoPayEnabled': ('auto_pay_enabled', EbayParser.parse_bool),
        # If true, indicates that the category supports immediate payment. If not present, the category does not
        # support immediate payment. Will not be returned if false.
        'LSD': ('item_lot_size_disabled', EbayParser.parse_bool),
        # "Lot Size Disabled (LSD)" indicates that Item.LotSize is not permitted when you list
        # in this category. If true, indicates that lot sizes are disabled in the specified category. Will not be
        # returned if false.

    }


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
    # Indicators for categories where you cannot publish anymore
    virtual = False
    expired = False

    @property
    def can_publish(self):
        return not self.virtual and not self.expired

    @classmethod
    def create_from_data(cls, data):
        category = EbayCategory()
        mapping = EbayCategoryMappingFields.ALL
        for key, value in mapping.iteritems():
            field_name, parser = value
            data_value = data.get(key)
            if parser:
                data_value = parser(data_value)
            setattr(category, field_name, data_value)

        if category.parent_id == category.category_id:
            # If it is level=1 category then parent_id == category_id
            category.parent_id = None
        return category

