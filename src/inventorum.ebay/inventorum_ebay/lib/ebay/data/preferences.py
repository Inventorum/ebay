# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from inventorum_ebay.lib.ebay.data import EbayArrayField, EbayBooleanField
from inventorum_ebay.lib.rest.serializers import POPOSerializer
from rest_framework.fields import CharField


class CategoryGroupType(object):
    """
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/CategoryGroupType.html
    """

    def __init__(self, is_default):
        """
        :type is_default: bool
        """
        self.is_default = is_default

    # Deserialization #################

    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        IsDefault = EbayBooleanField(source='is_default')

CategoryGroupType.Deserializer.Meta.model = CategoryGroupType


class SupportedSellerProfileType(object):
    """
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/SupportedSellerProfileType.html
    """

    def __init__(self, category_group, profile_id, profile_name, profile_type):
        """
        :type category_group: CategoryGroupType
        :type profile_id: unicode
        :type profile_name: unicode
        :type profile_type: unicode
        """
        self.category_group = category_group
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.profile_type = profile_type

    # Deserialization #################

    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        CategoryGroup = CategoryGroupType.Deserializer(source='category_group')
        ProfileID = CharField(source='profile_id')
        ProfileName = CharField(source='profile_name')
        ProfileType = CharField(source='profile_type')

SupportedSellerProfileType.Deserializer.Meta.model = SupportedSellerProfileType


class SellerProfilePreferencesType(object):
    """
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/SellerProfilePreferencesType.html
    """

    def __init__(self, supported_seller_profiles):
        """
        :type supported_seller_profiles: list[SupportedSellerProfileType]
        """
        self.supported_seller_profiles = supported_seller_profiles

    # Deserialization #################

    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        SupportedSellerProfiles = EbayArrayField(source='supported_seller_profiles',
                                                 item_key='SupportedSellerProfile',
                                                 item_deserializer=SupportedSellerProfileType.Deserializer)

SellerProfilePreferencesType.Deserializer.Meta.model = SellerProfilePreferencesType


class GetUserPreferencesResponseType(object):
    """
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/GetUserPreferencesResponseType.html
    """

    def __init__(self, seller_profile_preferences):
        """
        :type seller_profile_preferences: SellerProfilePreferencesType
        """
        self.seller_profile_preferences = seller_profile_preferences

    # Deserialization #################

    class Deserializer(POPOSerializer):
        class Meta:
            model = None

        SellerProfilePreferences = SellerProfilePreferencesType.Deserializer(source='seller_profile_preferences')

GetUserPreferencesResponseType.Deserializer.Meta.model = GetUserPreferencesResponseType
