# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.conf import settings
from inventorum.ebay.apps.categories.models import CategoryModel
from inventorum.ebay.lib.ebay.categories import EbayCategories
from inventorum.ebay.lib.ebay.data.authorization import EbayToken


log = logging.getLogger(__name__)


class CategorySuggestion(object):

    def __init__(self, category, percent_item_found):
        """
        :type category: CategoryModel
        :type percent_item_found: int
        """
        self.category = category
        self.percent_item_found = percent_item_found


class CategorySuggestionsService(object):

    def __init__(self, account):
        """
        :type account: inventorum.ebay.apps.accounts.models.EbayAccountModel
        """
        self.account = account
        self.token = EbayToken(settings.EBAY_LIVE_TOKEN, expiration_time=settings.EBAY_LIVE_TOKEN_EXPIRATION_DATE,
                               site_id=self.account.site_id)

    def get_suggestions(self, query):
        """
        :type query: unicode
        """
        ebay_api = EbayCategories(token=self.token)
        response = ebay_api.get_suggested_categories(query)

        log.info("Received {} suggestions from ebay for query '{}'".format(response.category_count, query))
        suggestions = []
        for ebay_suggestion in response.suggested_categories:
            suggestion = self._map_ebay_suggestion_to_internal_suggestion(ebay_suggestion)
            if suggestion is not None:
                suggestions.append(suggestion)

        return suggestions

    def _map_ebay_suggestion_to_internal_suggestion(self, ebay_suggestion):
        """
        :type ebay_suggestion: inventorum.ebay.lib.ebay.data.categories.suggestions.SuggestedCategoryType
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
