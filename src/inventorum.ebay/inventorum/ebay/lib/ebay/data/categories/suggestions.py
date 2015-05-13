# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.lib.ebay.data import EbayArrayField
from inventorum.ebay.lib.ebay.data.categories import EbayCategorySerializer

from inventorum.ebay.lib.rest.serializers import POPOSerializer
from rest_framework import serializers


log = logging.getLogger(__name__)


class SuggestedCategoryType(object):
    """
    http://developer.ebay.com/devzone/xml/docs/reference/ebay/types/SuggestedCategoryType.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        Category = EbayCategorySerializer(source="category")
        PercentItemFound = serializers.IntegerField(source="percent_item_found")

    # / Deserialization ###############

    def __init__(self, category, percent_item_found):
        """
        :type category: inventorum.ebay.lib.ebay.data.categories.EbayCategory
        :type percent_item_found: int
        """
        self.category = category
        self.percent_item_found = percent_item_found

SuggestedCategoryType.Deserializer.Meta.model = SuggestedCategoryType


class GetSuggestedCategoriesResponseType(object):
    """
    http://developer.ebay.com/Devzone/xml/docs/Reference/ebay/GetSuggestedCategories.html
    """

    # Deserialization #################

    class Deserializer(POPOSerializer):

        class Meta:
            model = None

        CategoryCount = serializers.IntegerField(source="category_count")
        SuggestedCategoryArray = EbayArrayField(source="suggested_categories",
                                                item_key="SuggestedCategory",
                                                item_deserializer=SuggestedCategoryType.Deserializer)

    # / Deserialization ###############

    def __init__(self, category_count, suggested_categories):
        """
        :type category_count: int
        :type suggested_categories: list[SuggestedCategoryType]
        """
        self.category_count = category_count
        self.suggested_categories = suggested_categories

GetSuggestedCategoriesResponseType.Deserializer.Meta.model = GetSuggestedCategoriesResponseType
