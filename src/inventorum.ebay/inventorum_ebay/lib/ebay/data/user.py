# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum_ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField, BooleanField, DateTimeField


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
