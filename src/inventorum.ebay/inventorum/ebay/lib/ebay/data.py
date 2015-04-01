# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import Ebay


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
        user.registration_date = Ebay.parse_date(data['RegistrationDate'])
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

