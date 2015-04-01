# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db.transaction import atomic
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.lib.ebay.categories import EbayCategories


log = logging.getLogger(__name__)


class EbayCategoriesScrapper(object):
    limit_root_nodes = None
    count_root_nodes = 0

    def __init__(self, ebay_token, limit_root_nodes=None):
        """
        Scrapping categories from ebay and saving them to database
        :param ebay_token: Ebay token
        :param limit_root_nodes: Limit of how many root nodes we should scrap
        :return:
        :type ebay_token: inventorum.ebay.lib.ebay.data.EbayToken
        :type limit_root_nodes: int | None
        """
        self.limit_root_nodes = limit_root_nodes
        self.ebay_token = ebay_token
        self.api = EbayCategories(self.ebay_token)

    def fetch_all(self):
        """
        Get all categories as a tree from ebay and put them to database
        """
        with atomic():
            self._scrap_all_categories()
            self._convert_children_and_parents()

    def _scrap_all_categories(self):
        categories_generator = self.api.get_categories()
        for category in categories_generator:
            if self._did_we_reach_limit_of_root_nodes(category):
                break
            CategoryModel.create_from_ebay_category(category)

    def _did_we_reach_limit_of_root_nodes(self, category):
        """
        Check if we reached limit of root nodes
        :param category:
        :return:
        :rtype: bool
        :type category: inventorum.ebay.lib.ebay.data.EbayCategory
        """
        if self.limit_root_nodes is None:
            return False

        if category.parent_id is None:
            self.count_root_nodes += 1

        if self.count_root_nodes > self.limit_root_nodes:
            return True

    def _convert_children_and_parents(self):
        all_categories = CategoryModel.objects.all()
        children_categories = all_categories.exclude(external_parent_id=None)
        categories_by_external_id = {c.external_id: c for c in all_categories}
        for category in children_categories:
            category.parent = categories_by_external_id[category.external_parent_id]
            category.save()