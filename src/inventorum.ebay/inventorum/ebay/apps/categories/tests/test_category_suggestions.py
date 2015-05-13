# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.categories.suggestions import CategorySuggestionsService
from inventorum.ebay.apps.categories.tests.factories import CategoryFactory
from inventorum.ebay.lib.ebay.data.categories.suggestions import SuggestedCategoryType
from inventorum.ebay.lib.ebay.data.tests.factories import SuggestedCategoryTypeFactory, \
    GetSuggestedCategoriesResponseTypeFactory
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase


log = logging.getLogger(__name__)


class IntegrationTestCategorySuggestions(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(IntegrationTestCategorySuggestions, self).setUp()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        assert self.account.country == CategoryFactory.country

    def test_category_suggestions(self):
        pass


class UnitTestCategorySuggestionsService(UnitTestCase):

    def setUp(self):
        super(UnitTestCategorySuggestionsService, self).setUp()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        self.account = EbayAccountFactory.create(country=CategoryFactory.country)

        self.ebay_api_get_suggested_categories_mock = \
            self.patch("inventorum.ebay.apps.categories.suggestions.EbayCategories.get_suggested_categories")

    def expect_suggestions(self, suggestions):
        """
        :type suggestions: list[inventorum.ebay.lib.ebay.data.categories.suggestions.SuggestedCategoryType]
        """
        self.ebay_api_get_suggested_categories_mock.reset_mock()

        response = GetSuggestedCategoriesResponseTypeFactory(category_count=len(suggestions),
                                                             suggested_categories=suggestions)

        self.ebay_api_get_suggested_categories_mock.return_value = response

    def test_no_suggestions(self):
        self.expect_suggestions([])

        subject = CategorySuggestionsService(account=self.account)
        suggestions = subject.get_suggestions("query without results")
        self.assertEqual(suggestions, [])

    def test_with_suggestions(self):
        category_1 = CategoryFactory.create(external_id="1")
        category_2 = CategoryFactory.create(external_id="2")
        category_3 = CategoryFactory.create(external_id="3")

        self.expect_suggestions([
            SuggestedCategoryTypeFactory.create(category__category_id="1", percent_item_found=80),
            SuggestedCategoryTypeFactory.create(category__category_id="2", percent_item_found=15),
            SuggestedCategoryTypeFactory.create(category__category_id="3", percent_item_found=5),
        ])

        subject = CategorySuggestionsService(account=self.account)
        suggestions = subject.get_suggestions("query with results, whoop whoop")

        self.assertEqual(len(suggestions), 3)
        self.assertItemsEqual([s.category for s in suggestions], [category_1, category_2, category_3])

    def test_suggestion_for_unknown_category(self):
        self.expect_suggestions([
            SuggestedCategoryTypeFactory.create(category__category_id="DoesNotExist", percent_item_found=80),
        ])

        subject = CategorySuggestionsService(account=self.account)
        suggestions = subject.get_suggestions("query with suggestion for unknown category")

        self.assertEqual(len(suggestions), 0)
