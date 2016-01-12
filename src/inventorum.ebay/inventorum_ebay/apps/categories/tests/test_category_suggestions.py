# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum_ebay.apps.accounts.tests.factories import EbayAccountFactory
from inventorum_ebay.apps.auth.models import EbayTokenModel

from inventorum_ebay.apps.categories.suggestions import CategorySuggestionsService
from inventorum_ebay.apps.categories.tests.factories import CategoryFactory
from inventorum_ebay.lib.ebay.data.tests.factories import SuggestedCategoryTypeFactory, \
    GetSuggestedCategoriesResponseTypeFactory
from inventorum_ebay.lib.ebay.tests.factories import EbayTokenFactory
from inventorum_ebay.tests import ApiTest
from inventorum_ebay.tests.testcases import EbayAuthenticatedAPITestCase, UnitTestCase
from rest_framework import status


log = logging.getLogger(__name__)


class TestCategorySuggestionsResource(EbayAuthenticatedAPITestCase):

    def setUp(self):
        super(TestCategorySuggestionsResource, self).setUp()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        assert self.account.country == CategoryFactory.country

    def request_suggestions(self, query):
        """
        :rtype: rest_framework.response.Response
        """
        return self.client.get("/categories/suggestions?query={}".format(query))

    def test_mocked_without_suggestions(self):
        self.suggestions_service_mock = \
            self.patch("inventorum_ebay.apps.categories.resources.CategorySuggestionsService.get_suggestions_by_category_root")
        self.suggestions_service_mock.return_value = []

        response = self.request_suggestions(query="I don't yield any results :-(")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, [])

    @ApiTest.use_cassette("category_suggestions.yaml")
    def test_category_suggestions_integration(self):
        # Note: While there are more suggestions in the cassette, we only map few of them here, rest will be ignored

        # Mobile & Communication > Mobile Phones without Contract
        category_mobiles = CategoryFactory.create(name="Mobile & Communication")
        category_mobiles_without_contract = CategoryFactory.create(name="Mobile Phones without Contract",
                                                                   external_id="9355",
                                                                   parent=category_mobiles)

        # Computer, Tablets & Network > Desktop Computers > Apple Desktops & All-in-Ones
        category_computers = CategoryFactory.create(name="Computer, Tablets & Network")

        category_desktop_computers = CategoryFactory.create(name="Desktop Computers",
                                                            parent=category_computers)

        category_apple_desktops = CategoryFactory.create(name="Apple Desktops & All-in-Ones",
                                                         external_id="111418",
                                                         parent=category_desktop_computers)

        # Computer, Tablets & Network > Notebooks & Netbooks > Apple Notebooks
        category_notebooks = CategoryFactory.create(name="Notebooks & Netbooks",
                                                    parent=category_computers)

        category_apple_notebooks = CategoryFactory.create(name="Apple Notebooks",
                                                          external_id="111422",
                                                          parent=category_notebooks)

        # TV, Video & Audio > Internet-TV & Media Streamer
        category_tv = CategoryFactory.create(name="TV, Video & Audio")
        category_internet_tv = CategoryFactory.create(name="Internet-TV & Media Streamer",
                                                      external_id="168058",
                                                      parent=category_tv)

        response = self.request_suggestions(query="Apple")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rooted_suggestions = response.data

        # we created 3 roots => there should be 3 entries
        self.assertEqual(len(response.data), 3)

        root_group_1 = rooted_suggestions[0]

        self.assertDictEqual(root_group_1, {
            "root": {
                "id": category_mobiles.id,
                "name": "Mobile & Communication",
                "country": "DE",
                "parent_id": None,
                "is_leaf": False,
                "variations_enabled": False,
                "ean_enabled": False,
                "ean_required": False
            },
            "suggested_categories": [
                {
                    "percent_item_found": 36,
                    "category": {
                        "id": category_mobiles_without_contract.id,
                        "name": "Mobile Phones without Contract",
                        "country": "DE",
                        "parent_id": category_mobiles.id,
                        "is_leaf": True,
                        "variations_enabled": False,
                        "ean_enabled": False,
                        "ean_required": False,
                        "breadcrumbs": [{"id": category_mobiles.id, "name": "Mobile & Communication"}]
                    },
                }
            ]
        })

        root_group_2 = rooted_suggestions[1]
        self.assertEqual(root_group_2["root"]["name"], "Computer, Tablets & Network")
        self.assertItemsEqual([sg["category"]["id"] for sg in root_group_2["suggested_categories"]],
                              [category_apple_desktops.id, category_apple_notebooks.id])

        root_group_3 = rooted_suggestions[2]
        self.assertEqual(root_group_3["root"]["name"], "TV, Video & Audio")
        self.assertItemsEqual([sg["category"]["id"] for sg in root_group_3["suggested_categories"]],
                              [category_internet_tv.id])


class UnitTestCategorySuggestionsService(UnitTestCase):

    def setUp(self):
        super(UnitTestCategorySuggestionsService, self).setUp()

        # Invariant: default country of categories must equal account category since categories are filtered by country
        self.account = EbayAccountFactory.create(country=CategoryFactory.country)
        self.account.token = EbayTokenModel.create_from_ebay_token(EbayTokenFactory.create())

        self.ebay_api_get_suggested_categories_mock = \
            self.patch("inventorum_ebay.apps.categories.suggestions.EbayCategories.get_suggested_categories")

    def expect_suggestions(self, suggestions):
        """
        :type suggestions: list[inventorum_ebay.lib.ebay.data.categories.suggestions.SuggestedCategoryType]
        """
        self.ebay_api_get_suggested_categories_mock.reset_mock()

        response = GetSuggestedCategoriesResponseTypeFactory(category_count=len(suggestions),
                                                             suggested_categories=suggestions)

        self.ebay_api_get_suggested_categories_mock.return_value = response

    def test_without_suggestions(self):
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
