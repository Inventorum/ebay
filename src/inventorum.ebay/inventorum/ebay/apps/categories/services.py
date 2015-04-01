# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db.transaction import atomic
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.lib.ebay.categories import EbayCategories
from django.conf import settings

log = logging.getLogger(__name__)


class EbayCategoriesScrapper(object):
    limit_root_nodes = None
    count_root_nodes_by_country = {}

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

    def fetch_all(self):
        """
        Get all categories as a tree from ebay and put them to database
        """
        with atomic():
            imported_ids = []
            for country_code in settings.EBAY_SUPPORTED_SITES.keys():
                self.count_root_nodes_by_country[country_code] = 0
                imported_ids += self._scrap_all_categories(country_code)

            self._convert_children_and_parents()
            self._remove_all_categories_except_these_ids(imported_ids)

    # FETCH ALL helpers

    def _scrap_all_categories(self, country_code):
        categories_ids = []

        api = EbayCategories(self.ebay_token, site_id=settings.EBAY_SUPPORTED_SITES[country_code])
        categories_generator = api.get_categories()

        for category in categories_generator:
            if self._did_we_reach_limit_of_root_nodes(category, country_code):
                break
            category = CategoryModel.create_or_update_from_ebay_category(category, country_code)
            categories_ids.append(category.pk)
        return categories_ids

    def _remove_all_categories_except_these_ids(self, categories_ids):
        CategoryModel.objects.exclude(pk__in=categories_ids).delete()

    def _did_we_reach_limit_of_root_nodes(self, category, country_code):
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
            self.count_root_nodes_by_country[country_code] += 1

        if self.count_root_nodes_by_country[country_code] > self.limit_root_nodes:
            return True

    def _convert_children_and_parents(self):
        all_categories = CategoryModel.objects.all()
        children_categories = all_categories.exclude(external_parent_id=None)
        categories_by_external_id = {c.external_id: c for c in all_categories}
        for category in children_categories:
            category.parent = categories_by_external_id[category.external_parent_id]
            category.save()