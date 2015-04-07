# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from ebaysdk.parallel import Parallel
import logging
from inventorum.ebay.lib.ebay import Ebay, EbayParallel
from inventorum.ebay.lib.ebay.data.categories import EbayCategorySerializer, EbayCategory
from inventorum.ebay.lib.ebay.data.features import EbayFeature


log = logging.getLogger(__name__)


class EbayCategories(Ebay):
    parallel_api = None

    def __init__(self, *args, **kwargs):
        super(EbayCategories, self).__init__(*args, **kwargs)
        self.parallel_api = EbayParallel(*args, **kwargs)

    def get_categories(self, level_limit=None):
        """
        Returns generator to iterate over categories
        :return: Generator of categories
        :rtype: generator object
        """

        # I am accessing private field `_declared_fields` cause I didn't see any other way to get this info...
        fields_to_retrieve = EbayCategorySerializer._declared_fields.keys()
        data = dict(
            DetailLevel='ReturnAll',
            OutputSelector=fields_to_retrieve
        )

        if level_limit is not None:
            data['LevelLimit'] = level_limit

        log.debug('Sending request to ebay categories: %s', data)
        response = self.execute('GetCategories', data)

        for category in response['CategoryArray']['Category']:
            # It is so much data I dont want to store in memory here, thats why we return generator
            yield EbayCategory.create_from_data(category)

    def get_features_for_categories(self, categories_ids):
        """
        Returns features per category
        :param categories_ids:
        :return: List of feature per category
        :rtype: [inventorum.ebay.lib.ebay.data.EbayFeature]
        """
        for category_id in categories_ids:
            self.parallel_api.execute('GetCategoryFeatures', dict(
                AllFeaturesForCategory=True,
                ViewAllNodes=True,
                CategoryID=category_id,
                LevelLimit=7,
                DetailLevel='ReturnAll'
            ))

        category_features = self.parallel_api.wait_and_validate()
        features = {}
        for i, response in enumerate(category_features):
            data = response.response.dict()
            feature = EbayFeature.create_from_data(data)
            features[feature.details.category_id] = feature

        return features