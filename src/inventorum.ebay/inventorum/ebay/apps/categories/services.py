# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.db.transaction import atomic
from django.utils.functional import cached_property
from inventorum.ebay.apps.categories.models import CategoryModel, CategoryFeaturesModel, CategorySpecificModel
from inventorum.ebay.lib.ebay.categories import EbayCategories
from django.conf import settings

log = logging.getLogger(__name__)


class EbayCategoriesScraper(object):
    limit_root_nodes = None
    count_root_nodes_by_country = {}
    count_nodes_by_country = {}

    limit_nodes_level = None

    def __init__(self, ebay_token, limit_root_nodes=None, limit_nodes_level=None, only_leaf=False, limit=None):
        """
        Scraping categories from ebay and saving them to database
        :param ebay_token: Ebay token
        :param limit_root_nodes: Limit of how many root nodes we should scrap
        :param only_leaf: If true, it will get only leaf categories
        :param limit: How many categories to download
        :return:
        :type ebay_token: inventorum.ebay.lib.ebay.data.EbayToken
        :type limit_root_nodes: int | None
        :type only_leaf: bool
        :type limit: int
        """
        self.limit_nodes_level = limit_nodes_level
        self.limit_root_nodes = limit_root_nodes
        self.only_leaf = only_leaf
        self.ebay_token = ebay_token
        self.limit = limit

    def fetch_all(self):
        """
        Get all categories as a tree from ebay and put them to database
        """
        with atomic():
            imported_ids = []
            for country_code in settings.EBAY_SUPPORTED_SITES.keys():
                self.count_root_nodes_by_country[country_code] = 0
                self.count_nodes_by_country[country_code] = 0
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
        categories_generator = api.get_categories(level_limit=self.limit_nodes_level, only_leaf=self.only_leaf)

        for category in categories_generator:
            log.debug('Parsing category: %s [%s], level: %s', category.name, category.category_id, category.level)
            if self._did_we_reach_limit_of_root_nodes(category, country_code):
                log.debug('Skipped because we reached limit of root nodes')
                break
            if self._did_we_reach_limit_of_nodes(country_code):
                log.debug('Skipped because we reached limit of nodes')
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

    def _did_we_reach_limit_of_nodes(self, country_code):
        """
        Check if we reached limit of nodes
        :return:
        :rtype: bool
        """
        if self.limit is None:
            return False

        self.count_nodes_by_country[country_code] += 1

        if self.count_nodes_by_country[country_code] > self.limit:
            return True

    def _convert_children_and_parents(self):
        all_categories = CategoryModel.objects.all()
        children_categories = all_categories.exclude(external_parent_id=None)
        categories_by_external_id = {c.external_id: c for c in all_categories}
        for category in children_categories:
            if not category.external_parent_id in categories_by_external_id:
                continue
            category.parent = categories_by_external_id[category.external_parent_id]
            category.save()


class EbayBatchScraper(object):
    batch_size = 20

    def __init__(self, ebay_token):
        self.ebay_token = ebay_token

    def get_queryset_with_country(self, country_code):
        raise NotImplementedError

    def fetch(self, limited_qs, country_code):
        raise NotImplementedError

    def fetch_all(self):
        for country_code in settings.EBAY_SUPPORTED_SITES.keys():
            self._fetch_in_batches(country_code)

    def _fetch_in_batches(self, country_code):
        queryset = self.get_queryset_with_country(country_code)
        count = queryset.count()
        pages = count/self.batch_size

        for page in range(0, pages):
            start = page * self.batch_size
            end = start + self.batch_size
            limited = queryset[start:end]
            log.debug('Fetching [%s], starting batch: %s/%s', self.__class__.__name__, page+1, pages)
            self.fetch(limited, country_code)


class EbayFeaturesScraper(EbayBatchScraper):
    def get_queryset(self):
        return CategoryModel.objects.filter(ebay_leaf=True)

    def get_queryset_with_country(self, country_code):
        return self.get_queryset().filter(country=country_code)

    def fetch(self, limited_qs, country_code):
        token = self.ebay_token
        token.site_id = settings.EBAY_SUPPORTED_SITES[country_code]

        ebay = EbayCategories(token)
        self._get_features_for_categories(limited_qs, ebay)

    def _get_features_for_categories(self, categories, ebay):
        categories_ids = {category.external_id: category for category in categories}
        features = ebay.get_features_for_categories(categories_ids.keys())

        with atomic():
            for category_id, feature in features.iteritems():
                CategoryFeaturesModel.create_or_update_from_ebay_data_for_category(feature, categories_ids[category_id])



class EbaySpecificsScraper(EbayBatchScraper):
    def get_queryset(self):
        return CategoryModel.objects.filter(ebay_leaf=True, features__item_specifics_enabled=True)

    def get_queryset_with_country(self, country_code):
        return self.get_queryset().filter(country=country_code)

    def fetch(self, limited_qs, country_code):
        token = self.ebay_token
        token.site_id = settings.EBAY_SUPPORTED_SITES[country_code]

        ebay = EbayCategories(token)
        categories_ids = {category.external_id: category for category in limited_qs}
        specifics = ebay.get_specifics_for_categories(categories_ids.keys())
        for category_id, specific in specifics.iteritems():
            CategorySpecificModel.create_or_update_from_ebay_data_for_category(specific,
                                                                               categories_ids[specific.category_id])


