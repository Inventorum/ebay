# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db.transaction import atomic
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel
from inventorum.ebay.lib.ebay.categories import EbayCategories
from django.conf import settings

log = logging.getLogger(__name__)


class EbayCategoriesScraper(object):
    limit_root_nodes = None
    count_root_nodes_by_country = {}

    limit_nodes_level = None

    def __init__(self, ebay_token, limit_root_nodes=None, limit_nodes_level=None):
        """
        Scraping categories from ebay and saving them to database
        :param ebay_token: Ebay token
        :param limit_root_nodes: Limit of how many root nodes we should scrap
        :return:
        :type ebay_token: inventorum.ebay.lib.ebay.data.EbayToken
        :type limit_root_nodes: int | None
        """
        self.limit_nodes_level = limit_nodes_level
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
        account_token = self.ebay_token

        # Lets do magic and change site_id for this token (why even ebay allows it, do not ask me...)
        account_token.site_id = settings.EBAY_SUPPORTED_SITES[country_code]

        api = EbayCategories(self.ebay_token)
        categories_generator = api.get_categories(level_limit=self.limit_nodes_level)

        for category in categories_generator:
            log.debug('Parsing category: %s [%s], level: %s', category.name, category.category_id, category.level)
            if self._did_we_reach_limit_of_root_nodes(category, country_code):
                log.debug('Skipped because we reached limit of root nodes')
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


class EbayFeaturesScraper(object):
    batch_size = 20

    def __init__(self, ebay_token):
        self.ebay_token = ebay_token

    @cached_property
    def count(self):
        return CategoryModel.objects.count()

    @property
    def pages(self):
        return self.count/self.batch_size

    def fetch_all(self):
        for country_code in settings.EBAY_SUPPORTED_SITES.keys():
            self._fetch_in_batches(country_code)

    def _fetch_in_batches(self, country_code):
        queryset = CategoryModel.objects.filter(country=country_code)

        for page in range(0, self.pages):
            start = page * self.batch_size
            end = start + self.batch_size
            limited_categories = queryset[start:end]
            log.debug('Fetching categories features, starting batch: %s/%s', page+1, self.pages)
            account_token = self.ebay_token

            # Lets do magic and change site_id for this token (why even ebay allows it, do not ask me...)
            account_token.site_id = settings.EBAY_SUPPORTED_SITES[country_code]

            ebay = EbayCategories(account_token)
            self._get_features_for_categories(limited_categories, ebay)

    def _get_features_for_categories(self, categories, ebay):
        categories_ids = {category.external_id: category for category in categories}
        features = ebay.get_features_for_categories(categories_ids.keys())

        with atomic():
            for category_id, feature in features.iteritems():
                CategoryFeaturesModel.create_or_update_from_ebay_data_for_category(feature, categories_ids[category_id])


