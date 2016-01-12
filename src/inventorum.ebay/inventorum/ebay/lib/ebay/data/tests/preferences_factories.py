# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy
from inventorum.ebay.lib.ebay.data import SellerProfileCodeType
from inventorum.ebay.lib.ebay.data.preferences import CategoryGroupType, SupportedSellerProfileType, \
    SellerProfilePreferencesType, GetUserPreferencesResponseType


log = logging.getLogger(__name__)

NUMBER_CHARS = [str(i) for i in range(10)]


class CategoryGroupTypeFactory(factory.Factory):
    class Meta:
        model = CategoryGroupType

    is_default = fuzzy.FuzzyChoice(choices=[True, False])


class SupportedSellerProfileTypeFactory(factory.Factory):
    class Meta:
        model = SupportedSellerProfileType

    category_group = factory.SubFactory(CategoryGroupTypeFactory)
    profile_id = fuzzy.FuzzyText(length=10, chars=NUMBER_CHARS)
    profile_name = factory.Sequence(lambda n: "Test Seller Profile #%s" % n)
    profile_type = fuzzy.FuzzyChoice(choices=[SellerProfileCodeType.CHOICES])


class SellerProfilePreferencesTypeFactory(factory.Factory):
    class Meta:
        model = SellerProfilePreferencesType

    supported_seller_profiles = factory.LazyAttribute(lambda o: [])


class GetUserPreferencesResponseTypeFactory(factory.Factory):
    class Meta:
        model = GetUserPreferencesResponseType

    seller_profile_preferences = factory.SubFactory(SellerProfilePreferencesTypeFactory)
