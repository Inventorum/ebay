# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from ebaysdk.parallel import Parallel
from inventorum.ebay.lib.ebay import Ebay, EbayException, EbayParallel


class EbayCategories(Ebay):
    parallel_api = None

    def __init__(self, *args, **kwargs):
        super(EbayCategories, self).__init__(*args, **kwargs)
        self.parallel_api = EbayParallel(*args, **kwargs)

    def get_categories(self):
        response = self.execute('GetCategories', dict(DetailLevel='ReturnAll'))

        for category in response['CategoryArray']['Category']:
            yield category

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