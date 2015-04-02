# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from ebaysdk.parallel import Parallel
import logging
from inventorum.ebay.lib.ebay import Ebay, EbayException, EbayParallel
from inventorum.ebay.lib.ebay.data import EbayCategoryMappingFields, EbayCategory


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

        fields_to_retrieve = EbayCategoryMappingFields.ALL.keys()
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

    def get_attributes_for_categories(self, categories_ids):

        for category_id in categories_ids:
            self.parallel_api.execute('', dict(
                AllFeaturesForCategory=True,
                ViewAllNodes=True,
                CategoryID=category_id,
                LevelLimit=7,
                DetailLevel='ReturnAll'
            ))

        return self.parallel_api.wait_and_validate()