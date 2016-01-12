# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import itertools

from inventorum_ebay.apps.categories.models import CategoryModel
from inventorum_ebay.lib.ebay.categories import EbayCategories


log = logging.getLogger(__name__)


class CategorySuggestion(object):

    def __init__(self, category, percent_item_found):
        """
        :type category: CategoryModel
        :type percent_item_found: int
        """
        self.category = category
        self.percent_item_found = percent_item_found


class RootedCategorySuggestions(object):

    def __init__(self, root, suggested_categories):
        """
        :type root: CategoryModel
        :type suggested_categories: list[CategorySuggestion]
        """
        self.root = root
        self.suggested_categories = suggested_categories


class CategorySuggestionsService(object):

    def __init__(self, account):
        """
        :type account: inventorum_ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account

    def get_suggestions(self, query):
        """
        :type query: unicode
        :rtype: list[CategorySuggestion]
        """
        ebay_api = EbayCategories(token=self.account.token.ebay_object)
        response = ebay_api.get_suggested_categories(query)

        log.info("Received {} suggestions from ebay for query '{}'".format(response.category_count, query))
        suggestions = []
        for ebay_suggestion in response.suggested_categories:
            suggestion = self._map_ebay_suggestion_to_internal_suggestion(ebay_suggestion)
            if suggestion is not None:
                suggestions.append(suggestion)

        return suggestions

    def get_suggestions_by_category_root(self, query):
        """
        :type query: unicode
        :rtype: list[RootedCategorySuggestions]
        """
        suggestions = self.get_suggestions(query)
        # group suggestions by category root
        return [RootedCategorySuggestions(root, list(suggested_categories))
                for root, suggested_categories in itertools.groupby(suggestions, lambda sc: sc.category.root)]

    def _map_ebay_suggestion_to_internal_suggestion(self, ebay_suggestion):
        """
        :type ebay_suggestion: inventorum_ebay.lib.ebay.data.categories.suggestions.SuggestedCategoryType
        :rtype: CategorySuggestion | None
        """
        try:
            category = CategoryModel.objects.get(country=self.account.country,
                                                 external_id=ebay_suggestion.category.category_id)
        except CategoryModel.DoesNotExist:
            log.info("Could not find matching category with suggested category id {}"
                     .format(ebay_suggestion.category.category_id))
            return None

        return CategorySuggestion(category, percent_item_found=ebay_suggestion.percent_item_found)
