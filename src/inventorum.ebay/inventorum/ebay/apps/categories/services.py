# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db.transaction import atomic
from inventorum.ebay.lib.ebay.categories import EbayCategories


class EbayCategoriesScrapper(object):

    def __init__(self, ebay_token):
        """
        Scrapping categories from ebay and saving them to database
        :param ebay_token:
        :return:
        :type ebay_token: inventorum.ebay.lib.ebay.data.EbayToken
        """

        self.ebay_token = ebay_token
        self.api = EbayCategories(self.ebay_token)

    def fetch_all(self):
        """
        Get all categories as a tree from ebay and put them to database
        """
        with atomic():
            self._scrap_all_categories()
            self._convert_children_and_parents()
            self._validate_all()

    def _scrap_all_categories(self):
        pass

    def _convert_children_and_parents(self):
        pass

    def _validate_all(self):
        pass