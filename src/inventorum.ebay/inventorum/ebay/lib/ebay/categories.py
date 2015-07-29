# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.lib.ebay import EbayTrading, EbayParallel
from inventorum.ebay.lib.ebay.data.categories import EbayCategorySerializer, EbayCategory
from inventorum.ebay.lib.ebay.data.categories.features import EbayFeature
from inventorum.ebay.lib.ebay.data.categories.specifics import EbayCategorySpecifics
from inventorum.ebay.lib.ebay.data.categories.suggestions import GetSuggestedCategoriesResponseType


log = logging.getLogger(__name__)


class EbayCategories(EbayTrading):
    parallel_api = None

    def __init__(self, *args, **kwargs):
        super(EbayCategories, self).__init__(*args, **kwargs)
        self.parallel_api = EbayParallel(*args, **kwargs)

    def get_categories(self, level_limit=None, only_leaf=False):
        """
        Returns generator to iterate over categories
        :return: Generator of categories
        :rtype: generator object
        """

        # I am accessing private field `_declared_fields` cause I didn't see any other way to get this info...
        fields_to_retrieve = EbayCategorySerializer._declared_fields.keys()
        data = dict(
            DetailLevel='ReturnAll',
            ViewAllNodes=not only_leaf,
            OutputSelector=fields_to_retrieve
        )

        if level_limit is not None:
            data['LevelLimit'] = level_limit

        log.debug('Sending request to ebay categories: %s', data)
        response = self.execute('GetCategories', data)

        for category in response['CategoryArray']['Category']:
            # It is so much data I dont want to store in memory here, thats why we return generator
            yield EbayCategory.create_from_data(category)

    def get_features_for_category(self, category_id):
        data = self.execute('GetCategoryFeatures', dict(
            AllFeaturesForCategory=True,
            ViewAllNodes=True,
            CategoryID=category_id,
            LevelLimit=7,
            DetailLevel='ReturnAll',
            FeatureID=['ListingDurations', 'PaymentMethods', 'ItemSpecificsEnabled', 'VariationsEnabled', 'EANEnabled']
            # If you input specific category features with FeatureID fields and set DetailLevel to ReturnAll,
            # eBay returns just the requested feature settings for the specified category, regardless of the
            # site defaults.
        ))
        return EbayFeature.create_from_data(data)

    def get_specifics_for_categories(self, categories_ids):
        """
        Returns specifics per category
        :param categories_ids:
        :return: List of specifics per category
        :rtype: dict[unicode, inventorum.ebay.lib.ebay.data.EbayFeature]
        """
        response = self.execute('GetCategorySpecifics', dict(
            AllFeaturesForCategory=True,
            ViewAllNodes=True,
            CategoryID=categories_ids,
            LevelLimit=7,
            MaxValuesPerName=2147483647,
            MaxNames=30,
            DetailLevel='ReturnAll',
        ))

        category_specifics = response['Recommendations']
        if not isinstance(category_specifics, list):
            category_specifics = [category_specifics]

        specifics = {}
        for i, data in enumerate(category_specifics):
            specific = EbayCategorySpecifics.create_from_data(data)
            log.debug('Parsing %d category specific: %s', i, data)
            specifics[specific.category_id] = specific

        return specifics

    def get_suggested_categories(self, query):
        """
        :rtype: GetSuggestedCategoriesResponseType
        """
        response = self.execute('GetSuggestedCategories', dict(
            Query=query
        ))

        return GetSuggestedCategoriesResponseType.Deserializer(data=response).build()
